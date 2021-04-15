var socket = new WebSocket('ws://localhost:8000/ws/connection/');

socket.onmessage = function(e) {
  var djangoData = JSON.parse(e.data);
  console.log(djangoData);

  id = djangoData['id']
  type = djangoData['type']
  count = djangoData['count']
  lat = djangoData['lat']
  lng = djangoData['lng']
  high = djangoData['high']

  document.querySelector('#app').innerText = `{'id': '${id}', 'type': ${type}, 'count': ${count}, 'lat': ${lat}, 'lng': ${lng}}, 'high': ${high}`;
}

socket.onclose = function(e) {
  console.error('Chat socket closed unexpectedly');
};

document.querySelector('#turn-on').onclick = function(e) {
  socket.send(JSON.stringify(
    {'id': 1, 'type': 2, 'count': 3, 'lat': -9, 'lng': 10}
  ));
};

document.querySelector('#turn-off').onclick = function(e) {
  socket.send(JSON.stringify(
    {'id': 1, 'type': 1, 'count': 3, 'lat': -9, 'lng': 10}
  ));
};