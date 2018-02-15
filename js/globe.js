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

    this.$el.append($('<h2>'+this.opt.title+'</h2>'))

    this.frames = _.map(this.opt.frames, function(path){
      return {
        path: path,
        texture: false
      }
    });

    var offsets = _.range(this.particleCount);
    this.offsets = _.map(offsets, function(v){ return Math.random(); });

    this.preprocessData(this.opt.data);
    this.initScene();
    this.loadGeojson(this.opt.geojson);
    this.loadParticles();
  };

  Globe.prototype.initScene = function() {
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
    // var aLight = new THREE.AmbientLight(0x888888);
    // this.scene.add(aLight);

    // init controls
    this.controls = new THREE.OrbitControls(this.camera, $("#globes")[0]);
  };

  Globe.prototype.loadEarth = function(from, to, mu) {
    var radius = this.opt.radius;

    // init globe
    var geo = new THREE.SphereGeometry(radius, 64, 64);
    var uniforms = {
      fromTexture: {
        type: 't',
        value: from
      },
      mu: {
        type: 'f',
        value: mu
      },
      toTexture: {
        type: 't',
        value: to
      }
    };
    var mat = new THREE.ShaderMaterial({
      uniforms: uniforms,
      vertexShader: document.getElementById('imageVertexShader').textContent,
      fragmentShader: document.getElementById('imageFragmentShader').textContent
    });

    this.earth = new THREE.Mesh(geo, mat);
    this.earth.rotation.y = -Math.PI/2;

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

  Globe.prototype.loadEarthTexture = function(from, to, mu) {
    var loader = new THREE.TextureLoader();
    var _this = this;
    var earth = this.earth;

    var loadImageTexture = function(frame){
      var deferred = $.Deferred();

      if (frame.texture) {
        // console.log('Found existing '+frame.path);
        setTimeout(function(){
          deferred.resolve(frame.texture);
        },10);
      } else {
        // console.log('Loading path '+frame.path)
        var loader = new THREE.TextureLoader();
        loader.load(frame.path, function(texture){
          frame.texture = texture;
          deferred.resolve(texture);
        });
      }
      return deferred.promise();
    };

    $.when(
      loadImageTexture(from),
      loadImageTexture(to)

    ).done(function(textureFrom, textureTo){
      _this.loadingEarthTexture = false;
      if (earth) _this.updateEarthTexture(textureFrom, textureTo, mu);
      else _this.loadEarth(textureFrom, textureTo, mu);
    });
  };

  Globe.prototype.loadGeojson = function(geojsonData){
    var opt = {
      color: this.opt.geojsonLineColor
    };
    var radius = this.opt.radius * 1.001;

    drawThreeGeo(geojsonData, radius, 'sphere', opt, this.scene);
  };

  Globe.prototype.loadParticles = function() {
    var data = this.data;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var offsets = this.offsets;

    var positions = [];
    var particleOffsets = [];
    var pointOffsets = [];

    // initialize empty months
    for (var m=0; m<12; m++) {
      positions.push([]);
    }

    var prevPoints = false;
    var prevOffset = false;

    for (var i=0; i<particleCount; i++) {
      var particleOffset = offsets[i];
      for (var j=0; j<pointsPerParticle; j++) {

        var points = [];
        for (var m=0; m<12; m++) {
          points.push(getPoint(data, m, i, j, particleCount, pointsPerParticle));
        }

        var pointOffset = 1.0 * j / (pointsPerParticle-1);
        if (prevPoints) {
          particleOffsets.push(particleOffset, particleOffset);
          pointOffsets.push(prevOffset, pointOffset);

          for (var m=0; m<12; m++) {
            var point = points[m];
            var prev = prevPoints[m];

            // first point of new segment, add an "invisible" line
            var mag = 0;
            var prevMag = 0;
            if (j > 0) {
              var mag = point[3];
              var prevMag = prev[3];
            }

            positions[m].push(
              prev[0], prev[1], prev[2], prevMag,
              point[0], point[1], point[2], mag
            );
          }
        }
        prevPoints = points;
        prevOffset = pointOffset;
      }
    }

    // Create geometry using buffer geometry for performance boost
    var geo = new THREE.BufferGeometry();
    var months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'];
    geo.addAttribute('position', new THREE.Float32BufferAttribute(positions[0], 4));
    for (var m=0; m<12; m++) {
      var name = months[m];
      geo.addAttribute(name, new THREE.Float32BufferAttribute(positions[m], 4));
    }
    geo.addAttribute('particleOffset', new THREE.Float32BufferAttribute(particleOffsets, 1));
    geo.addAttribute('pointOffset', new THREE.Float32BufferAttribute(pointOffsets, 1));

    var uniforms = {
      animationProgress: { type: "f", value: 0.0 },
      yearProgress: { type: "f", value: 0.0 },
      color: { type: "c", value: new THREE.Color( 0xffffff ) }
    };
    var mat = new THREE.ShaderMaterial({
      uniforms: uniforms,
      vertexShader: document.getElementById('particleVertexShader').textContent,
      fragmentShader: document.getElementById('particleFragmentShader').textContent,
      blending: THREE.AdditiveBlending,
      // depthTest: false,
      transparent: true,
      vertexColors: THREE.VertexColors
    });

    var line = new THREE.LineSegments(geo, mat);

    this.lineGeo = geo;
    this.lineMat = mat;
    this.scene.add(line);
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

        // retrieve coordinates from image data
        var lons = [];
        var lats = [];
        var mags = [];
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
          lons.push(lon);
          lats.push(lat);
          mags.push(mag);
        }

        // TODO: smooth out the coordinates
        // var degree = 3;
        // lons = smooth(lons, degree);
        // lats = smooth(lats, degree);

        // add the data
        for (var k=0; k<pointsPerParticle; k++) {
          var lon = lons[k];
          var lat = lats[k];
          var mag = mags[k];
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

    this.updateEarth(yearProgress);
    this.updateGlobeData(yearProgress, animationProgress);
    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  };

  Globe.prototype.updateEarth = function(yearProgress){
    if (this.loadingEarthTexture) return false;
    var frames = this.frames;
    var m = yearProgress * 12;
    var from = Math.floor(m);
    var to = from + 1;
    var mu = m - from;
    if (to >= 12) to = 0;

    if (this.from != from) {
      this.loadingEarthTexture = true;
      this.loadEarthTexture(frames[from], frames[to], mu);
      this.from = from;
      this.to = to;

    } else {
      this.updateEarthTextureMu(mu);
    }
  };

  Globe.prototype.updateEarthTexture = function(from, to, mu){
    if (!this.earth) return false;
    // console.log('updating '+mu)
    var uniforms = this.earth.material.uniforms;
    uniforms.fromTexture.value = from;
    uniforms.toTexture.value = to;
    uniforms.mu.value = mu;
  };

  Globe.prototype.updateEarthTextureMu = function(mu){
    if (!this.earth) return false;
    this.earth.material.uniforms.mu.value = mu;
  };

  Globe.prototype.updateGlobeData = function(yearProgress, animationProgress){
    var uniforms = this.lineMat.uniforms;
    uniforms.yearProgress.value = yearProgress;
    uniforms.animationProgress.value = animationProgress;
  };

  return Globe;

})();
