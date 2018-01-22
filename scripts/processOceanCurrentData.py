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
parser.add_argument('-ppp', dest="POINTS_PER_PARTICLE", type=int, default=50, help="Points per particle")
parser.add_argument('-vel', dest="VELOCITY_MULTIPLIER", type=float, default=1.0, help="Velocity mulitplier")
parser.add_argument('-dt', dest="DISPLAY_THRESHOLD", type=float, default=0.333, help="Percentage of particles to show depending on curve distance")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
PARTICLES_PER_ROW = args.PARTICLES_PER_ROW
PARTICLES_PER_COL = args.PARTICLES_PER_COL
POINTS_PER_PARTICLE = args.POINTS_PER_PARTICLE
VELOCITY_MULTIPLIER = args.VELOCITY_MULTIPLIER
DISPLAY_THRESHOLD = args.DISPLAY_THRESHOLD

PARTICLES = PARTICLES_PER_COL * PARTICLES_PER_ROW
LAT_RANGE = (-80, 80) # latitude is represented from -80° to 80° with a 1/3° resolution
LNG_RANGE = (20, 420) # longitude is represented from  as 20° to 420°
PRECISION = 3

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
            lng = getLon(xp, LNG_RANGE)
            lat = getLat(yp, LAT_RANGE)
            lng = round(lng, PRECISION)
            lat = round(lat, PRECISION)
            coordinates = [(lng, lat)]
            cDistance = 0

            xp = normLon(lng, LNG_RANGE)
            yp = normLat(lat, LAT_RANGE)
            ui = int(round(xp * (lngs-1)))
            vi = int(round(yp * (lats-1)))

            for j in range(POINTS_PER_PARTICLE-1):
                # retrieve velocity
                u, v = uvDataAt(month, ui, vi, us, vs)

                # particle is standing still
                if u == 0 and v == 0:
                    break

                # move particle based on velocity
                # mag = math.sqrt(u * u + v * v)
                lng += u * VELOCITY_MULTIPLIER
                lat += (-1.0 * v) * VELOCITY_MULTIPLIER

                # if lng < -180 or lng > 180:
                #     break
                if lat < LAT_RANGE[0] or lat > LAT_RANGE[1]:
                    break

                # add point
                coordinates.append((lng, lat))
                cDistance += distance(coordinates[j], (lng, lat))

                # retrieve new lat/lng
                xp = normLon(lng, LNG_RANGE)
                yp = normLat(lat, LAT_RANGE)
                ui = int(round(xp * (lngs-1)))
                vi = int(round(yp * (lats-1)))

            # only add curves that move
            if len(coordinates) > POINTS_PER_PARTICLE * 0.99:
                particles.append({
                    "points": coordinates,
                    "distance": cDistance
                })

            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*(col * PARTICLES_PER_ROW + row)/PARTICLES*100,1))
            sys.stdout.flush()

    pLen = len(particles)
    particles = sorted(particles, key=lambda k: k['distance'], reverse=True)
    displayLen = int(round(pLen * DISPLAY_THRESHOLD))
    particles = particles[:displayLen]
    particles = [p["points"] for p in particles]

    print "Actual particles: %s" % pLen
    print "Display particles: %s" % displayLen
    data.append(particles)

    # Draw sample image
    # WIDTH = 1200
    # HEIGHT = 600
    # im = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    # draw = ImageDraw.Draw(im)
    # for coordinates in particles:
    #     curve = [(norm(c[0], -180, 180) * WIDTH, norm(c[1], -90, 90) * HEIGHT) for c in coordinates]
    #     draw.line(curve, fill=255)
    # del draw
    # im.save("monthDraw.png", "PNG")
    # sys.exit(1)
    # break

jsonOut = {
    "yearInterval": timeCount,
    "lats": lats,
    "lngs": lngs,
    "data": data
}

# Write to file
with open(OUTPUT_FILE, 'w') as f:
    json.dump(jsonOut, f)
    print "Wrote %s items to %s" % (timeCount, OUTPUT_FILE)
