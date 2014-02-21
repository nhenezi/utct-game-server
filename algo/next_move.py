#! /usr/bin/python

import json
import redis


def send_move(n, oldData):
  data = {
    'socket_id': oldData['socket_id'],
    'next_move': n
  }
  rc.publish('nextMove', json.dumps(data))
  
def calculate_next_move(data):
  #...
  #...
  #...
  #...
  # calculation is done
  next_move = 5
  # send next move
  send_move(next_move, data)


if __name__ == "__main__":
  rc = redis.Redis();
  ps = rc.pubsub()
  ps.subscribe(['calculateNextMove']);

  for item in ps.listen():
    if item['type'] == 'message' and item['channel'] == 'calculateNextMove':
      calculate_next_move(json.loads(item['data']))


