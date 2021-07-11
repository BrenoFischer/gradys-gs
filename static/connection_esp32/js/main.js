var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');
var receivePostSocket = new WebSocket('ws://localhost:8000/ws/post/');


function notifyUiWhenJsonSent(jsonSent) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode("JSON enviado: " + jsonSent));
  p.className += "json-sent";

  element.appendChild(p);
}

function notifyUiWhenJsonReceived(jsonReceived, msg) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode(msg + jsonReceived));
  p.className += "json-received";

  element.appendChild(p);
}

function checkJsonType(msg) {
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
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 23:  //cmd-led-off-ACK
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 25: //forward 1 ACK
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 27: //forward 2 ACK
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 29: //Voo iniciado ACK
        notifyUiWhenJsonReceived(msg.data, msgUi);
        break;
      case 31: //Voo abortado ACK
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
        notifyUiWhenJsonReceived(msg.data, msgDefault);
        break;
    }
  } catch(e) {
    notifyUiWhenJsonReceived(msg.data);
  }
}

receivePostSocket.onmessage = function(msg) {
  checkJsonType(msg);
}

observableSocket.onmessage = function(msg) {
  checkJsonType(msg);
}


//On close functions
//-------------------
observableSocket.onclose = function(e) {
  console.error('Connection socket closed unexpectedly');
};

sendCommandSocket.onclose = function(e) {
  console.error('Send command socket closed unexpectedly');
};

receivePostSocket.onclose = function(e) {
  console.error('Receive POST socket closed unexpectedly');
}


// Onclick functions
//-------------------
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
