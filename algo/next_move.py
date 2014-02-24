#! /usr/bin/python

import json
import redis

def send_move(main_board_move, boards_move, oldData):
  # converion to specified format
  best_move = 9 * main_board_move + boards_move
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': best_move
  }
  rc.publish('nextMove', json.dumps(data))
  
def calculate_next_move(data):
  #...
  #...
  #...
  #...
  # calculation is done
  next_move_main_board = 5
  next_move_boards = 3
  # send next move
  send_move(next_move_main_board, next_move_boards, data)


if __name__ == "__main__":
  rc = redis.Redis();
  ps = rc.pubsub()
  ps.subscribe(['calculateNextMove']);

  for item in ps.listen():
    if item['type'] == 'message' and item['channel'] == 'calculateNextMove':
      calculate_next_move(json.loads(item['data']))


