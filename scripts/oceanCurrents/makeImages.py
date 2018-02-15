# -*- coding: utf-8 -*-

import argparse
# from colormaps import *
import csv
import datetime
import gzip
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
parser.add_argument('-in', dest="INPUT_FILE", default="../../data/sea_surface_temperature/MYD28M_2016-%s.CSV.gz", help="Input CSV files")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/ocean_currents/temperature/2016-%s.png", help="Output image file")
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

GRADIENT = []
with open(GRADIENT_FILE) as f:
    GRADIENT = json.load(f)

params = []
for month in range(12):
    params.append({
        "index": month,
        "fileIn": INPUT_FILE % str(month+1).zfill(2),
        "fileOut": OUTPUT_FILE % str(month+1).zfill(2),
        "height": HEIGHT,
        "width": WIDTH,
        "gradient": GRADIENT,
        "range": RANGE
    })

def fileToImage(p):
    fileIn = p["fileIn"]
    fileOut = p["fileOut"]
    width = p["width"]
    height = p["height"]
    gradient = p["gradient"]
    vRange = p["range"]

    print "Processing %s" % fileIn
    rows = []
    with gzip.open(fileIn, 'rb') as f:
        for line in f:
            row = [float(value) for value in line.split(",")]
            rows.append(row)

    lats = len(rows)
    lons = len(rows[0])
    im = Image.new("RGB", (width, height), (0, 0, 0))
    pixels = im.load()

    for y in range(height):
        for x in range(width):
            lat = int(round((1.0 * y / (height-1)) * (lats-1)))
            lon = int(round((1.0 * x / (width-1)) * (lons-1)))
            t = rows[lat][lon]

            if t < 99999:
                n = norm(t, vRange[0], vRange[1])
                color = getColor(gradient, n)
                pixels[x, y] = color

    im.save(fileOut)
    print "Saved %s" % fileOut

print "Processing data..."
pool = ThreadPool()
pool.map(fileToImage, params)
pool.close()
pool.join()

print "Done."
