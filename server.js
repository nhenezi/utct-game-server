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
    req.data.socket_id = req.socket.id;
    data = JSON.stringify(req.data);
    console.log('match:move');
    console.log(data);
    client_pub.publish("calculateNextMove", data);
  },
});

client.subscribe('nextMove');
client.on('message', function(channel, data) {
  data = JSON.parse(data);
  console.log(channel, data);
  if  (channel === 'nextMove') {
    var socket = app.io.sockets.sockets[data.socket_id];
    socket.emit('nextMove', data.next_move);
  }
});
app.listen(7076);
