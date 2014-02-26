#! /usr/bin/python

import json
import redis
import utct

win = 100
dubina = 4


def initialize():

  data ={}
  data['main_board'] = [utct.EMPTY_VALUE]*9
  boards = []
  for i in range(9):
    boards += [[utct.EMPTY_VALUE]*9]
  data['boards'] =  boards
  data['next_move'] = 1
  data['next_board'] = False
  data['socket_id'] = 'ztF4rnYQIWWzWKWICJJw'
  return data
  

def send_move(main_board_move, boards_move, oldData):
  # convertion to specified format
  best_move = 9 * main_board_move + boards_move
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': best_move
  }
  rc.publish('nextMove', json.dumps(data))
  
  
def calculate_next_move(data):
  value, next_move_main_board, next_move_boards = negamax(data, -1000, 1000, dubina, 1)
  print 'vrijednost negamax', value
  print next_move_main_board, next_move_boards
  # send next move
  return {
    'main_board': next_move_main_board,
    'boards': next_move_boards
  }


def make_move(main_board_move, boards_move, data):
  data['boards'][main_board_move][boards_move] = data['next_move']
  data['main_board'][main_board_move] = utct.EMPTY_VALUE if utct.winner(data['boards'][main_board_move]) is False else utct.winner(data['boards'][main_board_move])
  data['next_board'] = boards_move
  data['next_move']= utct.PLAYER_X if data['next_move'] == utct.PLAYER_Y else utct.PLAYER_Y
  return data
  
  
def undo_move(main_board_move, boards_move, data):
  data['boards'][main_board_move][boards_move] = utct.EMPTY_VALUE
  data['main_board'][main_board_move] = utct.EMPTY_VALUE if utct.winner(data['boards'][main_board_move]) is False else utct.winner(data['boards'][main_board_move])
  data['next_board'] = main_board_move
  data['next_move'] = utct.PLAYER_X if data['next_move'] == utct.PLAYER_Y else utct.PLAYER_Y
  return data
  
  
def evaluate(data):
  if utct.winner(data['main_board']) == data['next_move'] :
    return win
    
  elif utct.winner(data['main_board']) != data['next_move'] :
    return -win
    
  else:
    ret_val = 0
    for i in range(9):
      if data['main_board'][i] != utct.TIE and data['main_board'][i] != EMPTY_VALUE:
        if data['main_board'][i] != data['next_move']:
          ret_val -= 10
          print 'retval -10'
        elif data['main_board'][i] == data['next_move']:
          ret_val += 10
          print 'retval -10 '
  return ret_val
  
  
def negamax(data, alpha, beta, depth, color):
  on_move = data['next_move']
  next_main_board_move = None
  next_boards_move = None
  main_board_move = None
  boards_move = None
  
  if depth == 0: #or node is a terminal node
    return color * evaluate(data), main_board_move, boards_move
        
  bestValue = -1000
    
# legalni potezi u dozvoljenom okviru
  valid_board = data['next_board']
  legal_moves = {}
  if valid_board : 
    board = data['boards'][valid_board]
    legal_moves[valid_board] = utct.get_valid_moves(board)
    
# dozvoljeni potezi na cijelom boards, kada je dozvoljeno igrati bilo gdje
  else:
    for i in xrange(9):
      board = data['boards'][i]
      #print board
      legal_moves[i] = utct.get_valid_moves(board)
  #print legal_moves    
  for i in set(legal_moves) :
    next_main_board_move = i
    for j in xrange(9):
      if legal_moves[i][j]:
        next_boards_move =  j
        ## make move
        data = make_move(next_main_board_move, next_boards_move, data ) 
        score = -negamax(data, -beta, -alpha, depth-1, -color)[0]
        data = undo_move(next_main_board_move, next_boards_move, data )
        
        if score >= beta:
          return beta, main_board_move, boards_move
        if score > alpha:
          alpha = score
          if color == 1 and depth == dubina:
            main_board_move = next_main_board_move
            boards_move = next_boards_move
            print 'depth', depth, 'main_move', main_board_move, 'boards_move', boards_move
  return alpha, main_board_move, boards_move


def write(data):
  print 'on move', data['next_move']
  print 'main_board', data['main_board'], '\n'
  print 'boards'
  for i in range(9):
    print i, data['boards'][i]
    
  
 
if __name__ == "__main__":
  rc = redis.Redis();
  ps = rc.pubsub()
  ps.subscribe(['calculateNextMove']);
  #generiram plocu jedan potez do pobjede
  potezi1 = [(3,3), (3,4), (3,5), (0,0), (0,1), (0,2), (6,6)]
  potezi2 = [(1,1), (1,3), (1,8), (5,1), (5,2), (5,3), (7,1)]
  potez = []
  for i in range(len(potezi1)):
    potez += [potezi1[i], potezi2[i]]
  
  for item in ps.listen():
    if item['type'] == 'message' and item['channel'] == 'calculateNextMove':
      data = json.loads(item['data'])
      for i in range(len(potez)):
        data = make_move(potez[i][0], potez[i][1], data)
        send_move(potez[i][0], potez[i][1], data)
      next_move = calculate_next_move(data)
      write(data)

      send_move(next_move['main_board'], next_move['boards'], data)
      if evaluate(data) == win:
        print 'win'
        break
      if evaluate(data) == -win:
        print '-win'
        break


