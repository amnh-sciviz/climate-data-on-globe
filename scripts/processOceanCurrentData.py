# -*- coding: utf-8 -*-

import json
import math
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
import sys

INPUT_FILE = "../data/downloaded/oscar_vel2016.nc" # Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_third-deg
OUTPUT_FILE = "../data/oscar_vel2016.json"
PARTICLES_PER_ROW = 60
PARTICLES_PER_COL = 24
PARTICLES = PARTICLES_PER_COL * PARTICLES_PER_ROW
POINTS_PER_PARTICLE = 10
WIDTH = 960
HEIGHT = 480
VELOCITY_MULTIPLIER = 1.0

ds = Dataset(INPUT_FILE, 'r')

# Extract data from NetCDF file
depth = 0
us = ds.variables['u'][:]
vs = ds.variables['v'][:]

timeCount = len(us) # this should be 72
lats = len(us[0][depth]) # this should be 1201
lngs = len(us[0][depth][0]) # this should be 481
print "%s measurements found with %s degrees (lng) by %s degrees (lat)" % (timeCount, lngs, lats)

print "Target particles: %s" % PARTICLES
data = []

# go through each time interval
for t in range(timeCount):

    particles = []

    # init particles
    for col in range(PARTICLES_PER_COL):
        for row in range(PARTICLES_PER_ROW):
            yp = 1.0 * col / (PARTICLES_PER_COL-1)
            xp = 1.0 * row / (PARTICLES_PER_ROW-1)
            lat = int(round(yp * (lats-1)))
            lng = int(round(xp * (lngs-1)))
            x = int(round(xp * (WIDTH-1)))
            y = int(round(yp * (HEIGHT-1)))
            i = y * WIDTH + x
            curve = [i]

            for j in range(POINTS_PER_PARTICLE):
                # retrieve velocity
                u = us[t][depth][lat][lng]
                v = vs[t][depth][lat][lng]
                if np.isnan(u) or u is ma.masked:
                    u = 0
                if np.isnan(v) or v is ma.masked:
                    v = 0

                # particle is standing still
                if u == 0 and v == 0:
                    break

                # move particle based on velocity
                x += u * VELOCITY_MULTIPLIER
                y += v * VELOCITY_MULTIPLIER

                # check for bounds
                if y < 0 or y >= HEIGHT:
                    break
                if x < 0:
                    x = WIDTH + x
                if x > WIDTH - 1:
                    x = x - (WIDTH-1)

                # add point to curve
                curve.append(y * WIDTH + x)

                # retrieve new lat/lng
                yp = 1.0 * y / (HEIGHT-1)
                xp = 1.0 * x / (WIDTH-1)
                lat = int(round(yp * (lats-1)))
                lng = int(round(xp * (lngs-1)))

            # only add curves that move
            if len(curve) > 1:
                particles.append(curve)

    print "Actual particles: %s" % len(particles)
    data.append(particles)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*t/(timeCount-1)*100,1))
    sys.stdout.flush()

jsonOut = {
    "yearInterval": timeCount,
    "lats": lats,
    "lngs": lngs,
    "width": WIDTH,
    "height": HEIGHT,
    "data": data
}

# Write to file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(jsonOut, f)
    print "Wrote %s items to %s" % (timeCount, OUTPUT_FILE)
