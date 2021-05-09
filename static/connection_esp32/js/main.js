var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

observableSocket.onmessage = function(msg) {
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
  
    if(djangoData['id'] == "3") {
      document.querySelector('#json-received').innerText = "Conectando...";
    }
    else {
      id = djangoData['id'];
      type = djangoData['type'];
      seq = djangoData['seq'];
      ack = djangoData['ACK'];
      sdata = djangoData['SDATA'];
      lat = djangoData['lat'];
      lng = djangoData['lng'];
      high = djangoData['high'];
  
      document.querySelector('#json-received').innerText = `{'id': '${id}', 'type': ${type}, 'seq': ${seq}, 'ack': ${ack}, 'sdata': ${sdata}, 'lat': ${lat}, 'lng': ${lng}, 'high': ${high}}`;
    }
  } catch(e) {
    document.querySelector('#json-received').innerText = msg.data;
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
    {'id': 1, 'type': 249, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};

document.querySelector('#turn-off').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 250, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};

document.querySelector('#forward-1').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 251, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};

document.querySelector('#forward-2').onclick = function(e) {
  sendCommandSocket.send(JSON.stringify(
    {'id': 1, 'type': 252, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
  ));
};