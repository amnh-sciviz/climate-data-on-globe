'use strict';

var Globe = (function() {
  function Globe(options) {
    var defaults = {
      el: '#globe',
      viewAngle: 45,
      near: 0.01,
      far: 1000,
      radius: 0.5
    };
    this.opt = $.extend({}, defaults, options);
    this.init();
  }

  function lerp(a, b, percent) {
    return (1.0*b - a) * percent + a;
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

    this.loadEarth();
    this.loadGeojson(this.opt.geojson);
    this.loadData(this.opt.data);
  };

  Globe.prototype.loadData = function(data) {
    var intervals = this.intervals;
    var particleCount = this.particleCount;
    var pointsPerParticle = this.pointsPerParticle;
    var radius = this.opt.radius * 1.001;

    var geo = new THREE.Geometry();

    var prev = false;
    for (var i=0; i<pointsPerParticle; i++) {
      var start = i * 4;
      var lon = lerp(-180, 180, data[start] / 255.0);
      var lat = lerp(-90, 90, data[start+1] / 255.0);
      var mag = data[start+2] / 255.0;
      var point = toSphere(lon, lat, radius);

      if (prev) {
        geo.vertices.push(new THREE.Vector3(prev[0], prev[1], prev[2]));
        geo.vertices.push(new THREE.Vector3(point[0], point[1], point[2]));
        geo.colors.push(new THREE.Color(mag, mag, mag));
        geo.colors.push(new THREE.Color(mag, mag, mag));
      }

      prev = point;
    }

    var mat = new THREE.LineBasicMaterial({ vertexColors: THREE.VertexColors });
    var line = new THREE.LineSegments(geo, mat);

    this.scene.add(line);

    // geometry.colors[ 0 ].setRGB( 1, 0, 0 );
    // geometry.colorsNeedUpdate = true;
    // material.vertexColors = THREE.VertexColors;
    // material.needsUpdate = true;
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
    var material = new THREE.MeshBasicMaterial({ color: 0x111111 });

    this.earth = new THREE.Mesh(geometry, material);
    this.earth.rotation.y = Math.PI;

    // equator
    var eqGeo = new THREE.CircleGeometry(radius*1.0001, 64);
    eqGeo.vertices.shift();
    eqGeo.vertices.push(eqGeo.vertices[0].clone());
    var eqMat = new THREE.LineBasicMaterial( { color: 0x00f6ff } );
    var equator = new THREE.Line(eqGeo, eqMat);
    equator.rotation.x = Math.PI / 2;

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
    this.scene.add(equator);
  };

  Globe.prototype.loadGeojson = function(geojsonData){
    var opt = {
      color: 'white'
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
    this.renderer.render(this.scene, this.camera);
    this.controls.update();
  };

  return Globe;

})();
