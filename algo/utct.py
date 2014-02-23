#! /usr/bin/python

PLAYER_X = 1
PLAYER_Y = 2
TIE = 0
EMPTY_VALUE = -1


def is_allowed_move(main_board_move, boards_move, main_board, boards):
  '''Checks if move is valid'''
  # if main board is populated
  if main_board[main_board_move] != EMPTY_VALUE:
    return False
  # if that field is taken
  if boards[main_board_move][boards_move] != EMPTY_VALUE:
    return False
  return True

def winner(board):
  '''
  Returns winner of `board`
  winner can be either PLAYER_X, PLAYER_Y, TIE or False if no one won on board
  board is list of 9 elements, representing one tic-tac-toe board
  '''
  if board[0] != EMPTY_VALUE:
    if board[0] == board[1] and  board[1] == board[2]:
      return board[0]
    elif board[0] == board[3] and board[3] == board[6]:
      return board[0]
    elif board[0] == board[4] and board[4] == board[8]:
      return  board[0]
    
  if board[1] != EMPTY_VALUE:
    if board[1] == board[4] and board[4] == board[7]:
      return board[1]
    
  if board[2] != EMPTY_VALUE:
    if board[2] == board[4] and board[4] == board[6]:
      return board[2]
    elif board[2] == board[5] and board[5] == board[8]:
      return board[2]
    
  if board[3] != EMPTY_VALUE:
    if board[3] == board[4] and board[4] == board[5]:
      return board[3]
    
  if board[6] != EMPTY_VALUE:
    if board[6] == board[7] and board[7] == board[8]:
      return board[6]
    
  tie = True
  for field in board:
    if field == EMPYT_VALUE:
      tie = false
      break
  if tie is True:
    return TIE
  else:
    return False
