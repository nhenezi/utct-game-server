#! /usr/bin/python

import copy
import random

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

def get_valid_moves(board):
  return map(lambda x: x == EMPTY_VALUE, board)

def get_possible_moves(board):
  valid_moves = get_valid_moves(board)
  possible_moves = []
  for i, valid in enumerate(valid_moves):
    if valid:
      possible_moves.append(i)
  return possible_moves

def get_rand_move(board):
  '''Finds random move on board, returns False if no move is valid'''
  possible_moves = get_possible_moves(board)
  if possible_moves:
    return random.choice(possible_moves)
  return False


def get_winning_move(board, player):
  '''
  Retrieves a winning move for player on board,
  None of such move doesn't exists
  '''
  possible_moves = get_possible_moves(board)
  if not possible_moves:
    return None
  for move in possible_moves:
    tmp_board = copy.deepcopy(board)
    tmp_board[move] = player
    if winner(tmp_board) != False and winner(tmp_board) != TIE:
      return move

  return None


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
    if field == EMPTY_VALUE:
      tie = False
      break
  if tie is True:
    return TIE
  else:
    return False
