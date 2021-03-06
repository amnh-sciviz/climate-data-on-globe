# -*- coding: utf-8 -*-

import argparse
# from colormaps import *
import datetime
import json
from lib import *
import math
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import os
from PIL import Image, ImageDraw
from pprint import pprint
import random
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="../../data/atmosphere_wind/gfsanl_4_100000_monthly.json", help="Input json file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/atmosphere_wind/temperature/2016-%s.png", help="Output image file")
parser.add_argument('-grad', dest="GRADIENT_FILE", default="../../data/colorGradientRainbow.json", help="Color gradient json file")
parser.add_argument('-range', dest="RANGE", default="-20.0,40.0", help="Temperature range")
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

params = []

for month, monthData in enumerate(tData):
    params.append({
        "index": month,
        "fileOut": OUTPUT_FILE % str(month+1).zfill(2),
        "data": monthData,
        "height": HEIGHT,
        "width": WIDTH,
        "gradient": GRADIENT,
        "range": RANGE,
        "lats": lats,
        "lons": lons
    })

def processImage(p):
    fileOut = p["fileOut"]
    data = p["data"]
    width = p["width"]
    height = p["height"]
    gradient = p["gradient"]
    vRange = p["range"]
    lats = p["lats"]
    lons = p["lons"]

    print "Processing %s" % fileOut

    im = Image.new("RGB", (width, height), (0, 0, 0))
    pixels = im.load()

    for y in range(height):
        for x in range(width):
            lat = int(round((1.0 * y / (height-1)) * (lats-1)))
            lon = int(round((1.0 * x / (width-1)) * (lons-1)))
            index = lat * lons + lon
            t = data[index]
            n = norm(t, vRange[0], vRange[1])
            color = getColor(gradient, n)
            pixels[x, y] = color

    im.save(fileOut)
    print "Saved %s" % fileOut

print "Processing data..."
pool = ThreadPool()
pool.map(processImage, params)
pool.close()
pool.join()

print "Done."
