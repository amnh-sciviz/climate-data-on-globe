# -*- coding: utf-8 -*-

import argparse
# from colormaps import *
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
parser.add_argument('-in', dest="INPUT_FILE", default="../../data/atmosphere_wind/gfsanl_4_100000_monthly.json", help="Input json file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/atmosphere_wind/temperature/2016-%s.png", help="Output image file")
parser.add_argument('-grad', dest="GRADIENT_FILE", default="../../data/colorGradientAnomaly.json", help="Color gradient json file")
parser.add_argument('-range', dest="RANGE", default="-35.0,40.0", help="Temperature range")
parser.add_argument('-width', dest="WIDTH", type=int, default=1024, help="Target image width")
parser.add_argument('-height', dest="HEIGHT", type=int, default=512, help="Target image height")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
GRADIENT_FILE = args.GRADIENT_FILE
RANGE = [float(d) for d in args.RANGE.split(",")]
WIDTH = args.WIDTH
HEIGHT = args.HEIGHT

data = []
print "Reading JSON file..."
with open(INPUT_FILE) as f:
    data = json.load(f)
tData = data["t"]
lats = int(data["lats"])
lons = int(data["lons"])
total = lons * lats
totalPixels = WIDTH * HEIGHT

GRADIENT = []
with open(GRADIENT_FILE) as f:
    GRADIENT = json.load(f)

print "%s degrees (lon) by %s degrees (lat) = %s (total)" % (lons, lats, total)

mint = 999
maxt = -999
ts = []

for month, monthData in enumerate(tData):
    filename = OUTPUT_FILE % str(month+1).zfill(2)
    print "Processing %s" % filename

    im = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    pixels = im.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            lat = int(round((1.0 * y / (HEIGHT-1)) * (lats-1)))
            lon = int(round((1.0 * x / (WIDTH-1)) * (lons-1)))
            index = lat * lons + lon
            t = monthData[index]
            if t > maxt:
                maxt = t
            if t < mint:
                mint = t
            ts.append(t)
            n = norm(t, RANGE[0], RANGE[1])
            color = getColor(GRADIENT, n)
            pixels[x, y] = color

            i = y * WIDTH + x
            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*i/totalPixels*100,1))
            sys.stdout.flush()

    im.save(filename)

print "Range: %s, %s" % (mint, maxt)
print "Mean: %s" % mean(ts)
