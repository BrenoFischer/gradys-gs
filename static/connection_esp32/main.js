var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

observableSocket.onmessage = function(e) {
  var djangoData = JSON.parse(e.data);
  console.log(djangoData);

  id = djangoData['id']
  type = djangoData['type']
  count = djangoData['count']
  lat = djangoData['lat']
  lng = djangoData['lng']
  high = djangoData['high']

  document.querySelector('#json-received').innerText = `{'id': '${id}', 'type': ${type}, 'count': ${count}, 'lat': ${lat}, 'lng': ${lng}, 'high': ${high}}`;
}

observableSocket.onclose = function(e) {
  console.error('Connection socket closed unexpectedly');
};

sendCommandSocket.onclose = function(e) {
  console.error('Receive socket closed unexpectedly');
};

document.querySelector('#turn-on').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 2, 'count': 3, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};

document.querySelector('#turn-off').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 1, 'count': 3, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};