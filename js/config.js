var CONFIG = {
  "geojson": "data/countries_states.geojson",
  "yearMs": 120000,
  "calendar": {
    "marker": "#marker"
  },
  "globes": [
    {
      "el": '#ocean-currents',
      "data": "data/ocean_currents/oscar_vel2016.png",
      "meta": "data/ocean_currents/oscar_vel2016_meta.json",
      "viewAngle": 45,
      "near": 0.01,
      "far": 1000,
      "radius": 0.5,
      "minMag": 0.33,
      "precision": 0.01,
      "animationMs": 4000,
      "geojsonLineColor": 0x555555,
      "frames": [
        "data/ocean_currents/temperature/2016-01.png",
        "data/ocean_currents/temperature/2016-02.png",
        "data/ocean_currents/temperature/2016-03.png",
        "data/ocean_currents/temperature/2016-04.png",
        "data/ocean_currents/temperature/2016-05.png",
        "data/ocean_currents/temperature/2016-06.png",
        "data/ocean_currents/temperature/2016-07.png",
        "data/ocean_currents/temperature/2016-08.png",
        "data/ocean_currents/temperature/2016-09.png",
        "data/ocean_currents/temperature/2016-10.png",
        "data/ocean_currents/temperature/2016-11.png",
        "data/ocean_currents/temperature/2016-12.png"
      ]
    },{
      "el": '#atmosphere-wind',
      "data": "data/atmosphere_wind/gfsanl_4_25000.png",
      "meta": "data/atmosphere_wind/gfsanl_4_25000_meta.json",
      "viewAngle": 45,
      "near": 0.01,
      "far": 1000,
      "radius": 0.5,
      "minMag": 0.0,
      "precision": 0.01,
      "animationMs": 3000,
      "geojsonLineColor": 0xdddddd,
      "frames": [
        "data/atmosphere_wind/temperature/2016-01.png",
        "data/atmosphere_wind/temperature/2016-02.png",
        "data/atmosphere_wind/temperature/2016-03.png",
        "data/atmosphere_wind/temperature/2016-04.png",
        "data/atmosphere_wind/temperature/2016-05.png",
        "data/atmosphere_wind/temperature/2016-06.png",
        "data/atmosphere_wind/temperature/2016-07.png",
        "data/atmosphere_wind/temperature/2016-08.png",
        "data/atmosphere_wind/temperature/2016-09.png",
        "data/atmosphere_wind/temperature/2016-10.png",
        "data/atmosphere_wind/temperature/2016-11.png",
        "data/atmosphere_wind/temperature/2016-12.png"
      ]
    }
  ]
};
