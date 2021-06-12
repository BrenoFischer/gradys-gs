class MyMarker {
  constructor(id, marker) {
    this.id = id;
    this.marker = marker;    
  }
}

class GoogleMaps {
  constructor() {
    this.markers = [];
    this.map;
    this.initMap = function () {
      this.map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -22.9469182, lng: -43.1615082 },
        zoom: 15,
      });
    };
  }

  findMarkerIdIndex(id) {
    return this.markers.findIndex(marker => marker.id === id);
  }

  newMarker(id, lat, log) {
    let foundedMarkerIndex = this.findMarkerIdIndex(id);
    if(foundedMarkerIndex == -1) {
      let myLatLng = new google.maps.LatLng(lat,log);
      let marker = new google.maps.Marker({
        position: myLatLng,
        title: "Drone " + id
      });
      this.markers.push(new MyMarker(id, marker));
      marker.setMap(this.map);
    }
    else {
      let myLatLng = new google.maps.LatLng(lat,log);
      this.markers[foundedMarkerIndex].marker.setPosition(myLatLng);
    }
  }
}

var gmap = new GoogleMaps();