#! /usr/bin/python

import copy
import utct
import random
import json
import redis
from pprint import pprint

def send_move(main_board_move, boards_move, oldData):
  # converion to specified format
  best_move = 9 * main_board_move + boards_move
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': best_move
  }
  rc.publish('nextMove', json.dumps(data))

# precision
NUMBER_OF_SIMULATIONS = 1000

def calculate_next_move(data):
  pprint(data);
  '''
  We are using monte carlo method for calculating best next move.
  Number of simulations is defined by NUMBER_OF_SIMULATIONS constant.

  Each starting move has a winning percentage defined, winning percentage is
  calculated as:
      (number_of_winning_moves * 2 + number_of_tying_moves) /
      (number_of_winning_moves * 2 + number_of_typing_moves + number_of_losing_moves)
  Initialy, each move as a winning percentage of 0.5.
  '''
  player = data['next_move']
  winning_moves = [[0 for _ in xrange(9)] for _ in xrange(9)]
  tying_moves = [[1 for _ in xrange(9)] for _ in xrange(9)]
  losing_moves = [[1 for _ in xrange(9)] for _ in xrange(9)]
  game_over = False

  for i in xrange(NUMBER_OF_SIMULATIONS):
    if game_over is True:
      break
    next_board = data['next_board']
    main_board = copy.deepcopy(data['main_board'])
    boards = copy.deepcopy(data['boards'])
    on_move = data['next_move']
    # we are caculating success for next move
    next_main_board_move = None
    next_boards_move = None
    if utct.winner(main_board) is not False:
      game_over = True
      break
    # until we have a winner
    while utct.winner(main_board) is False:
      # generate a random move if there is no restriction on next board
      if next_board is not False:
        main_board_move = next_board
      else:
        main_board_move = utct.get_rand_move(main_board)

      winning_move = utct.get_winning_move(boards[main_board_move], on_move)
      if winning_move == None:
        boards_move = utct.get_rand_move(boards[main_board_move])
      else:
        boards_move = winning_move
      boards[main_board_move][boards_move] = on_move
      next_board = boards_move

      # if this value is not set, this is our next move
      if next_main_board_move == None:
        next_main_board_move = main_board_move
        next_boards_move = boards_move

      # if we have a winner or a tie mark it on main board
      if utct.winner(boards[main_board_move]) is not False:
        main_board[main_board_move] = utct.winner(boards[main_board_move])
      # next player move
      on_move = utct.PLAYER_X if on_move == utct.PLAYER_Y else utct.PLAYER_Y

    winning_player = utct.winner(main_board)
    if winning_player == player:
      winning_moves[next_main_board_move][next_boards_move] += 1;
    elif winning_player == utct.TIE:
      tying_moves[next_main_board_move][next_boards_move] += 1;
    else:
      losing_moves[next_main_board_move][next_boards_move] += 1;

  if game_over is True:
    return
  winning_percentages = calculate_winning_percentages(winning_moves, tying_moves,
                                                     losing_moves)

  best_move = find_best_move(winning_percentages)
  print "Best move: ", best_move
  return best_move

def calculate_winning_percentages(winning_moves, tying_moves, losing_moves):
  winning_percentages = [[0 for _ in xrange(9)] for _ in xrange(9)]
  # win percentage = (2 * number of winning moves + number of tying moves)/
  # (2 * number of winning moves + number of tying moves + number of losing moves)
  for main_board in xrange(9):
    for board in xrange(9):
      winning_percentages[main_board][board] = float(2 * winning_moves[main_board][board] \
                                                     + tying_moves[main_board][board]) \
        / float(2 * winning_moves[main_board][board] + tying_moves[main_board][board] + \
                losing_moves[main_board][board])
  return winning_percentages

def find_best_move(winning_percentages):
  # findes index of a maximum element in a list
  def max_index_in_list(a):
    return max(enumerate(a),key=lambda x: x[1])[0]

  best_moves = []
  best_move_values = []
  # we find the best and their values move in each grid
  for boards in winning_percentages:
    best_move = max_index_in_list(boards)
    best_moves.append(best_move)
    best_move_values.append(boards[best_move])

  best_big_move = max_index_in_list(best_move_values)
  return {
    'main_board': best_big_move,
    'boards': best_moves[best_big_move]
    }


if __name__ == "__main__":
  rc = redis.Redis();
  ps = rc.pubsub()
  ps.subscribe(['calculateNextMove']);

  for item in ps.listen():
    if item['type'] == 'message' and item['channel'] == 'calculateNextMove':
      data = json.loads(item['data'])
      best_move = calculate_next_move(data)
      send_move(best_move['main_board'], best_move['boards'], data)
