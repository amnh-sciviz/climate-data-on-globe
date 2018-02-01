# -*- coding: utf-8 -*-

# python gribjsonToCsv.py -in ../../data/atmosphere_wind/gfsanl_4_20160101_0000_000.json -out ../../data/atmosphere_wind/gfsanl_4_20160101_0000_000.json.csv

import argparse
import csv
import json
import math
import os
from pprint import pprint
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="path/to/file.json", help="Input file")
parser.add_argument('-level', dest="LEVEL", type=float, default=25000.0, help="Input file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="path/to/file.csv", help="Output file")
args = parser.parse_args()

print "Reading JSON..."
data = {}
with open(args.INPUT_FILE) as f:
    data = json.load(f)

tData = []
uData = []
vData = []
nx = 0
ny = 0

for d in data:
    info = d["header"]

    if info['surface1TypeName'] == 'Isobaric surface' and info['surface1Value'] == args.LEVEL:
        if info['parameterNumberName'] == 'U-component_of_wind':
            uData = d["data"]
            nx = info["nx"]
            ny = info["ny"]

        elif info['parameterNumberName'] == 'V-component_of_wind':
            vData = d["data"]

        elif info['parameterNumberName'] == 'Temperature':
            tData = d["data"]

if len(uData) == len(vData) and len(uData) == len(tData) and nx > 0 and ny > 0:

    # calculate wind speed
    rows = []
    for y in range(ny):
        row = []
        for x in range(nx):
            i = y * nx + x
            t = tData[i]
            u = uData[i]
            v = vData[i]
            row.append(":".join([str(t), str(u), str(v)]))
        rows.append(row)

    with open(args.OUTPUT_FILE, 'wb') as f:
        w = csv.writer(f, delimiter=',')
        w.writerows(rows)
        print "Successfully converted to %s" % args.OUTPUT_FILE

else:
    print "Could not find UV data for level"
