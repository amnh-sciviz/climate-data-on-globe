# -*- coding: utf-8 -*-

import argparse
import json
from lib import *
import math
from netCDF4 import Dataset
from PIL import Image, ImageDraw
from pprint import pprint
import sys

parser = argparse.ArgumentParser()
# Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_third-deg
# Doc: ftp://podaac-ftp.jpl.nasa.gov/allData/oscar/preview/L4/oscar_third_deg/docs/oscarthirdguide.pdf
parser.add_argument('-in', dest="INPUT_FILE", default="../data/downloaded/oscar_vel2016.nc", help="Input NetCDF data file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../data/oscar_vel2016.json", help="Output json file")
parser.add_argument('-ppr', dest="PARTICLES_PER_ROW", type=int, default=120, help="Particles per row")
parser.add_argument('-ppc', dest="PARTICLES_PER_COL", type=int, default=60, help="Particles per col")
parser.add_argument('-ppp', dest="POINTS_PER_PARTICLE", type=int, default=80, help="Points per particle")
parser.add_argument('-vel', dest="VELOCITY_MULTIPLIER", type=float, default=0.8, help="Velocity mulitplier")
parser.add_argument('-dt', dest="DISPLAY_PARTICLES", type=int, default=2000, help="Number of particles to display")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
PARTICLES_PER_ROW = args.PARTICLES_PER_ROW
PARTICLES_PER_COL = args.PARTICLES_PER_COL
POINTS_PER_PARTICLE = args.POINTS_PER_PARTICLE
VELOCITY_MULTIPLIER = args.VELOCITY_MULTIPLIER
DISPLAY_PARTICLES = args.DISPLAY_PARTICLES

PARTICLES = PARTICLES_PER_COL * PARTICLES_PER_ROW
LAT_RANGE = (80, -80) # latitude is represented from -80° to 80° with a 1/3° resolution
LNG_RANGE = (20, 420) # longitude is represented from  as 20° to 420°
LAT_RANGE_SAMPLE = LAT_RANGE
LNG_RANGE_SAMPLE = (40, 400)
PRECISION = 3

if PARTICLES < DISPLAY_PARTICLES:
    DISPLAY_PARTICLES = PARTICLES

ds = Dataset(INPUT_FILE, 'r')

# Extract data from NetCDF file
us = ds.variables['u'][:]
vs = ds.variables['v'][:]
depth = 0

timeCount = len(us) # this should be 72, i.e. ~5 day interval
lats = len(us[0][depth]) # this should be 1201
lngs = len(us[0][depth][0]) # this should be 481;
print "%s measurements found with %s degrees (lng) by %s degrees (lat)" % (timeCount, lngs, lats)

# draw month data
# im = Image.new("RGB", (lngs, lats), (0, 0, 0))
# pixels = im.load()
# for lat in range(lats):
#     for lng in range(lngs):
#         u, v = uvDataAt(0, lng, lat, us, vs)
#         mag = math.sqrt(u * u + v * v)
#         normal = clamp(mag / 2.0)
#         c = normal * 255.0
#         c = int(round(c))
#         pixels[lng, lat] = (c, c, c)
# im.save("monthData.png")

print "Target particles: %s" % PARTICLES
data = []

# go through each time interval
for month in range(12):

    print "Month %s" % (month+1)
    particles = []

    # u, v = uvDataAt(month, 799, 131, us, vs)
    # print "%s, %s" % (u, v)
    # sys.exit(1)

    # init particles
    for col in range(PARTICLES_PER_COL):
        for row in range(PARTICLES_PER_ROW):
            yp = 1.0 * col / (PARTICLES_PER_COL-1)
            xp = 1.0 * row / (PARTICLES_PER_ROW-1)
            lng = getLon(xp, LNG_RANGE_SAMPLE)
            lat = getLat(yp, LAT_RANGE_SAMPLE)
            lng = round(lng, PRECISION)
            lat = round(lat, PRECISION)
            coordinates = []
            cDistance = 0
            particleIndex = col * PARTICLES_PER_ROW + row

            for j in range(POINTS_PER_PARTICLE):
                xp = normLon(lng, LNG_RANGE)
                yp = normLat(lat, LAT_RANGE)
                ui = int(round(xp * (lngs-1)))
                vi = int(round(yp * (lats-1)))
                u, v = uvDataAt(month, ui, vi, us, vs)
                mag = math.sqrt(u * u + v * v)

                # add point
                coordinates.append((lng, lat, mag))

                # particle is standing still
                # if u == 0 and v == 0:
                #     break

                # move particle based on velocity
                lng += u * VELOCITY_MULTIPLIER
                lat += (-1.0 * v) * VELOCITY_MULTIPLIER

                # if lng < -180 or lng > 180:
                #     break
                # if lat < LAT_RANGE[0] or lat > LAT_RANGE[1]:
                #     break
                lat = clamp(lat, LAT_RANGE[0], LAT_RANGE[1])

                # keep track of distance for the first month
                if mag > 0 and month <= 0 and j > 0:
                    cDistance += distance(coordinates[j-1], (lng, lat))

            particles.append({
                "index": particleIndex,
                "points": coordinates,
                "distance": cDistance
            })

            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*particleIndex/PARTICLES*100,1))
            sys.stdout.flush()

    # for the first month, pick the longest paths and slice
    if month <= 0:
        pLen = len(particles)
        particles = sorted(particles, key=lambda k: k['distance'], reverse=True)
        addParticles = particles[:DISPLAY_PARTICLES]
        print "Actual particles: %s" % pLen
        print "Display particles: %s" % DISPLAY_PARTICLES
    # for subsequent months, pick particles based on the longest path from the first month
    else:
        baseParticles = data[0]
        addParticles = []
        for p in baseParticles:
            index = p["index"]
            addParticles.append(particles[index])
    data.append(addParticles)

    # Draw sample image
    # WIDTH = 1200
    # HEIGHT = 600
    # im = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    # draw = ImageDraw.Draw(im)
    # for particle in addParticles:
    #     coordinates = particle["points"]
    #     curve = [(norm(c[0], -180, 180, clamp=False) * WIDTH, norm(c[1], -90, 90, clamp=False) * HEIGHT) for c in coordinates]
    #     draw.line(curve, fill=255)
    # del draw
    # im.save("monthDraw.png", "PNG")
    # sys.exit(1)
    # break

# Flatten data to make file size as small as possible
intervalLen = len(data)
dataLen = intervalLen * DISPLAY_PARTICLES * POINTS_PER_PARTICLE
print "Flattening data with %s data points..." % dataLen
lonData = [0 for i in range(dataLen)]
latData = [0 for i in range(dataLen)]
magData = [0 for i in range(dataLen)]
for i, interval in enumerate(data):
    for j, particle in enumerate(interval):
        for k, point in enumerate(particle["points"]):
            index = i * DISPLAY_PARTICLES * POINTS_PER_PARTICLE + j * POINTS_PER_PARTICLE + k
            lonData[index] = int(point[0]*PRECISION)
            latData[index] = int(point[1]*PRECISION)
            magData[index] = int(point[2]*PRECISION)

jsonOut = {
    "intervals": intervalLen,
    "pointsPerParticle": POINTS_PER_PARTICLE,
    "particleCount": DISPLAY_PARTICLES,
    "multiplier": 1.0 / PRECISION,
    "lon": lonData,
    "lat": latData,
    "mag": magData
}

# Write to file
print "Writing data to file..."
with open(OUTPUT_FILE, 'w') as f:
    json.dump(jsonOut, f)
    print "Wrote data to %s" % OUTPUT_FILE
