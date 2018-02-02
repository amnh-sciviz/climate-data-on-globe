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
      deferred.resolve([data]);
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

    var promises = [$.getJSON(this.opt.geojson)];
    var globes = this.opt.globes;

    _.each(globes, function(globe){
      promises.push($.getJSON(globe.meta));
      promises.push(getPNG(globe.data));
    });

    $.when.apply(null, promises).done(function () {
      var responses = []
      for(var arg = 0; arg < arguments.length; ++ arg) {
        var response = arguments[arg][0];
        responses.push(response);
      }
      _this.onReady(responses[0], responses.slice(1));
    });
  };

  App.prototype.loadListeners = function(){
    var _this = this;

    var globes = this.globes;

    $(window).on('resize', function(){
      _.each(globes, function(globe){
        globe.onResize();
      });
    });
  };

  App.prototype.onReady = function(geojson, globeDatas){
    console.log("All globe data loaded");

    $('.loading').remove();

    this.globes = [];
    var globes = [];
    var globesOpt = this.opt.globes;

    for (var i=0; i<globeDatas.length; i+=2) {
      var metadata = globeDatas[i];
      var data = globeDatas[i+1];

      globes.push(new Globe(_.extend({}, metadata, globesOpt[i/2], {"geojson": geojson, "data": data})));
    }

    this.globes = globes;
    this.calendar = new Calendar(_.extend({}, this.opt.calendar));

    this.loadListeners();

    this.render();
  };

  App.prototype.render = function(){
    var _this = this;

    var now = new Date();
    var yearMs = this.opt.yearMs;
    var yearProgress = (now % yearMs) / yearMs;

    _.each(this.globes, function(globe){
      globe.render(yearProgress);
    });

    this.calendar.render(yearProgress);

    requestAnimationFrame(function(){ _this.render(); });
  };

  return App;

})();

$(function() {
  var app = new App(CONFIG);
});
