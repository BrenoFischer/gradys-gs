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
        mapTypeId: 'satellite',
      });
    };
  }

  findMarkerIdIndex(id) {
    return this.markers.findIndex(marker => marker.id === id);
  }

  getMarkerColor(status) {
    if(status == 'active') return "green";
    if(status == 'inactive') return "red";
    return "yellow";
  }

  getMarkerImage(id, status, deviceType) {
    const markerColor = this.getMarkerColor(status);
    return deviceType == 'uav' ? 
      `https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_${markerColor}${id}.png`
    :
      `https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_black${id}.png`;
  }

  newMarker(id, lat, log, status, deviceType) {
    let foundedMarkerIndex = this.findMarkerIdIndex(id);

    if(foundedMarkerIndex == -1) {
      const image = this.getMarkerImage(id, status, deviceType);

      let myLatLng = new google.maps.LatLng(lat,log);
      let marker = new google.maps.Marker({
        position: myLatLng,
        title: "Drone " + id,
        icon: image,
        //label: {
        //  text: id.toString(),
        //  fontSize: "20px",
        //  fontWeight: "bold",
        //}
      });
      this.markers.push(new MyMarker(id, marker));
      marker.setMap(this.map);
    }
    else {
      const myLatLng = new google.maps.LatLng(lat,log);
      const image = this.getMarkerImage(id, status, deviceType);

      //can change .setVisible(false) if wanna hide
      //can change .setOpacity, between 0.0 and 1.0.
      this.markers[foundedMarkerIndex].marker.setIcon(image);
      this.markers[foundedMarkerIndex].marker.setPosition(myLatLng);
    }
  }
}

var gmap = new GoogleMaps();