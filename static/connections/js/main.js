// Starting websocket connections
var observableSocket = new WebSocket('ws://localhost:8000/ws/connection/');
var sendCommandSocket = new WebSocket('ws://localhost:8000/ws/receive/');
var receivePostSocket = new WebSocket('ws://localhost:8000/ws/update-info/');
var updateSocket = new WebSocket('ws://localhost:8000/ws/update-periodically/');

// List of active devices that'll show at 'select' field
var activeDevicesId = []

// Set the interface status to connected, if POST socket is Open
if(receivePostSocket.readyState === WebSocket.OPEN || receivePostSocket.readyState === WebSocket.CONNECTING){
  document.querySelector('#ip-connected').innerText = "IP: OK";
}

function sendCommand(type) {
  // Send the selected command to a set of devices, obtained from getDeviceReceive()
  //
  // Format of command-json that will be sent:
  // id - (int) id of the groundstation
  // type - (int) integer that represent what this command will do (see table of commands)
  // receiver - (int) ID of the active device on the 'select-device list'
  //            note if the command will be sent to all devices, the ID will be 'all'

  jsonToSend = {id: 1, type: type}
  jsonToSend["receiver"] = getDeviceReceiver();

  jsonToSend = JSON.stringify(jsonToSend);
  console.log(jsonToSend);
  
  // Send the command to the Consumers.
  // The PostConsumer will receive the command and handle it
  if (receivePostSocket.readyState == WebSocket.OPEN) {
    receivePostSocket.send(jsonToSend);
    notifyUiWhenJsonSent(jsonToSend);
  }

  // The ReceiveCommandConsumer will receive the command and handle it
  // Note this is the Serial Consumer, in charge to stablish and change messages with serial connected device
  if (sendCommandSocket.readyState == WebSocket.OPEN) {
    //sendCommandSocket.send(jsonToSend);
    //notifyUiWhenJsonSent(jsonToSend);
  }
}



function getMatchingIndex(id) {
  //Return the index of the matching ID, in the list of active devices OR return -1 if not found
  var matchingId = -1;

  [...document.getElementById('select-device').children].forEach((option, index) => {
    if(option.value == id) matchingId = index;
  });

  return matchingId
}


function getDeviceReceiver() {
  // Return the device ID selected at 'select' field
  selectElement = document.getElementById('select-device');
  selectedDeviceId = selectElement.value;

  return selectedDeviceId;
}

function verifyActiveDevices(id) {
  // Search the list of active devices and
  // return true if found matching ID
  // return false if not found matching ID
  let match = false;
  activeDevicesId.forEach((deviceId) => {
    if(deviceId == id) match = true;
  });
  return match;
}

function pushNewCommandOption(id, deviceType) {
  // Insert in the 'select' field a new device option
  var selectElement = document.getElementById('select-device');
  var opt = new Option(`${deviceType.toUpperCase()} ${id}`, id);
  selectElement.add(opt);
}

function removeCommandOption(id) {
  // Remove from the 'select' field a device with matching id
  var selectElement = document.getElementById('select-device');
  const matchingId = getMatchingIndex(id);

  if(matchingId != -1) {
    selectElement.remove(matchingId);
    activeDevicesId = activeDevicesId.filter(deviceId => id !== deviceId);
  }
}

function notifyUiWhenJsonSent(jsonSent) {
  // Insert on interface visual log the command sent.
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode("Command sent: " + jsonSent));
  p.className += "json-sent";

  element.prepend(p);
}

function notifyUiWhenJsonReceived(jsonReceived, msg) {
  // Insert on interface visual log the message received
  var element = document.getElementById('actions-logs');
  var p = document.createElement("p");
  p.appendChild(document.createTextNode(msg + jsonReceived));
  p.className += "json-received";

  element.prepend(p);
}

function checkJsonType(msg) {
  // The main logic to handle received messages
  // A message will try to be parsed to JSON format, and it's 'type' will contain what the message represents
  // The type 102 represents a location update message, and it'll be reflected on Google Maps.
  // All messages are shown on interface visual log
  try {
    var djangoData = JSON.parse(msg.data);
    console.log(djangoData);
    json_type = djangoData['type'];

    msgUi = 'ACK: ';
    msgDefault = 'JSON unknown: ';
    msgDrone = 'UAV info: ';

    switch(json_type) {
      case 102: // Device information received
        var id = djangoData['id'];
        var lat = parseFloat(djangoData['lat']);
        var lng = parseFloat(djangoData['lng']);
        var status = djangoData.hasOwnProperty('status') ? djangoData['status'] : 'active';
        var deviceType = djangoData.hasOwnProperty('device') ? djangoData['device'] : 'uav';

        // Add device as a new option in Select list, if not already included
        if(!verifyActiveDevices(id)){
          if(status != 'inactive') {
            activeDevicesId.push(id);
            pushNewCommandOption(id, deviceType);
          }
        }
        // else {
        //   //Retira device se está nas opções e está inativo
        //   if(status == 'inactive') {
        //     removeCommandOption(id);
        //   }
        // }

        notifyUiWhenJsonReceived(msg.data, msgDrone);
        // Insert/Update the marker on Google Maps, with it's location
        gmap.newMarker(id, lat, lng, status, deviceType);
        break;

      // The default behavior to other types not included above
      default:
        notifyUiWhenJsonReceived(msg.data, msgDefault);
        break;
    }
  } catch(e) {
    // If it's not a JSON, it'll show the message on interface visual log
    notifyUiWhenJsonReceived(msg.data);
  }
}

function checkAbort(checkbox) {
  if(checkbox.checked) {
    sendCommand(30);
  }
  else {
    sendCommand(31);
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
  document.querySelector('#ip-disconnected').innerText = 'IP: OFF';
  console.error('Receive POST socket closed unexpectedly');
}

updateSocket.onclose = function(e) {
  console.error('Update socket closed unexpectedly');
}


// Onclick functions
//-------------------
// Table of commands:
// 20: /path_position_absolute
// 22: /path_position_relative
// 24: /auto
// 26: /run_experiment
// 28: /set_auto
// 30: /set_rtl
// 32: /takeoff_and_hold
document.querySelector('#position-absolute').onclick = function(e) {
  sendCommand(20);
};

document.querySelector('#position-relative').onclick = function(e) {
  sendCommand(22);
};

document.querySelector('#auto').onclick = function(e) {
  sendCommand(24);
};

document.querySelector('#run-experiment').onclick = function(e) {
  sendCommand(26);
};

document.querySelector('#set-auto').onclick = function(e) {
  sendCommand(28);
};

// document.querySelector('#abort-all').onclick = function(e) {
//   sendCommand(30);
// };

document.querySelector('#takeoff-and-hold').onclick = function(e) {
  sendCommand(32);
};
