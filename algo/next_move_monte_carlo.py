#! /usr/bin/python

import copy
import utct
import random
import json
import redis
from pprint import pprint

def send_move(n, oldData):
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': n
  }
  rc.publish('nextMove', json.dumps(data))

# precision
NUMBER_OF_SIMULATIONS = 100

def calculate_next_move(data):
  player = data['next_move']
  winning_moves = [[0 for _ in xrange(9)] for _ in xrange(9)]
  losing_moves = [[0 for _ in xrange(9)] for _ in xrange(9)]
  game_over = False
  print data['next_board']
  for i in xrange(NUMBER_OF_SIMULATIONS):
    if done is True:
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
      if next_board is not False:
        main_board_move = next_board
      else:
        main_board_move = utct.get_rand_move(main_board)
      boards_move = utct.get_rand_move(boards[main_board_move])
      boards[main_board_move][boards_move] = on_move
      next_board = boards_move
      if next_main_board_move == None:
        next_main_board_move = main_board_move
        next_boards_move = boards_move
#        print next_main_board_move, next_boards_move
#      print on_move, main_board_move, boards_move
      if utct.winner(boards[main_board_move]) is not False:
        main_board[main_board_move] = utct.winner(boards[main_board_move])
      # next player move
      on_move = utct.PLAYER_X if on_move == utct.PLAYER_Y else utct.PLAYER_Y

    winning_player = utct.winner(main_board)
    print winning_player, next_main_board_move, next_boards_move
    if winning_player == player:
      winning_moves[next_main_board_move][next_boards_move] += 1;
    else:
      losing_moves[next_main_board_move][next_boards_move] += 1;
#    pprint(winning_moves)
#    pprint(losing_moves)

  if game_over is true:
    return
  winning_percentages = [[0 for _ in xrange(9)] for _ in xrange(9)]
  for main_board in xrange(9):
    for board in xrange(9):
      if winning_moves[main_board][board] > 0:
        winning_percentages[main_board][board] = float(winning_moves[main_board][board]) \
          / float(winning_moves[main_board][board] + losing_moves[main_board][board])
      else:
        winning_percentages[main_board][board] = 0

  def max_index_in_list(a):
    return max(enumerate(a),key=lambda x: x[1])[0]
  best_moves = []
  best_move_values = []
  for boards in winning_percentages:
    best_move = max_index_in_list(boards)
    best_moves.append(best_move)
    best_move_values.append(boards[best_move])

  best_big_move = max_index_in_list(best_move_values)
  best_move = 9 * best_big_move + best_moves[best_big_move]

  send_move(best_move, data)

if __name__ == "__main__":
  rc = redis.Redis();
  ps = rc.pubsub()
  ps.subscribe(['calculateNextMove']);

  for item in ps.listen():
    if item['type'] == 'message' and item['channel'] == 'calculateNextMove':
      calculate_next_move(json.loads(item['data']))

