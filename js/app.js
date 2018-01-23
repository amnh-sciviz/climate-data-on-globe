'use strict';

var App = (function() {
  function App(options) {
    var defaults = {};
    this.opt = $.extend({}, defaults, options);
    this.init();
  }

  function getPNG(filename) {
    var deferred = $.Deferred();
    var img = new Image();

    var loaded = function(img){
      var canvas = document.createElement('canvas');
      var w = img.width;
      var h = img.height;
      canvas.width = w;
      canvas.height = h;
      var context = canvas.getContext('2d');
      context.drawImage(img, 0, 0, w, h);
      var data = context.getImageData(0, 0, w, h).data;
      deferred.resolve(data);
    };

    img.src = filename;
    if (img.complete) {
      loaded(img);
    } else {
      img.addEventListener('load', function(){
        loaded(img);
      });
    }

    return deferred.promise();
  }

  App.prototype.init = function(){
    var _this = this;

    $.when(
      $.getJSON(this.opt.geojson),
      $.getJSON(this.opt.meta),
      getPNG(this.opt.data)

    ).done(function(geojson, metadata, data){
      _this.onReady(geojson[0], metadata[0], data);
    });
  };

  App.prototype.loadListeners = function(){
    var _this = this;

    $(window).on('resize', function(){
      _this.globe.onResize();
    });
  };

  App.prototype.onReady = function(geojson, metadata, data){
    console.log("All globe data loaded");

    $('.loading').remove();

    this.globe = new Globe(_.extend({}, metadata, {"geojson": geojson, "data": data}));

    this.loadListeners();

    this.render();
  };

  App.prototype.render = function(){
    var _this = this;

    this.globe.render();

    requestAnimationFrame(function(){ _this.render(); });
  };

  return App;

})();

$(function() {
  var app = new App(CONFIG);
});
