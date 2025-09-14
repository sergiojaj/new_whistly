// Simple helpers for Google Maps features used across pages

function createCircularIcon(url, size, callback) {
  try {
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      var canvas = document.createElement('canvas');
      canvas.width = size; canvas.height = size;
      var ctx = canvas.getContext('2d');
      ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
      ctx.closePath();
      ctx.clip();
      // cover-fit the image
      var scale = Math.max(size / img.width, size / img.height);
      var w = img.width * scale;
      var h = img.height * scale;
      var dx = (size - w) / 2;
      var dy = (size - h) / 2;
      ctx.drawImage(img, dx, dy, w, h);
      callback(canvas.toDataURL());
    };
    img.onerror = function () { callback(url); };
    img.src = url;
  } catch (e) {
    callback(url);
  }
}

// Utility: ensure Leaflet is loaded (CSS + JS) before invoking cb
function ensureLeafletLoaded(cb) {
  if (window.L && window.L.map) { cb(); return; }
  // inject CSS
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  document.head.appendChild(link);
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  script.onload = cb;
  document.body.appendChild(script);
}

// Guard to avoid double init
function markInited(el) {
  if (!el) return false;
  if (el.getAttribute('data-map-initialized') === '1') return true;
  el.setAttribute('data-map-initialized', '1');
  return false;
}

// Add Bird page: map with autocomplete and click-to-set marker (Google or Leaflet fallback)
function initAddBirdMap() {
  var mapDiv = document.getElementById('add-bird-map');
  if (!mapDiv) return;
  if (markInited(mapDiv)) return; // already initialized
  var locInput = document.getElementById('id_location');
  var latInput = document.getElementById('id_latitude');
  var lngInput = document.getElementById('id_longitude');

  var center = { lat: 39.8283, lng: -98.5795 }; // US center fallback
  if (typeof google !== 'undefined' && google.maps) {
    try {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (pos) {
          center = { lat: pos.coords.latitude, lng: pos.coords.longitude };
          map.setCenter(center);
          setMarker(center.lat, center.lng);
        });
      }
    } catch (e) {}

    var map = new google.maps.Map(mapDiv, {
      center: center,
      zoom: 5,
      mapTypeControl: false,
    });
    var marker = new google.maps.Marker({ map: map, draggable: false });
    function setMarker(lat, lng) {
      marker.setPosition({ lat: lat, lng: lng });
      latInput.value = lat.toFixed(6);
      lngInput.value = lng.toFixed(6);
    }
    map.addListener('click', function (e) {
      setMarker(e.latLng.lat(), e.latLng.lng());
    });
    // EXIF-based auto-detect from selected image
    try {
      var inputPic = document.getElementById('id_picture');
      if (inputPic) {
        inputPic.addEventListener('change', function(){
          if (!this.files || !this.files[0]) return;
          try {
            EXIF.getData(this.files[0], function(){
              var lat = EXIF.getTag(this, 'GPSLatitude');
              var lon = EXIF.getTag(this, 'GPSLongitude');
              var latRef = EXIF.getTag(this, 'GPSLatitudeRef');
              var lonRef = EXIF.getTag(this, 'GPSLongitudeRef');
              function dmsToDeg(dms){ return dms[0] + dms[1]/60 + dms[2]/3600; }
              if (lat && lon) {
                var la = dmsToDeg(lat); if (latRef === 'S') la = -la;
                var lo = dmsToDeg(lon); if (lonRef === 'W') lo = -lo;
                setMarker(la, lo);
                map.setCenter({lat: la, lng: lo});
                map.setZoom(13);
                // reverse geocode via free Nominatim
                reverseGeocodeNominatim(la, lo, function(addr){ if (locInput && addr) locInput.value = addr; });
              }
            });
          } catch(e){}
        });
      }
    } catch(e){}
    try {
      var autocomplete = new google.maps.places.Autocomplete(locInput, { fields: ['geometry', 'formatted_address', 'name'] });
      autocomplete.addListener('place_changed', function () {
        var place = autocomplete.getPlace();
        if (!place.geometry) return;
        var loc = place.geometry.location;
        map.setCenter(loc);
        map.setZoom(13);
        setMarker(loc.lat(), loc.lng());
        if (place.formatted_address) locInput.value = place.formatted_address;
      });
    } catch (e) {}
  } else {
    ensureLeafletLoaded(function () {
      // Leaflet fallback
      var map = L.map(mapDiv).setView([center.lat, center.lng], 5);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);
      var marker = L.marker([center.lat, center.lng]).addTo(map);
      function setMarker(lat, lng) {
        marker.setLatLng([lat, lng]);
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
      }
      map.on('click', function (e) { setMarker(e.latlng.lat, e.latlng.lng); });
      try {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(function (pos) {
            var c = [pos.coords.latitude, pos.coords.longitude];
            map.setView(c, 13); setMarker(c[0], c[1]);
          });
        }
      } catch (e) {}

      // Nominatim search function
      window.searchNominatim = function(query, email){
        if (!query || query.trim().length < 3) return;
        var url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q=' + encodeURIComponent(query);
        if (email) { url += '&email=' + encodeURIComponent(email); }
        fetch(url, { headers: { 'Accept': 'application/json' }})
          .then(function(r){ return r.json(); })
          .then(function(results){
            if (!results || !results.length) return;
            var r = results[0];
            var lat = parseFloat(r.lat), lon = parseFloat(r.lon);
            if (isFinite(lat) && isFinite(lon)){
              map.setView([lat, lon], 13);
              setMarker(lat, lon);
              if (locInput && r.display_name) { locInput.value = r.display_name; }
            }
          }).catch(function(){});
      };

      // EXIF-based auto-detect from selected image
      try {
        var inputPic = document.getElementById('id_picture');
        if (inputPic) {
          inputPic.addEventListener('change', function(){
            if (!this.files || !this.files[0]) return;
            try {
              EXIF.getData(this.files[0], function(){
                var lat = EXIF.getTag(this, 'GPSLatitude');
                var lon = EXIF.getTag(this, 'GPSLongitude');
                var latRef = EXIF.getTag(this, 'GPSLatitudeRef');
                var lonRef = EXIF.getTag(this, 'GPSLongitudeRef');
                function dmsToDeg(dms){ return dms[0] + dms[1]/60 + dms[2]/3600; }
                if (lat && lon) {
                  var la = dmsToDeg(lat); if (latRef === 'S') la = -la;
                  var lo = dmsToDeg(lon); if (lonRef === 'W') lo = -lo;
                  setMarker(la, lo);
                  map.setView([la, lo], 13);
                  // reverse geocode via free Nominatim
                  reverseGeocodeNominatim(la, lo, function(addr){ if (locInput && addr) locInput.value = addr; });
                }
              });
            } catch(e){}
          });
        }
      } catch(e){}
    });
  }
}

function reverseGeocodeNominatim(lat, lon, cb, email){
  var url = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + encodeURIComponent(lat) + '&lon=' + encodeURIComponent(lon);
  if (email) { url += '&email=' + encodeURIComponent(email); }
  fetch(url, { headers: { 'Accept': 'application/json' }})
   .then(function(r){ return r.json(); })
   .then(function(j){ cb && cb(j && j.display_name); })
   .catch(function(){ cb && cb(null); });
}

// Profile map: show markers for user's birds
function initProfileMap() {
  var mapDiv = document.getElementById('profile-map');
  if (!mapDiv || typeof google === 'undefined') return;
  var birds = (typeof window.PROFILE_BIRDS !== 'undefined') ? window.PROFILE_BIRDS : [];
  var center = { lat: 20, lng: 0 };
  if (birds.length) {
    center = { lat: birds[0].lat, lng: birds[0].lng };
  }
  if (typeof google !== 'undefined' && google.maps) {
    var map = new google.maps.Map(mapDiv, { center: center, zoom: birds.length ? 4 : 2, mapTypeControl: false });
    var bounds = new google.maps.LatLngBounds();
    birds.forEach(function (b) {
      var pos = { lat: b.lat, lng: b.lng };
      createCircularIcon(b.image, 48, function (iconUrl) {
        var marker = new google.maps.Marker({ position: pos, map: map, icon: { url: iconUrl, scaledSize: new google.maps.Size(48, 48) }, title: b.species });
        marker.addListener('click', function () { window.location.href = b.url; });
      });
      bounds.extend(pos);
    });
    if (birds.length > 1) {
      map.fitBounds(bounds);
    }
  } else {
    ensureLeafletLoaded(function () {
      ensureLeafletClusterLoaded(function(){
        var map = L.map(mapDiv).setView([center.lat, center.lng], birds.length ? 4 : 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
        var cluster = L.markerClusterGroup();
        var bounds = [];
        birds.forEach(function (b) {
          var pos = [b.lat, b.lng];
          var html = '<div style="width:48px;height:48px;border-radius:50%;background-size:cover;background-position:center;background-image:url(' + b.image + ');"></div>';
          var icon = L.divIcon({ html: html, className: 'leaflet-div-icon', iconSize: [48, 48] });
          var marker = L.marker(pos, { icon: icon });
          marker.on('click', function () { window.location.href = b.url; });
          cluster.addLayer(marker);
          bounds.push(pos);
        });
        map.addLayer(cluster);
        if (bounds.length > 1) { map.fitBounds(bounds); }
      });
    });
  }
}

// Single bird detail map
function initBirdMap() {
  var mapDiv = document.getElementById('bird-map');
  if (!mapDiv || !window.BIRD_POS) return;
  if (markInited(mapDiv)) return;
  if (typeof google !== 'undefined' && google.maps) {
    var map = new google.maps.Map(mapDiv, { center: window.BIRD_POS, zoom: 13, mapTypeControl: false });
    new google.maps.Marker({ position: window.BIRD_POS, map: map });
  } else {
    ensureLeafletLoaded(function () {
      var map = L.map(mapDiv).setView([window.BIRD_POS.lat, window.BIRD_POS.lng], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
      L.marker([window.BIRD_POS.lat, window.BIRD_POS.lng]).addTo(map);
    });
  }
}

// My birds full screen map
function initMyBirdsMap() {
  var mapDiv = document.getElementById('my-birds-map');
  if (!mapDiv) return;
  var birds = (typeof window.MY_BIRDS !== 'undefined') ? window.MY_BIRDS : [];
  var center = birds.length ? {lat: birds[0].lat, lng: birds[0].lng} : {lat: 20, lng: 0};
  ensureLeafletLoaded(function(){
    ensureLeafletClusterLoaded(function(){
      var map = L.map(mapDiv).setView([center.lat, center.lng], birds.length ? 4 : 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(map);
      var cluster = L.markerClusterGroup();
      var bounds = [];
      birds.forEach(function(b){
        var pos = [b.lat, b.lng];
        var html = '<div style="width:48px;height:48px;border-radius:50%;background-size:cover;background-position:center;background-image:url(' + b.image + ');"></div>';
        var icon = L.divIcon({ html: html, className: 'leaflet-div-icon', iconSize: [48, 48] });
        var marker = L.marker(pos, { icon: icon });
        marker.on('click', function () { window.location.href = b.url; });
        cluster.addLayer(marker);
        bounds.push(pos);
      });
      map.addLayer(cluster);
      if (bounds.length > 1) { map.fitBounds(bounds); }
    });
  });
}

// Load Leaflet.markercluster plugin
function ensureLeafletClusterLoaded(cb){
  if (window.L && L.MarkerClusterGroup) { cb(); return; }
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css';
  document.head.appendChild(link);
  var link2 = document.createElement('link');
  link2.rel = 'stylesheet';
  link2.href = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css';
  document.head.appendChild(link2);
  var script = document.createElement('script');
  script.src = 'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js';
  script.onload = cb;
  document.body.appendChild(script);
}

// Expose to global for Google callback
window.initAddBirdMap = initAddBirdMap;
window.initProfileMap = initProfileMap;
window.initBirdMap = initBirdMap;
window.initMyBirdsMap = initMyBirdsMap;
