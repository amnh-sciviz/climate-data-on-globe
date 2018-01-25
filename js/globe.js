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

  function getPoint(data, interval, particle, point, particleCount, pointsPerParticle) {
    var index = interval * particleCount * pointsPerParticle * 4 + particle * pointsPerParticle * 4 + point * 4;
    var x = data[index];
    var y = data[++index];
    var z = data[++index];
    var mag = data[++index];
    return [x, y, z, mag];
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
  }

  function lerpPoint(p1, p2, percent) {
    return [
      lerp(p1[0], p2[0], percent),
      lerp(p1[1], p2[1], percent),
      lerp(p1[2], p2[2], percent),
      lerp(p1[3], p2[3], percent)
    ]
  }

  function round(value, nearest) {
    return Math.round(value / nearest) * nearest;
  }

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

    var offsets = _.range(this.particleCount);
    this.offsets = _.map(offsets, function(v){ return Math.random(); });

    this.preprocessData(this.opt.data);

    this.loadEarth();
    this.loadGeojson(this.opt.geojson);
    this.loadData();
  };

  Globe.prototype.loadData = function() {
    var data = this.data;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var offsets = this.offsets;

    var positions = [];
    var colors = [];
    var color = new THREE.Color();

    var prev = false;
    var prevOffset = false;

    for (var i=0; i<particleCount; i++) {
      var offset = offsets[i];
      for (var j=0; j<pointsPerParticle; j++) {
        var point = getPoint(data, 0, i, j, particleCount, pointsPerParticle);
        var pOffset = 1.0 * j / (pointsPerParticle-1) + offset;
        pOffset = 1.0 - pOffset % 1.0;

        if (prev) {
          positions.push(prev[0], prev[1], prev[2]);
          positions.push(point[0], point[1], point[2]);
          // first point of new segment, add an "invisible" line
          if (j <= 0) {
            color.setRGB(0, 0, 0);
            colors.push(color.r, color.g, color.b);
            colors.push(color.r, color.g, color.b);
          } else {
            // mag = 0.5;
            // prevMag = 0.5;
            var mag = point[3];
            var prevMag = prev[3];
            color.setRGB(prevMag*prevOffset, prevMag*prevOffset, prevMag*prevOffset);
            colors.push(color.r, color.g, color.b);
            color.setRGB(mag*pOffset, mag*pOffset, mag*pOffset);
            colors.push(color.r, color.g, color.b);
          }
        }

        prev = point;
        prevOffset = pOffset;
      }
    }

    var geo = new THREE.BufferGeometry();
    geo.addAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geo.addAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    // geo.computeBoundingSphere();

    // geo.attributes.position.dynamic = true;
    // geo.attributes.color.dynamic = true;

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

  // Turn image data into [x, y, z, mag] values
  Globe.prototype.preprocessData = function(imgData){
    var intervals = this.intervals;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var minMag = this.opt.minMag;
    var precision = this.opt.precision;
    var radius = this.opt.radius * 1.001;

    var imgDataLen = imgData.length;
    var targetDataLen = intervals * particleCount * pointsPerParticle * 4;

    // console.log('Target data length:' + targetDataLen);
    var data = [];
    data.length = targetDataLen;

    var offsetPerPoint = 4;
    var rowLength = pointsPerParticle * intervals * offsetPerPoint;
    var offsetPerParticle = rowLength * 2;
    var offsetPerInterval = pointsPerParticle;

    for (var i=0; i<intervals; i++) {
      for (var j=0; j<particleCount; j++) {
        for (var k=0; k<pointsPerParticle; k++) {
          var start = i * offsetPerInterval * offsetPerPoint + j * offsetPerParticle + k * offsetPerPoint;
          var lon = round(imgData[start] / 255.0, precision);
          var lat = round(imgData[start+1] / 255.0, precision);
          var mag = round(imgData[start+2] / 255.0, precision);
          var lonDec = imgData[start+rowLength] / 255.0 * precision;
          var latDec = imgData[start+rowLength+1] / 255.0 * precision;
          var magDec = imgData[start+rowLength+2] / 255.0 * precision;
          lon = lerp(-270, 90, lon+lonDec);
          lat = lerp(90, -90, lat+latDec);
          mag = Math.max(minMag, mag + magDec);
          var point = toSphere(lon, lat, radius);
          var index = i * particleCount * pointsPerParticle * 4 + j * pointsPerParticle * 4 + k * 4;
          data[index] = point[0]; // x
          data[++index] = point[1]; // y
          data[++index] = point[2]; // z
          data[++index] = mag;
        }
      }
    }

    this.data = data;
  };

  Globe.prototype.render = function(yearProgress){
    var animationMs = this.opt.animationMs;
    var now = new Date();
    var animationProgress = (now % animationMs) / animationMs;

    this.updateGlobeData(yearProgress, animationProgress);
    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  };

  Globe.prototype.updateGlobeData = function(yearProgress, animationProgress){
    var mat = this.lineMat;
    var geo = this.lineGeo;
    var data = this.data;

    var intervals = this.intervals;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var offsets = this.offsets;

    var prev = false;
    var prevOffset = false;

    var interval1 = Math.floor(yearProgress * (intervals-1));
    var interval2 = interval1 + 1;
    if (interval2 >= intervals) interval2 = 0;
    var intervalProgress = (yearProgress * (intervals-1)) % 1.0;

    var positions = geo.attributes.position.array;
    var colors = geo.attributes.color.array;

    for (var i=0; i<particleCount; i++) {
      var offset = offsets[i];
      for (var j=0; j<pointsPerParticle; j++) {
        var point1 = getPoint(data, interval1, i, j, particleCount, pointsPerParticle);
        var point2 = getPoint(data, interval2, i, j, particleCount, pointsPerParticle);
        var point = lerpPoint(point1, point2, intervalProgress);

        var pOffset = 1.0 * j / (pointsPerParticle-1) + offset + animationProgress;
        pOffset = 1.0 - pOffset % 1.0;

        if (prev) {
          var geoIndex = (i * (pointsPerParticle-1) * 2 + (j * 2 - 1)) * 3;
          positions[geoIndex-3] = prev[0];
          positions[geoIndex-2] = prev[1];
          positions[geoIndex-1] = prev[2];
          positions[geoIndex] = point[0];
          positions[geoIndex+1] = point[1];
          positions[geoIndex+2] = point[2];
          if (j > 0) {
            var c0 = prev[3] * pOffset;
            var c1 = point[3] * pOffset;
            colors[geoIndex-3] = c0;
            colors[geoIndex-2] = c0;
            colors[geoIndex-1] = c0;
            colors[geoIndex] = c1;
            colors[geoIndex+1] = c1;
            colors[geoIndex+2] = c1;
          }
        }

        prev = point;
        prevOffset = pOffset;
      }
    }

    geo.attributes.position.needsUpdate = true;
    geo.attributes.color.needsUpdate = true;
    // geo.computeBoundingSphere();

    // mat.vertexColors = THREE.VertexColors;
    // mat.needsUpdate = true;
  };

  return Globe;

})();
