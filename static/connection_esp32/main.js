var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

observableSocket.onmessage = function(e) {
  var djangoData = JSON.parse(e.data);
  console.log(djangoData);

  if(djangoData['id'] == "3") {
    document.querySelector('#json-received').innerText = "Conectando...";
  }
  else {
    id = djangoData['id'];
    type = djangoData['type'];
    seq = djangoData['seq'];
    payload = djangoData['payload']
    lat = payload['lat'];
    lng = payload['lng'];
    high = payload['high'];

    document.querySelector('#json-received').innerText = `{'id': '${id}', 'type': ${type}, 'seq': ${seq}, 'payload':{'lat': ${lat}, 'lng': ${lng}, 'high': ${high}}}`;
  }
}

observableSocket.onclose = function(e) {
  console.error('Connection socket closed unexpectedly');
};

sendCommandSocket.onclose = function(e) {
  console.error('Receive socket closed unexpectedly');
};

document.querySelector('#turn-on').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 2, 'seq': 3, 'payload':{'lat': -9, 'lng': 10, 'high': 11}}
  ));
};

document.querySelector('#turn-off').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 1, 'seq': 3, 'payload':{'lat': -9, 'lng': 10, 'high': 11}}
  ));
};