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
        center: { lat: -15.84163738782225, lng: -47.92686308971462 },
        zoom: 16,
      });
    };
  }

  findMarkerIdIndex(id) {
    return this.markers.findIndex(marker => marker.id === id);
  }

  newMarker(id, lat, log) {
    let foundedMarkerIndex = this.findMarkerIdIndex(id);

    if(foundedMarkerIndex == -1) {
      const icon_images = ['pin', 'pinRed', 'pinPurple', 'pinYellow']
      const url_icon = (id >= 5 && id <= 8) ? icon_images[id-5] : 'pin';
      let icon_image = `../static/connection_esp32/images/${url_icon}.png`;
      let icon = {
        url: icon_image,
        size: new google.maps.Size(43, 41),
        origin: new google.maps.Point(0,0),
        anchor: new google.maps.Point(21, 41)
      };

      let myLatLng = new google.maps.LatLng(lat,log);
      let marker = new google.maps.Marker({
        position: myLatLng,
        title: "Drone " + id,
        icon: icon
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