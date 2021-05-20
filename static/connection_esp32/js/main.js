var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

observableSocket.onmessage = function(msg) {
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
    json_type = djangoData['type'];
    switch(json_type) {
      case 13:  //Esperando conexão
        document.querySelector('#connection-status').innerText = "Esperando conexão serial...";
        break;
      case 14:  //Conectado
        document.querySelector('#connection-status').innerText = "Conectado";
        break;
      case 21:  //cmd-led-on-ACK
        document.querySelector('#actions-logs').innerText = "Acendeu LED";
        break;
      case 23:  //cmd-led-off-ACK
        document.querySelector('#actions-logs').innerText = "Apagou LED";
        break;
      case 25: //forward 1 ACK
        document.querySelector('#actions-logs').innerText = "Forward 1 recebido";
        break;
      case 27: //forward 2 ACK
        document.querySelector('#actions-logs').innerText = "Forward 2 recebido";
        break;
      case 29: //Voo iniciado ACK
        document.querySelector('#actions-logs').innerText = "Voo iniciado";
        break;
      case 31: //Voo abortado ACK
        document.querySelector('#actions-logs').innerText = "Voo abortado";
        break;
      default:
        document.querySelector('#actions-logs').innerText = "JSON unknown: " + msg.data;
        break;
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
      {'id': 1, 'type': 20, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};

document.querySelector('#turn-off').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 22, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};

document.querySelector('#forward-1').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 24, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};

document.querySelector('#forward-2').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 26, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};

document.querySelector('#initiate-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 28, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};

document.querySelector('#interrupt-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    sendCommandSocket.send(JSON.stringify(
      {'id': 1, 'type': 30, 'seq': 0, 'lat': -9, 'log': 10, 'high': 11, 'DATA': "0"}
    ));
  }
};