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
us = ds.variables['u'][:]
vs = ds.variables['v'][:]
depth = 0

timeCount = len(us) # this should be 72
lats = len(us[0][depth]) # this should be 1201
lngs = len(us[0][depth][0]) # this should be 481
print "%s measurements found with %s degrees (lng) by %s degrees (lat)" % (timeCount, lngs, lats)

def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return 1.0 * sum(data) / n

def uvDataAt(month, lng, lat, udata, vdata):
    depth = 0
    tLen = len(udata)
    mus = []
    mvs = []
    for t in range(tLen):
        tmonth = int(round(1.0 * t / (tLen-1) * 11.0))
        if tmonth == month:
            # retrieve velocity
            u = udata[t][depth][lat][lng]
            v = vdata[t][depth][lat][lng]
            if np.isnan(u) or u is ma.masked or np.isnan(v) or v is ma.masked:
                continue
            mus.append(u)
            mvs.append(u)
    u = mean(mus)
    v = mean(mvs)
    return (u, v)

print "Target particles: %s" % PARTICLES
data = []

# go through each time interval
for month in range(12):

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
                u, v = uvDataAt(month, lng, lat, us, vs)

                # particle is standing still
                if u == 0 and v == 0:
                    break

                # move particle based on velocity
                x += int(round(u * VELOCITY_MULTIPLIER))
                y += int(round(v * VELOCITY_MULTIPLIER))

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
    sys.stdout.write("%s%%" % round(1.0*month/11*100,1))
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
