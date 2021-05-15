var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

observableSocket.onmessage = function(msg) {
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
  
    if(djangoData['type'] == 13) { //Conectando
      document.querySelector('#connection-status').innerText = "Esperando conexão serial...";
    }
    else if(djangoData['type'] == 14) { //Conectado
      document.querySelector('#connection-status').innerText = "Conectado";
    }
    else {
      if(djangoData['type'] == 249) {
        document.querySelector('#actions-logs').innerText = "Acendeu LED";
      }
      else if(djangoData['type'] == 250) {
        document.querySelector('#actions-logs').innerText = "Apagou LED";
      }
      //id = djangoData['id'];
      //type = djangoData['type'];
      //seq = djangoData['seq'];
      //ack = djangoData['ACK'];
      //sdata = djangoData['SDATA'];
      //lat = djangoData['lat'];
      //lng = djangoData['lng'];
      //high = djangoData['high'];
  
      //document.querySelector('#actions-logs').innerText = `{'id': '${id}', 'type': ${type}, 'seq': ${seq}, 'ack': ${ack}, 'sdata': ${sdata}, 'lat': ${lat}, 'lng': ${lng}, 'high': ${high}}`;
    }
  } catch(e) {
    document.querySelector('#actions-logs').innerText = msg.data;
  }
}

observableSocket.onclose = function(e) {
  console.error('Connection socket closed unexpectedly');
};

sendCommandSocket.onclose = function(e) {
  console.error('Receive socket closed unexpectedly');
};


// Onclick functions

document.querySelector('#turn-on').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 249, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};

document.querySelector('#turn-off').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 250, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};

document.querySelector('#forward-1').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 251, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};

document.querySelector('#forward-2').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 252, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};

document.querySelector('#initiate-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 253, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};

document.querySelector('#interrupt-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 254, 'seq': 0, 'ACK': 0, 'SDATA': 0, 'lat': -9, 'lng': 10, 'high': 11}
    ));
  }
};