var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');

function notifyUiWhenJsonSent(json_sent) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode("JSON enviado: " + json_sent));
  p.className += "json-sent";

  element.appendChild(p);
}

function notifyUiWhenJsonReceived(json_received, msg) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode(msg + json_received));
  p.className += "json-received";

  element.appendChild(p);
}

observableSocket.onmessage = function(msg) {
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
    json_type = djangoData['type'];
    msgUi = "JSON recebido: ";
    msgDefault = "JSON unknown: ";
    msgDrone = "Drone info JSON: ";
    switch(json_type) {
      case 13:  //Esperando conexão
        document.querySelector('#disconnected').innerText = "Esperando conexão serial...";
        document.querySelector('#connected').innerText = "";
        break;
      case 14:  //Conectado
        document.querySelector('#disconnected').innerText = "";
        document.querySelector('#connected').innerText = "Conectado";
        break;
      case 21:  //cmd-led-on-ACK
        //document.querySelector('#actions-logs').innerText = "Acendeu LED";
        //notifyUiWhenJsonReceived("Acendeu LED");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 23:  //cmd-led-off-ACK
        //document.querySelector('#actions-logs').innerText = "Apagou LED";
        //notifyUiWhenJsonReceived("Apagou LED");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 25: //forward 1 ACK
        //document.querySelector('#actions-logs').innerText = "Forward 1 recebido";
        //notifyUiWhenJsonReceived("Forward 1 recebido");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 27: //forward 2 ACK
        //document.querySelector('#actions-logs').innerText = "Forward 2 recebido";
        //notifyUiWhenJsonReceived("Forward 2 recebido");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 29: //Voo iniciado ACK
        //document.querySelector('#actions-logs').innerText = "Voo iniciado";
        //notifyUiWhenJsonReceived("Voo iniciado");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 31: //Voo abortado ACK
        //document.querySelector('#actions-logs').innerText = "Voo abortado";
        //notifyUiWhenJsonReceived("Voo abortado");
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 35: //Informação drone recebido
        notifyUiWhenJsonReceived(msg.data, msgDrone);
        let id = djangoData['id'];
        let lat = parseFloat(djangoData['lat']);
        let log = parseFloat(djangoData['log']);
        gmap.newMarker(id, lat, log);
        break;
      default:
        //document.querySelector('#actions-logs').innerText = "JSON unknown: " + msg.data;
        notifyUiWhenJsonReceived(msg.data, msgDefault);
        break;
    }
  } catch(e) {
    //document.querySelector('#actions-logs').innerText = msg.data;
    notifyUiWhenJsonReceived(msg.data);
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
    json_to_send = JSON.stringify(
      {id: 1, type: 20, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#turn-off').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 22, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#forward-1').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 24, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#forward-2').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 26, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#initiate-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 28, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#interrupt-flight').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 30, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    sendCommandSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};