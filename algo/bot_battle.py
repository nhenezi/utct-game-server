#! /usr/bin/python
import next_move_monte_carlo as bot1
import nextmoveminmax as bot2
import utct

def play_one_match():
  main_board = [utct.EMPTY_VALUE for _ in xrange(9)]
  boards = [[utct.EMPTY_VALUE for _ in xrange(9)] for _ in xrange(9)]
  next_board = False

  while utct.winner(main_board) is False:
    data = {
      'main_board': main_board,
      'boards': boards,
      'next_move': utct.PLAYER_X,
      'next_board': next_board
    }
    bot1_move = bot1.calculate_next_move(data)
    if bot1_move is None:
      break
    boards[bot1_move['main_board']][bot1_move['boards']] = utct.PLAYER_X
    next_board = bot1_move['main_board']
    if utct.winner(boards[next_board]) is not False:
      main_board[bot1_move['main_board']] = utct.winner(boards[bot1_move['main_board']])
      next_board = False

    data = {
      'main_board': main_board,
      'boards': boards,
      'next_move': utct.PLAYER_Y,
      'next_board': next_board
    }
    bot2_move = bot2.calculate_next_move(data)
    if bot2_move is None:
      break

    boards[bot2_move['main_board']][bot2_move['boards']] = utct.PLAYER_Y
    next_board = bot2_move['main_board']
    if utct.winner(boards[next_board]) is not False:
      main_board[bot2_move['main_board']] = utct.winner(boards[bot2_move['main_board']])
      next_board = False

  return utct.winner(main_board)
  
NUMBER_OF_MATCHES = 10

if __name__ == "__main__":
  results = [0, 0, 0]
  for i in xrange(NUMBER_OF_MATCHES):
    print '.'
    results[play_one_match()] += 1

  print NUMBER_OF_MATCHES, 'matches played'
  print 'Bot1 has won', results[1], 'times'
  print 'Bot2 has won', results[2], 'times'
  print  results[0], 'ties'











