'use strict';

var Globe = (function() {
  function Globe(options) {
    var defaults = {
      el: '#globe',
      viewAngle: 45,
      near: 0.01,
      far: 1000,
      radius: 0.5,
      minMag: 0.2,
      precision: 0.01,
      animationMs: 2000,
      yearMs: 120000
    };
    this.opt = $.extend({}, defaults, options);
    this.init();
  }

  function getCoordinateFromImageData(data, i, j, pointsPerParticle, intervals, precision, minMag, interval) {
    var rowLength = pointsPerParticle * intervals * 4;
    var offsetPerParticle = rowLength * 2;
    var offsetPerInterval = pointsPerParticle;
    var start = i * offsetPerParticle + interval * offsetPerInterval * 4 + j * 4;
    var lon = round(data[start] / 255.0, precision);
    var lat = round(data[start+1] / 255.0, precision);
    var mag = round(data[start+2] / 255.0, precision);
    var lonDec = data[start+rowLength] / 255.0 * precision;
    var latDec = data[start+rowLength+1] / 255.0 * precision;
    var magDec = data[start+rowLength+2] / 255.0 * precision;
    lon = lerp(-270, 90, lon+lonDec);
    lat = lerp(90, -90, lat+latDec);
    mag = Math.max(minMag, mag + magDec);
    return [lon, lat, mag];
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
  }

  function round(value, nearest) {
    return Math.round(value / nearest) * nearest;
  };

  function toSphere(lon, lat, radius) {
    var phi = (90-lat) * (Math.PI/180);
    var theta = (lon+180) * (Math.PI/180);
    var x = -(radius * Math.sin(phi) * Math.cos(theta));
    var y = (radius * Math.cos(phi));
    var z = (radius * Math.sin(phi) * Math.sin(theta));
    return [x, y, z];
  }

  Globe.prototype.init = function(){
    this.$el = $(this.opt.el);
    this.intervals = this.opt.intervals;
    this.particleCount = this.opt.particleCount;
    this.pointsPerParticle = this.opt.pointsPerParticle;
    this.data = this.opt.data;
    this.dataLen = this.data.length;

    var offsets = _.range(this.particleCount);
    this.offsets = _.map(offsets, function(v){ return Math.random(); });

    this.loadEarth();
    this.loadGeojson(this.opt.geojson);
    this.loadData();
  };

  Globe.prototype.loadData = function() {
    var data = this.data;
    var intervals = this.intervals;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var offsets = this.offsets;
    var radius = this.opt.radius * 1.001;
    var minMag = this.opt.minMag;
    var precision = this.opt.precision;

    var geo = new THREE.Geometry();

    var prev = false;
    var prevMag = false;
    var prevOffset = false;
    var interval = 0;

    for (var i=0; i<particleCount; i++) {
      var offset = offsets[i];
      for (var j=0; j<pointsPerParticle; j++) {
        var coord = getCoordinateFromImageData(data, i, j, pointsPerParticle, intervals, precision, minMag, interval);
        var lon = coord[0];
        var lat = coord[1];
        var mag = coord[2];

        var pOffset = 1.0 * j / (pointsPerParticle-1) + offset;
        pOffset = 1.0 - pOffset % 1.0;

        var point = toSphere(lon, lat, radius);

        if (prev) {
          geo.vertices.push(new THREE.Vector3(prev[0], prev[1], prev[2]));
          geo.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
          // first point of new segment, add an "invisible" line
          if (j <= 0) {
            geo.colors.push(new THREE.Color(0, 0, 0));
            geo.colors.push(new THREE.Color(0, 0, 0));
          } else {
            // mag = 0.5;
            // prevMag = 0.5;
            geo.colors.push(new THREE.Color(prevMag*prevOffset, prevMag*prevOffset, prevMag*prevOffset));
            geo.colors.push(new THREE.Color(mag*pOffset, mag*pOffset, mag*pOffset));
          }
        }

        prev = point.slice(0);
        prevMag = mag;
        prevOffset = pOffset;
      }
    }

    var mat = new THREE.LineBasicMaterial({ vertexColors: THREE.VertexColors });
    var line = new THREE.LineSegments(geo, mat);

    this.lineGeo = geo;
    this.lineMat = mat;
    this.scene.add(line);
  };

  Globe.prototype.loadEarth = function() {
    var _this = this;
    var w = this.$el.width();
    var h = this.$el.height();
    var radius = this.opt.radius;

    // init renderer
    this.renderer = new THREE.WebGLRenderer({alpha: true, antialias: true});
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.setSize(w, h);
    this.$el.append(this.renderer.domElement);

    // init scene
    this.scene = new THREE.Scene();

    // init camera
    var viewAngle = this.opt.viewAngle;
    var aspect = w / h;
    var near = this.opt.near;
    var far = this.opt.far;
    this.camera = new THREE.PerspectiveCamera(viewAngle, w / h, near, far);
    this.camera.position.z = radius * 4.0;

    // ambient light
    var aLight = new THREE.AmbientLight(0x888888);
    this.scene.add(aLight);

    // init controls
    this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);

    // init globe
    var geometry = new THREE.SphereGeometry(radius, 64, 64);
    var material = new THREE.MeshBasicMaterial({ color: 0x000000 });

    this.earth = new THREE.Mesh(geometry, material);
    this.earth.rotation.y = Math.PI;

    // equator
    // var eqGeo = new THREE.CircleGeometry(radius*1.0001, 64);
    // eqGeo.vertices.shift();
    // eqGeo.vertices.push(eqGeo.vertices[0].clone());
    // var eqMat = new THREE.LineBasicMaterial( { color: 0x00f6ff } );
    // var equator = new THREE.Line(eqGeo, eqMat);
    // equator.rotation.x = Math.PI / 2;
    // this.scene.add(equator);

    // add north arrow
    var dir = new THREE.Vector3(0, 1, 0);
    var origin = new THREE.Vector3(0, 0, 0);
    var length = radius * 1.5;
    var hex = 0x00ff00;
    var northArrow = new THREE.ArrowHelper(dir, origin, length, hex);
    this.earth.add(northArrow);

    // add south arrow
    dir = new THREE.Vector3(0, -1, 0);
    hex = 0xff0000;
    var southArrow = new THREE.ArrowHelper(dir, origin, length, hex);
    this.earth.add(southArrow);
    this.scene.add(this.earth);
  };

  Globe.prototype.loadGeojson = function(geojsonData){
    var opt = {
      color: 0x555555
    };
    var radius = this.opt.radius * 1.001;

    drawThreeGeo(geojsonData, radius, 'sphere', opt, this.scene);
  };

  Globe.prototype.onResize = function(){
    var w = this.$el.width();
    var h = this.$el.height();

    this.renderer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  };

  Globe.prototype.render = function(){
    var animationMs = this.opt.animationMs;
    var yearMs = this.opt.yearMs;
    var now = new Date();

    var yearProgress = (now % yearMs) / yearMs;
    var animationProgress = (now % animationMs) / animationMs;

    this.updateGlobeData(yearProgress, animationProgress);

    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  };

  Globe.prototype.updateGlobeData = function(yearProgress, animationProgress){
    var mat = this.lineMat;
    var geo = this.lineGeo;
    var data = this.data;
    var dataLen = this.dataLen;

    var intervals = this.intervals;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var offsets = this.offsets;
    var minMag = this.opt.minMag;
    var precision = this.opt.precision;
    var radius = this.opt.radius * 1.001;

    var prev = false;
    var prevMag = false;
    var prevOffset = false;
    var rowLength = pointsPerParticle * intervals * 4;
    var offsetPerParticle = rowLength * 2;

    var interval1 = Math.floor(yearProgress * (intervals-1));
    var interval2 = interval1 + 1;
    if (interval2 >= intervals) interval2 = 0;
    var intervalProgress = (yearProgress * (intervals-1)) % 1.0;

    for (var i=0; i<particleCount; i++) {
      var offset = offsets[i];
      for (var j=0; j<pointsPerParticle; j++) {
        var coord1 = getCoordinateFromImageData(data, i, j, pointsPerParticle, intervals, precision, minMag, interval1);
        var coord2 = getCoordinateFromImageData(data, i, j, pointsPerParticle, intervals, precision, minMag, interval2);
        var lon = lerp(coord1[0], coord2[0], intervalProgress);
        var lat = lerp(coord1[1], coord2[1], intervalProgress);
        var mag = lerp(coord1[2], coord2[2], intervalProgress);

        var pOffset = 1.0 * j / (pointsPerParticle-1) + offset + animationProgress;
        pOffset = 1.0 - pOffset % 1.0;

        var point = toSphere(lon, lat, radius);

        if (prev) {
          var index = i * (pointsPerParticle-1) * 2 + (j * 2 - 1);
          geo.vertices[index-1].set(prev[0], prev[1], prev[2]);
          geo.vertices[index].set(point[0], point[1], point[2]);
          if (j > 0) {
            geo.colors[index-1].setRGB(prevMag*prevOffset, prevMag*prevOffset, prevMag*prevOffset);
            geo.colors[index].setRGB(mag*pOffset, mag*pOffset, mag*pOffset);
          }
        }

        prev = point.slice(0);
        prevMag = mag;
        prevOffset = pOffset;
      }
    }

    geo.colorsNeedUpdate = true;
    geo.verticesNeedUpdate = true;
    mat.vertexColors = THREE.VertexColors;
    mat.needsUpdate = true;
  };

  return Globe;

})();
