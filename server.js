app = require('express.io')()
redis = require('redis')
client = redis.createClient();
client_pub = redis.createClient();
app.http().io()

app.io.route('match', {
  /**
   * Creates a new match
   */
  move: function(req) {
    var data;
    console.log('match:move');
    req.data.socket_id = req.socket.id;
    data = JSON.stringify(req.data);
    client_pub.publish("calculateNextMove", data);
  },
});

client.subscribe('nextMove');
client.on('message', function(channel, data) {
  data = JSON.parse(data);
  console.log(channel, data);
  if  (channel === 'nextMove') {
    console.log('pass');
    var socket = app.io.sockets.sockets[data.socket_id];
    console.log(data.socket_id); 
    console.log('DDDDD', data, data.socket_id, data['socket_id']);
    console.log(socket);
    socket.emit('nextMove', data.next_move);
  }
});
app.listen(7076);
