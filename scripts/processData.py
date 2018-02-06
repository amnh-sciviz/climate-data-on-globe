# -*- coding: utf-8 -*-

# python processData.py -in ../data/ocean_currents/oscar_vel2016_monthly.json -out ../data/ocean_currents/oscar_vel2016.json -lon " 20,420" -lat " 80,-80" -lonsample " 40,400" -latsample " 80,-80" -vel 0.6 -rand 0 -ppr 120 -ppc 60

import argparse
import datetime
import json
from lib import *
import math
import os
from PIL import Image, ImageDraw
from pprint import pprint
import random
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="../data/atmosphere_wind/gfsanl_4_25000_monthly.json", help="Input CSV files")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../data/atmosphere_wind/gfsanl_4_25000.json", help="Output json file")
parser.add_argument('-lon', dest="LON_RANGE", default="0,360", help="Longitude range")
parser.add_argument('-lat', dest="LAT_RANGE", default="90,-90", help="Latitude range")
parser.add_argument('-lonsample', dest="LON_RANGE_SAMPLE", default="0,360", help="Longitude range")
parser.add_argument('-latsample', dest="LAT_RANGE_SAMPLE", default="90,-90", help="Latitude range")
parser.add_argument('-ppr', dest="PARTICLES_PER_ROW", type=int, default=240, help="Particles per row")
parser.add_argument('-ppc', dest="PARTICLES_PER_COL", type=int, default=120, help="Particles per col")
parser.add_argument('-ppp', dest="POINTS_PER_PARTICLE", type=int, default=100, help="Points per particle")
parser.add_argument('-vel', dest="VELOCITY_MULTIPLIER", type=float, default=0.03, help="Velocity mulitplier")
parser.add_argument('-dt', dest="DISPLAY_PARTICLES", type=int, default=2200, help="Number of particles to display")
parser.add_argument('-rand', dest="RANDOM", type=int, default=1, help="(1) if we should show random particles or (0) particles sorted by velocity")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
PARTICLES_PER_ROW = args.PARTICLES_PER_ROW
PARTICLES_PER_COL = args.PARTICLES_PER_COL
POINTS_PER_PARTICLE = args.POINTS_PER_PARTICLE
VELOCITY_MULTIPLIER = args.VELOCITY_MULTIPLIER
DISPLAY_PARTICLES = args.DISPLAY_PARTICLES
LON_RANGE = [float(d) for d in args.LON_RANGE.strip().split(",")]
LAT_RANGE = [float(d) for d in args.LAT_RANGE.strip().split(",")]
LON_RANGE_SAMPLE = [float(d) for d in args.LON_RANGE_SAMPLE.strip().split(",")]
LAT_RANGE_SAMPLE = [float(d) for d in args.LAT_RANGE_SAMPLE.strip().split(",")]
RANDOM = (args.RANDOM > 0)
PRECISION = 3
MAX_INCREMENT = 0.5

PARTICLES = PARTICLES_PER_COL * PARTICLES_PER_ROW

if PARTICLES < DISPLAY_PARTICLES:
    DISPLAY_PARTICLES = PARTICLES

data = []
print "Reading JSON file..."
with open(INPUT_FILE) as f:
    data = json.load(f)
uData = data["u"]
vData = data["v"]
lats = int(data["lats"])
lons = int(data["lons"])
total = lons * lats

print "%s degrees (lon) by %s degrees (lat) = %s (total)" % (lons, lats, total)

# draw month data
# im = Image.new("RGB", (lons, lats), (0, 0, 0))
# pixels = im.load()
# mmin = 999
# mmax = 0
# umin = 999
# umax = 0
# vmin = 999
# vmax = 0
# for lat in range(lats):
#     for lon in range(lons):
#         u, v = uvDataAt(0, lon, lat, uData, vData, lons, lats)
#         mag = math.sqrt(u * u + v * v)
#
#         if u > umax:
#             umax = u
#         if u < umin:
#             umin = u
#         if v > vmax:
#             vmax = v
#         if v < vmin:
#             vmin = v
#         if mag > mmax:
#             mmax = mag
#         if mag < mmin:
#             mmin = mag
#
#         # normal = norm(mag, 0, 3)
#         normal = norm(mag, 0, 70)
#         c = normal * 255.0
#         c = int(round(c))
#         pixels[lon, lat] = (c, c, c)
#
#         i = lat * lons + lon
#         sys.stdout.write('\r')
#         sys.stdout.write("%s%%" % round(1.0*i/total*100,1))
#         sys.stdout.flush()
# print "U range: [%s, %s]" % (umin, umax)
# print "V range: [%s, %s]" % (vmin, vmax)
# print "Mag range: [%s, %s]" % (mmin, mmax)
# im.save("monthData.png")
# sys.exit(1)

print "Target particles: %s" % PARTICLES
data = []

randomCols = [random.randint(0, PARTICLES_PER_COL-1) for col in range(PARTICLES_PER_COL)]
randomRows = [random.randint(0, PARTICLES_PER_ROW-1) for row in range(PARTICLES_PER_ROW)]
indices = []

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
            particleIndex = col * PARTICLES_PER_ROW + row
            if month > 0 and particleIndex not in indices:
                particles.append({})
                continue

            yp = 1.0 * col / (PARTICLES_PER_COL-1)
            xp = 1.0 * row / (PARTICLES_PER_ROW-1)
            lon = getLon(xp, LON_RANGE_SAMPLE)
            lat = getLat(yp, LAT_RANGE_SAMPLE)
            lon = round(lon, PRECISION)
            lat = round(lat, PRECISION)
            coordinates = []
            cDistance = 0

            for j in range(POINTS_PER_PARTICLE):
                xp = normLon(lon, LON_RANGE)
                yp = normLat(lat, LAT_RANGE)
                ui = int(round(xp * (lons-1)))
                vi = int(round(yp * (lats-1)))
                u, v = uvDataAt(month, ui, vi, uData, vData, lons, lats)
                mag = math.sqrt(u * u + v * v)

                # add point
                coordinates.append((lon, lat, mag))

                # particle is standing still
                # if u == 0 and v == 0:
                #     break

                addLon = u * VELOCITY_MULTIPLIER
                addLat = v * VELOCITY_MULTIPLIER

                addLon = clamp(addLon, -MAX_INCREMENT, MAX_INCREMENT)
                addLat = clamp(addLat, -MAX_INCREMENT, MAX_INCREMENT)

                # move particle based on velocity
                lon += addLon
                lat += addLat

                # if lon < -180 or lon > 180:
                #     break
                # if lat < LAT_RANGE[0] or lat > LAT_RANGE[1]:
                #     break
                lat = clamp(lat, LAT_RANGE[0], LAT_RANGE[1])

                # keep track of distance for the first month
                if mag > 0 and month <= 0 and j > 0:
                    cDistance += distance(coordinates[j-1], (lon, lat))

            particles.append({
                "index": particleIndex,
                "points": coordinates,
                "distance": cDistance
            })

            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*particleIndex/(PARTICLES-1)*100,1))
            sys.stdout.flush()

    # for the first month
    if month <= 0:
        # pick at random
        if RANDOM:
            addParticles = random.sample(particles, DISPLAY_PARTICLES)
        # otherwise, pick the longest paths and slice
        else:
            pLen = len(particles)
            particles = sorted(particles, key=lambda k: k['distance'], reverse=True)
            addParticles = particles[:DISPLAY_PARTICLES]
        indices = [p["index"] for p in addParticles]

    # for subsequent months, pick particles based on the first month
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
    # im = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    # draw = ImageDraw.Draw(im)
    # for particle in addParticles:
    #     coordinates = particle["points"]
    #     for i, point in enumerate(coordinates):
    #         if i > 0:
    #             prev = coordinates[i-1]
    #             p0 = (norm(prev[0], LON_RANGE_SAMPLE[0], LON_RANGE_SAMPLE[1], clamp=False) * WIDTH, norm(prev[1], LAT_RANGE_SAMPLE[0], LAT_RANGE_SAMPLE[1], clamp=False) * HEIGHT)
    #             p1 = (norm(point[0], LON_RANGE_SAMPLE[0], LON_RANGE_SAMPLE[1], clamp=False) * WIDTH, norm(point[1], LAT_RANGE_SAMPLE[0], LAT_RANGE_SAMPLE[1], clamp=False) * HEIGHT)
    #             alpha = int(round(norm(point[2], 0, 70) * 255))
    #             # alpha = int(round(norm(point[2], 0, 2) * 255))
    #             draw.line([p0, p1], fill=(255, 255, 255, alpha))
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
