var config = {
  hostname: "http://localhost",
  port: 7076
}

redis = require('redis')
client = redis.createClient();

var io = require('socket.io-client');
var socket = io.connect(config.hostname, {port: config.port});

console.log('ss');
socket.on('connect', function(data) {
  console.log('connection established');
  console.log(data);
  socket.emit('match:nextMove', {board: [[1,2,3], [4,5,6], [7,8,9]], nextBoard: 2, player: 1});
});

