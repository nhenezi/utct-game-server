from collections import namedtuple
import random
import sys
import curses
import time
import resource
import redis
import json

position = namedtuple("position", "x o")

class ploca:
    def __init__(self):
        self.polje = [position]*10
        self.okvir = 0

win = 10
move = 0
brojac = 0
dubina = 6
okvir = 0

pobjeda = [ int('111000000',2) , int('000111000', 2), int('000000111',2), 
		int('100100100', 2) , int('010010010',2) , int('001001001',2), 
		int('100010001', 2) , int('001010100', 2)]
		
		
def loadgame(gamename):
	file = open(gamename, 'r')
	tablica = []
	igra = ploca()
	for line in file:
		tablica += [line]
	#ucitaj male ploce
	j = 1
	for i in range(len(tablica)):
		xplayer = ''
		oplayer = ''
		if tablica[i] != '\n':
			xplayer = tablica[i].split('%')[0]
			oplayer = tablica[i].split('%')[1]
			oplayer = oplayer[:-1]
			igra.polje[j] = position(xplayer, oplayer)
			j += 1	
		
	#ucitaj veliku plocu
	xplayer = ''
	oplayer = ''
	for i in range(9):
		if evaluate(igra.polje[i+1]) == win:
			xplayer = xplayer + '1'
			oplayer = oplayer + '0'
		elif evaluate(igra.polje[i+1]) == -win:
			xplayer = xplayer + '0'
			oplayer = oplayer + '1'
		else:
			xplayer = xplayer + '0'
			oplayer = oplayer + '0'
	igra.polje[0] = position(xplayer, oplayer)
	return igra
		
		
def evaluate(pozicija):
	x = int(pozicija.x, 2)
	o = int(pozicija.o, 2)

	for i in range(len(pobjeda)):
		if x & pobjeda[i] == pobjeda[i]:
			return win
			
		if o & pobjeda[i] == pobjeda[i]:
			return -win
					
	return 0
	
	
def uevaluate(igra):
	return evaluate(igra.polje[0])


def legalmoves(pozicija):
	legal = int(pozicija.x, 2) | int(pozicija.o, 2)
	y = int('111111111', 2)
	legal = bin(legal^y)
	legal = legal[2:]
	while len(legal) < 9:
		legal = '0' + legal
	choiceset = []
	for i in range(len(legal)):
		if legal[i] == '1':
			choiceset += [i+1]
	return choiceset
	
	
def ulegalmoves(igra):
	choiceset = []
	if igra.okvir == 0:
		for i in range(9):
			legal = legalmoves(igra.polje[i+1])
			choiceset += [legal]
	else:
		choiceset = legalmoves(igra.polje[igra.okvir])
	return choiceset
	
	
def xchild(pozicija, move):
	x = pozicija.x[:move-1] + '1' + pozicija.x[move:]
	return position(x, pozicija.o)


def ochild(pozicija, move):
	o = pozicija.o[:move-1] + '1' + pozicija.o[move:]
	return position(pozicija.x, o)


def uxchild(igra, move):
	igra.polje[igra.okvir] = xchild(igra.polje[igra.okvir], move)
	if evaluate(igra.polje[igra.okvir]) == win:
		igra.polje[0] = xchild(igra.polje[0], igra.okvir)
		
	igra.okvir = move
	if evaluate(igra.polje[igra.okvir]) == win or evaluate(igra.polje[igra.okvir]) == -win:
		igra.okvir = 0
	return igra
	
	
def uochild(igra, move):
	igra.polje[igra.okvir] = ochild(igra.polje[igra.okvir], move)
	if evaluate(igra.polje[igra.okvir]) == -win:
		igra.polje[0] = ochild(igra.polje[0], igra.okvir)
		
	igra.okvir = move
	if evaluate(igra.polje[igra.okvir]) == win or evaluate(igra.polje[igra.okvir]) == -win:
		igra.okvir = 0
	return igra


def undoxchild(pozicija, move):
	x = pozicija.x[:move-1] + '0' + pozicija.x[move:]
	vrati = position(x, pozicija.o)
	del x
	return vrati
	
	
def undoochild(pozicija, move):
	o = pozicija.o[:move-1] + '0' + pozicija.o[move:]
	vrati = position(pozicija.x, o)
	del o
	return vrati
	

def uundoxchild(igra, move):
	igra.polje[igra.okvir] = undoxchild(igra.polje[igra.okvir], move)
	if evaluate(igra.polje[igra.okvir]) == 0 and igra.okvir != 0:
		igra.polje[0] = undoxchild(igra.polje[0], igra.okvir)
		igra.polje[0] = undoochild(igra.polje[0], igra.okvir)	
	return igra
	
	
def uundoochild(igra, move):
	igra.polje[igra.okvir] = undoochild(igra.polje[igra.okvir], move)
	if evaluate(igra.polje[igra.okvir]) == 0 and igra.okvir != 0:
		igra.polje[0] = undoxchild(igra.polje[0], igra.okvir)
		igra.polje[0] = undoochild(igra.polje[0], igra.okvir)
	return igra


def ualphabetamax(igra, alpha, beta, depth):
	global move
	global brojac
	global dubina
	global okvir
	stariokvir = 0
	#gc.enable()
	ulegal = ulegalmoves(igra)
	if depth == 0 or uevaluate(igra)!= 0 or len(ulegal) == 0:
		brojac += 1
		return uevaluate(igra)
	if isinstance( ulegal[0], ( int, long ) ):
		for i in range(len(ulegal)):
			stariokvir = igra.okvir
			#print 'max if', ulegal[i]
			igra = uxchild(igra, ulegal[i])
			score = ualphabetamin(igra, alpha, beta, depth-1)
			
			igra.okvir = stariokvir
			igra = uundoxchild(igra, ulegal[i])
		
			if score >= beta:
				return beta
			if score > alpha:
				alpha = score
				if depth == dubina:
					move = ulegal[i]
				#print 'abmax okvir',igra.okvir, 'move', move, 'depth', depth, 'ocjena', score
	else:
		for j in range(len(ulegal)):
			for i in range(len(ulegal[j])):
				igra.okvir = j+1
				stariokvir = igra.okvir
				#print 'max else', ulegal[j][i]
				igra = uxchild(igra, ulegal[j][i])
				score = ualphabetamin(igra, alpha, beta, depth-1)
				
				igra.okvir = stariokvir
				igra = uundoxchild(igra, ulegal[j][i])
		
				if score >= beta:
					return beta
				if score > alpha:
					alpha = score
					if depth == dubina:
						move = ulegal[j][i]
						okvir = j+1
					#print 'abmax okvir',igra.okvir, 'move', move, 'depth', depth, 'ocjena', score			
	return alpha
	 
	
def ualphabetamin(igra, alpha, beta, depth):
	global move
	global brojac
	global okvir
	#gc.enable()
	ulegal = ulegalmoves(igra)
	if depth == 0 or uevaluate(igra)!= 0 or len(ulegal) == 0:
		brojac += 1
		return uevaluate(igra)
		
	if isinstance( ulegal[0], ( int, long ) ):
		for i in range(len(ulegal)):
			stariokvir = igra.okvir
			igra = uochild(igra, ulegal[i])
			#print 'min if', ulegal[i]
			score = ualphabetamax(igra, alpha, beta, depth-1)
			
			igra.okvir = stariokvir
			igra = uundoochild(igra, ulegal[i])
		
			if score <= alpha:
				return alpha
			if score < beta:
				beta = score
	else:
		for j in range(len(ulegal)):
			for i in range(len(ulegal[j])):
				
				igra.okvir = j+1
				stariokvir = igra.okvir
				igra = uochild(igra, ulegal[j][i])
				#print 'min else', j+1, ulegal[j][i]
				score = ualphabetamax(igra, alpha, beta, depth-1)
				igra.okvir = stariokvir
				igra = uundoochild(igra, ulegal[j][i])
				if score <= alpha:
					return alpha
				if score < beta:
					beta = score
	return beta


def uxturn(igra):
	
	global move
	global okvir
	print '\nigra x'
	print ualphabetamax(igra, -100, 100, dubina), 'uabmax'
	#print 'neposredno nakon uabmax okvir',igra.okvir,'move', move
	if okvir != 0:
		igra.okvir = okvir
	#sendmove(preracunajzaserver(igra.okvir, move), oldData)
	print '\nxturn', igra.okvir, move 
	print "leafs:", brojac
	
	igra = uxchild(igra, move)
	
	ispisi(igra)
	return igra


def uoturn(igra):
	print '\nigra o'
	if igra.okvir == 0:
		while 1:
			polje = int(raw_input('koje polje igras:'))
			if polje < 10 and polje > 0:
				igra.okvir = polje
				break

	while 1:
		ulegal = ulegalmoves(igra)
		print 'dozvoljeni potezi u okviru', igra.okvir, ':', ulegal
		move = int(raw_input('koji potez igras:'))
		
		if ulegal.count(move) != 0:
			break
		print 'zauzeto. koncentriraj se!'
		
	igra = uochild(igra, move)
	ispisi(igra)
	return igra

	
def ispisi(igra):
	print '\nokvir', igra.okvir
	for i in range(len(igra.polje)):
		print igra.polje[i], legalmoves(igra.polje[i])

def preracunajzaserver(okvir, move):
	vrati = (okvir-1)*9 + move-1
	return vrati

############NIKOLINA FJe ZA SLANJE POTEZA	#############

def sendmove(n, oldData):
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': n
  }
  rc.publish('nextMove', json.dumps(data))
		
      
#############	MAIN	##################
igra = ploca()
igra = loadgame('uigra1')
#igra.okvir = 4
prvi = int(raw_input('ako zelis igrati prvi upisi 1:'))
ispisi(igra)
if prvi == 1:
	igra = uoturn(igra)
#print preracunajzaserver(4, 9)
while 1:
	if uevaluate(igra) == -win:
		print 'pobjeda za o!'
		break
	start = time.time()
	igra = uxturn(igra)
	end = time.time()
	print 'vrijeme potrage', end - start
	print 'potrosena memorija' , resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
	if uevaluate(igra) == win:
		print 'pobjeda za x!'
		break
		
	igra = uoturn(igra)

