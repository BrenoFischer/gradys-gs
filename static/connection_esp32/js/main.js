var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');
var receivePostSocket = new WebSocket('ws://localhost:8000/ws/update-drone/');
var updateSocket = new WebSocket('ws://localhost:8000/ws/update-periodically/');


function notifyUiWhenJsonSent(jsonSent) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode("Command sent: " + jsonSent));
  p.className += "json-sent";

  element.prepend(p);
}

function notifyUiWhenJsonReceived(jsonReceived, msg) {
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode(msg + jsonReceived));
  p.className += "json-received";

  element.prepend(p);
}

function checkJsonType(msg) {
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
    json_type = djangoData['type'];

    msgUi = "ACK: ";
    msgDefault = "JSON unknown: ";
    msgDrone = "UAV info: ";

    switch(json_type) {
      case 13:  //Esperando conexão
        //document.querySelector('#disconnected').innerText = "IP: OK | UART: OFF";
        //document.querySelector('#connected').innerText = "";
        document.querySelector('#connected').innerText = "IP: OK";
        document.querySelector('#disconnected').innerText = "UART: OFF";
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
      case 102: //Informação drone recebido
        notifyUiWhenJsonReceived(msg.data, msgDrone);
        const id = djangoData['id'];
        const lat = parseFloat(djangoData['lat']);
        const log = parseFloat(djangoData['log']);
        const status = djangoData['status'];
        const deviceType = djangoData['device'];
        gmap.newMarker(id, lat, log, status, deviceType);
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

updateSocket.onmessage = function(msg) {
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

updateSocket.onclose = function(e) {
  console.error('Update socket closed unexpectedly');
}


// Onclick functions
//-------------------
document.querySelector('#turn-on').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 20, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#turn-off').onclick = function(e) {
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    json_to_send = JSON.stringify(
      {id: 1, type: 22, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
    );
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#forward-1').onclick = function(e) {
  json_to_send = JSON.stringify(
    {id: 1, type: 24, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
  );

  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#forward-2').onclick = function(e) {
  json_to_send = JSON.stringify(
    {id: 1, type: 26, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
  );

  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#initiate-flight').onclick = function(e) {
  json_to_send = JSON.stringify(
    {id: 1, type: 28, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
  );

  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};

document.querySelector('#interrupt-flight').onclick = function(e) {
  json_to_send = JSON.stringify(
    {id: 1, type: 30, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
  );

  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(json_to_send);
    //notifyUiWhenJsonSent(json_to_send);
  }
  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(json_to_send);
    notifyUiWhenJsonSent(json_to_send);
  }
};
