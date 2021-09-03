var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');
var receivePostSocket = new WebSocket('ws://localhost:8000/ws/update-info/');
var updateSocket = new WebSocket('ws://localhost:8000/ws/update-periodically/');

var activeDevicesId = []

document.querySelector('#ip-connected').innerText = "IP: OK";

function sendCommand(type) {
  jsonToSend = {id: 1, type: type, seq: 0, lat: -9, log: 10, high: 11, DATA: "0"}
  jsonToSend["receiver"] = getDeviceReceiver();

  jsonToSend = JSON.stringify(jsonToSend);
  console.log(jsonToSend);

  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(jsonToSend);
    notifyUiWhenJsonSent(jsonToSend);
  }
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(jsonToSend);
    //notifyUiWhenJsonSent(jsonToSend);
  }
}



function getMatchingIndex(id) {
  //Retorna a posição do id encontrado, no vetor de devices ou -1 caso não encontre
  var matchingId = -1;

  [...document.getElementById('select-device').children].forEach((option, index) => {
    if(option.value == id) matchingId = index;
  });

  return matchingId
}


function getDeviceReceiver() {
  selectElement = document.getElementById('select-device');
  selectedDeviceId = selectElement.value;

  return selectedDeviceId;
}

function verifyActiveDevices(id) {
  let match = false;
  activeDevicesId.forEach((deviceId) => {
    if(deviceId == id) match = true;
  });
  return match;
}

function pushNewCommandOption(id, deviceType) {
  var selectElement = document.getElementById('select-device');
  var opt = new Option(`${deviceType.toUpperCase()} ${id}`, id);
  selectElement.add(opt);
}

function removeCommandOption(id) {
  var selectElement = document.getElementById('select-device');
  const matchingId = getMatchingIndex(id);

  if(matchingId != -1) {
    selectElement.remove(matchingId);
    activeDevicesId = activeDevicesId.filter(deviceId => id !== deviceId);
    //console.log(activeDevicesId);
  }
}

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
      document.querySelector('#serial-connected').innerText = "";
        document.querySelector('#serial-disconnected').innerText = "UART: OFF";
        break;
      case 14:  //Conectado
        document.querySelector('#serial-disconnected').innerText = "";
        document.querySelector('#serial-connected').innerText = "UART: ON";
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
      case 102: //Informação do device recebido
        const id = djangoData['id'];
        const ip = djangoData['ip'];
        const lat = parseFloat(djangoData['lat']);
        const log = parseFloat(djangoData['log']);
        const status = djangoData['status'];
        const deviceType = djangoData['device'];

        //Adiciona novo device nas opções de comando
        if(!verifyActiveDevices(id)){
          if(status != "inactive") {
            activeDevicesId.push(id);
            pushNewCommandOption(id, deviceType);
          }
        }
        else {
          //Retira device se está nas opções e está inativo
          if(status == "inactive") {
            removeCommandOption(id);
          }
        }

        notifyUiWhenJsonReceived(msg.data, msgDrone);
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
  document.querySelector('#ip-connected').innerText = "";
  document.querySelector('#ip-disconnected').innerText = "IP: OFF";
  console.error('Receive POST socket closed unexpectedly');
}

updateSocket.onclose = function(e) {
  console.error('Update socket closed unexpectedly');
}


// Onclick functions
//-------------------
document.querySelector('#turn-on').onclick = function(e) {
  sendCommand(20);
};

document.querySelector('#turn-off').onclick = function(e) {
  sendCommand(22);
};

document.querySelector('#forward-1').onclick = function(e) {
  sendCommand(24);
};

document.querySelector('#forward-2').onclick = function(e) {
  sendCommand(26);
};

document.querySelector('#initiate-flight').onclick = function(e) {
  sendCommand(28);
};

document.querySelector('#interrupt-flight').onclick = function(e) {
  sendCommand(30);
};
