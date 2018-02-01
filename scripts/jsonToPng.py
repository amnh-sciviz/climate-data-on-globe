# -*- coding: utf-8 -*-

# python jsonToPng.py -in ../data/ocean_currents/oscar_vel2016.json -meta ../data/ocean_currents/oscar_vel2016_meta.json -out ../data/ocean_currents/oscar_vel2016.png -range " -180,180;90,-90;0,2"

import argparse
import json
from lib import *
from PIL import Image
from pprint import pprint
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-in', dest="INPUT_FILE", default="../../data/atmosphere_wind/gfsanl_4_25000.json", help="Input JSON data file")
parser.add_argument('-rgb', dest="RGB", default="lon,lat,mag", help="Key to map to red, green, blue")
parser.add_argument('-range', dest="RANGE", default="-180,180;90,-90;208,239", help="Ranges for RGB values")
parser.add_argument('-dim', dest="DIM", default="intervals,particleCount,pointsPerParticle", help="Keys for dimension counts")
parser.add_argument('-meta', dest="OUTPUT_META_FILE", default="../../data/atmosphere_wind/gfsanl_4_25000_meta.json", help="Output meta JSON file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/atmosphere_wind/gfsanl_4_25000.png", help="Output PNG file")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
RGB = args.RGB.strip().split(",")
DIM = args.DIM.strip().split(",")
RANGE = [r.split(",") for r in args.RANGE.strip().split(";")]
OUTPUT_META_FILE = args.OUTPUT_META_FILE
OUTPUT_FILE = args.OUTPUT_FILE

for i,r in enumerate(RANGE):
    RANGE[i] = (float(r[0]), float(r[1]))

data = {}
with open(INPUT_FILE) as f:
    data = json.load(f)
MULTIPLIER = float(data["multiplier"])

rData = data[RGB[0]]
gData = data[RGB[1]]
bData = data[RGB[2]]

rRange = RANGE[0]
gRange = RANGE[1]
bRange = RANGE[2]
dimCount = len(DIM)

if dimCount == 2:
    x = data[DIM[0]]
    y = data[DIM[1]]
    WIDTH = x
    HEIGHT = y

elif dimCount == 3:
    x = data[DIM[0]]
    y = data[DIM[1]]
    z = data[DIM[2]]
    WIDTH = x * z
    HEIGHT = y

else:
    print "You must have 2 or 3 dimensions of data"
    sys.exit(1)

# Create two blank image
PRECISION = 0.01
im = Image.new("RGB", (WIDTH, HEIGHT*2), (0, 0, 0))
pixels = im.load()
for row in range(HEIGHT):
    for col in range(WIDTH):
        index = row * WIDTH + col
        if dimCount == 3:
            i = int(col / z)
            j = row
            k = int(col % z)
            index = i * y * z + j * z + k
        r = norm(rData[index] * MULTIPLIER, rRange[0], rRange[1], clamp=False, wrap=True) # longitude should wrap around
        g = norm(gData[index] * MULTIPLIER, gRange[0], gRange[1])
        b = norm(bData[index] * MULTIPLIER, bRange[0], bRange[1])
        # store the decimal
        rd = r / PRECISION % 1.0
        gd = g / PRECISION % 1.0
        bd = b / PRECISION % 1.0
        # chop off decimal of rgb
        r = int(r / PRECISION) * PRECISION
        g = int(g / PRECISION) * PRECISION
        b = int(b / PRECISION) * PRECISION
        thisRow = row * 2
        pixels[col, thisRow] = (int(round(r * 255.0)), int(round(g * 255.0)), int(round(b * 255.0)))
        pixels[col, thisRow+1] = (int(round(rd * 255.0)), int(round(gd * 255.0)), int(round(bd * 255.0)))
im.save(OUTPUT_FILE)
print "Saved file %s" % OUTPUT_FILE

meta = {}
for dim in DIM:
    meta[dim] = data[dim]
with open(OUTPUT_META_FILE, 'w') as f:
    json.dump(meta, f)
    print "Wrote metadata to %s" % OUTPUT_META_FILE
