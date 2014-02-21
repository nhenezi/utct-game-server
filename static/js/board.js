var canvas = this.__canvas = new fabric.StaticCanvas('main');

options = {
  colors: {
    x : 'red',
    o : 'blue',
    marker: 'rgba(0, 255, 0, 0.4)',
    grid : {
      'small': 'green',
      'main': 'black',
    },
    line: 'black',
    win: {
      x: 'rgba(255, 0, 0, 0.2',
      o: 'rgba(0, 0, 255, 0.2',
      stroke: 'black',
    }
  },
  player: 'o'
};

var p = {
  size: 600,
  lineSize: 4,
  padding: {
    vertical: 20,
    horizontal: 20,
  },
  cols: 3,
};

var getMousePos = function(e) {
  var canvas = document.getElementById('main');
  var rect = canvas.getBoundingClientRect();
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  };
}
/**
 * Draws sizeX * sizeY tic-tac-toe grid starting at (startX, startY)
 */
var drawGrid = function(startX, startY, sizeX, sizeY, color) {
  var interval = Math.floor(sizeX/p.cols);
  var gridPixels = []; // coordinates of each field

  // we draw lines
  for (var i = interval; i < sizeX - interval/2; i += interval) {
    canvas.add(new fabric.Rect({ // vertical line
      top: startY + p.padding.vertical,
      left: startX + i,
      width: p.lineSize,
      height: sizeY - 2 * p.padding.vertical,
      fill: color,
    }), new fabric.Rect({ // and horizontal
      top: startY + i,
      left: startX + p.padding.horizontal,
      width: sizeX - 2 * p.padding.vertical,
      height: p.lineSize,
      fill: color,
    }));
  }

  // we populate gridPixes with field coordinates
  // e.g. gridPixels[8] holds coordinates of 9th field in grid
  // Numbering is schemed below
  //
  //  0 | 1 | 2
  // ---+--+----
  //  3 | 4 | 5
  // ---+---+---
  //  6 | 7 | 9
  //

  // - interval/2 is needed due to rounding errors in interval
  for (var x = startX; x < startX + sizeX - interval/2; x += interval) {
    for (var y = startY; y < startY + sizeY - interval/2; y += interval) {
      // we are using "inverted" y coordinates, e.g. (0,0) is in top left corner
      gridPixels.push({
        x: y,
        y: x,
        endX: y + interval,
        endY: x + interval
      });
    }
  }

  return gridPixels;
};

/**
 * Given coordMatrix and x,y coordinates, return grid number.
 * Numbering is schemed below:
 *
 *  0 | 1 | 2
 * ---+--+----
 *  3 | 4 | 5
 * ---+---+---
 *  6 | 7 | 9
 *
 */
var findGrid = function(x, y, coordMatrix, o) {
  for (var i = 0; i < coordMatrix.length; i++) {
    if (o && o.debug) {
    }
    if (coordMatrix[i].x <= x && x <= coordMatrix[i].endX &&
        coordMatrix[i].y <= y && y <= coordMatrix[i].endY) {
      return i;
    }
  }
  return false;
};

/**
 * Finds center of coordinate object
 */
var findCenter = function(coordObj) {
  return {
    x: (coordObj.x + coordObj.endX) / 2,
    y: (coordObj.y + coordObj.endY) / 2,
  };
}

/**
 * Marks a spot with nice magenta circle
 */
var markSpot = function(top, left) {
  var radius = 2;
  canvas.add(new fabric.Circle({
    top: top - radius,
    left: left - radius,
    radius: radius,
    fill: 'white',
    stroke: 'magenta',
    strokeWidth: 5,
  }));
}
/**
 * Draws circle or x inside boardMatrix[i][j]
 */
var draw = function(i, j, type, boardMatrix) {
  var center = findCenter(boardMatrix[i][j]);
  if (type == 'o') {
    var radius = 20;
    canvas.add(new fabric.Circle({
      top: center.y - radius,
      left: center.x - radius,
      radius: radius,
      fill: 'white',
      stroke: options.colors.o,
      strokeWidth: 5,
    }));
  } else {
    var lineSize = 50;
    canvas.add(new fabric.Line([boardMatrix[i][j].x, boardMatrix[i][j].y, center.x, center.y], {
      stroke: options.colors.x,
      strokeWidth: 5,
    }), new fabric.Line([boardMatrix[i][j].x + 35, boardMatrix[i][j].y, center.x + 35, center.y], {
      stroke: options.colors.x,
      strokeWidth: 5,
      angle: 90,
    }));
  }
}

var initData = function() {
  mainBoard = [];
  boards = [];
  for (var i = 0; i < 9; i++) {
    mainBoard.push(null);
    var row = [];
    for (var j = 0; j < 9; j++) {
      row.push(null);
    }
    boards.push(row);
  }

  return {
    mainBoard: mainBoard,
    boards: boards,
  }
}


var winner = function(board) {
  if (board[0] != null) {
    if (board[0] === board[1] &&  board[1] === board[2]) {
      return {winner: board[0], c: [0, 1, 2]};
    } else if (board[0] === board[3] && board[3] === board[6]) {
      return {winner: board[0], c: [0, 3, 6]};
    } else if (board[0] === board[4] && board[4] === board[8]) {
      return {winner:  board[0], c: [0, 4, 8]};
    }
  }

  if (board[1] != null) {
    if (board[1] == board[4] && board[4] == board[7]) {
      return {winner: board[1], c: [1, 4, 7] };
    }
  }

  if (board[2] != null) {
    if (board[2] === board[4] && board[4] === board[6]) {
      return {winner: board[2], c: [2, 4, 6]};
    } else if (board[2] === board[5] && board[5] === board[8]) {
      return {winner: board[2], c: [2, 5, 8]};
    }
  }

  if (board[3] != null) {
    if (board[3] === board[4] && board[4] === board[5]) {
      return {winner: board[3], c: [3, 4, 5]};
    }
  }

  if (board[6] != null) {
    if (board[6] === board[7] && board[7] === board[8]) {
      return {winner: board[6], c: [6, 7, 8]};
    }
  }

  return false;
};

/**
 * Draws a colored line connecting centers of startGrid and endGrid
 */
var drawLine = function(startGrid, endGrid, coordMatrix, color) {
  console.log(startGrid, endGrid, coordMatrix);
  var coords = {
    start: findCenter(coordMatrix[startGrid]),
    end: findCenter(coordMatrix[endGrid])
  };

  if (coords.end.x - coords.start.x == 0) {
    // we have to draw horizontal line
    height = coords.end.y - coords.start.y;
    console.log(height);
    canvas.add(new fabric.Rect({
      top: coords.start.y - 15,
      left: coords.start.x,
      width: p.lineSize + 2,
      height: height + 30,
      fill: color,
    }));
  } else if (coords.end.y - coords.start.y == 0) {
    // we have to draw vertical line
    height = coords.end.x - coords.start.x;
    canvas.add(new fabric.Rect({
      top: coords.start.y,
      left: coords.start.x - 15,
      width: height + 30,
      height: p.lineSize + 2,
      fill: color,
    }));
  } else if(coords.start.x < coords.end.x) {
    var distance = Math.sqrt(Math.pow(coords.start.x - coords.end.x, 2) +
                             Math.pow(coords.start.y - coords.end.y, 2));
    canvas.add(new fabric.Rect({
      top: coords.start.y - 10,
      left: coords.start.x - 10,
      angle: 45,
      width: distance + 30,
      height: p.lineSize + 2,
      fill: color,
    }));
  } else if(coords.start.x > coords.end.x) {
    var distance = Math.sqrt(Math.pow(coords.start.x - coords.end.x, 2) +
                             Math.pow(coords.start.y - coords.end.y, 2));
    canvas.add(new fabric.Rect({
      top: coords.end.y + 10,
      left: coords.end.x - 10,
      angle: 315,
      width: distance + 30,
      height: p.lineSize + 2,
      fill: color,
    }));
  }
}

var markedBoard = null;
var markBoard = function(board, coordMatrix) {
  var coords = coordMatrix[board];
  clearMark();
  markedBoard = new fabric.Rect({
      top: coords.y,
      left: coords.x,
      width: 200,
      height: 200,
      fill: options.colors.marker
    });
  canvas.add(markedBoard);
}

var clearMark = function() {
  if (markedBoard) {
    canvas.remove(markedBoard);
  }
}

var coords = {
  mainBoard: drawGrid(0, 0, p.size, p.size, options.colors.grid.main),
  boards: []
};

var interval = p.size/p.cols;
for (var i = interval; i <= p.size; i += interval) {
  var gridSize = 200;
  for (var j = interval; j <= p.size; j += interval) {
    coords.boards.push(drawGrid(i - interval, j - interval, gridSize, gridSize,
                                options.colors.grid.small));
  }
}
var processMove = function(bigGrid, smallGrid, player) {
  data.boards[bigGrid][smallGrid] = player;
  draw(bigGrid, smallGrid, player, coords.boards);
  var w;
  nextBoard = null;
  // if board is not decided we calculate winner
  if (data.mainBoard[bigGrid] == null && (w = winner(data.boards[bigGrid]))) {
    data.mainBoard[bigGrid] = player;
    drawLine(w.c[0], w.c[2], coords.boards[bigGrid], options.colors.win.stroke);
    console.log(w, 'at', bigGrid);
    if (w = winner(data.mainBoard)) {
      console.log('winner is' + player);
    }
  } else if (data.mainBoard[smallGrid] == null) {
    nextBoard = smallGrid;
  }
  if (last === options.player) {
    socket.emit('match:move', {
      main_board: data.mainBoard,
      boards: data.boards,
      next_moved: player
    });
  }
  last = player == 'o' ? 'x' : 'o';
  if (nextBoard != null) {
    markBoard(smallGrid, coords.mainBoard);
  } else {
    clearMark();
  }
}

var socket = io.connect('http://localhost:7076');
socket.on('nextMove', function (n) {
  console.log('nextMove', n);
  bigGrid = Math.floor(n/9);
  smallGrid = n % 9;
  processMove(bigGrid, smallGrid, last);
});

var last = 'o'
var data = initData();
var nextBoard = null;
//drawLine(0, 4, coords.MainBoard);
document.getElementById('main').onclick = function(e) {
  // get initial positions
  var pos = getMousePos(e);
  var bigGrid = findGrid(pos.x, pos.y,   coords.mainBoard);
  var smallGrid = findGrid(pos.x, pos.y, coords.boards[bigGrid], {debug: true});
  console.log(bigGrid, smallGrid);
  // if big and small boards are not populated and move is valid
  if (data.boards[bigGrid][smallGrid] == null && data.mainBoard[bigGrid] == null
      && (nextBoard == null || nextBoard == bigGrid)) {
    processMove(bigGrid, smallGrid, last);
  }
}
