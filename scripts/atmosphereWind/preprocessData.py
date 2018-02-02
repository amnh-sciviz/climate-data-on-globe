# -*- coding: utf-8 -*-

# python preprocessData.py -in "../../data/atmosphere_wind/100000/gfsanl_4_%s_0000_000.csv.gz" -out "../../data/atmosphere_wind/gfsanl_4_100000_monthly.json"

import argparse
import datetime
import json
from lib import *
import math
import os
from PIL import Image, ImageDraw
from pprint import pprint
import sys

parser = argparse.ArgumentParser()
# Source: https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs
# Data: https://nomads.ncdc.noaa.gov/data/gfs4/201602/20160229/
# Doc: http://www.nco.ncep.noaa.gov/pmb/docs/on388/tableb.html#GRID4
    # 259920-point (720x361) global Lon/Lat grid. (1,1) at (0E, 90N); matrix layout; prime meridian not duplicated
parser.add_argument('-in', dest="INPUT_FILE", default="../../data/atmosphere_wind/25000/gfsanl_4_%s_0000_000.csv.gz", help="Input CSV files")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/atmosphere_wind/gfsanl_4_25000_monthly.json", help="Output json file")
parser.add_argument('-start', dest="DATE_START", default="2016-01-01", help="Date start")
parser.add_argument('-end', dest="DATE_END", default="2016-12-31", help="Date end")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE
DATE_START = [int(d) for d in args.DATE_START.split("-")]
DATE_END = [int(d) for d in args.DATE_END.split("-")]

# Read data
data = [[] for d in range(12)]
dateStart = datetime.date(DATE_START[0], DATE_START[1], DATE_START[2])
dateEnd = datetime.date(DATE_END[0], DATE_END[1], DATE_END[2])
date = dateStart

print "Reading data..."
i = 0
while date <= dateEnd:
    filename = INPUT_FILE % date.strftime("%Y%m%d")
    if os.path.isfile(filename):
        thisData = readCSVData(filename)
        monthIndex = date.month - 1
        data[monthIndex].append(thisData)
    date += datetime.timedelta(days=1)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*i/365.0*100,1))
    sys.stdout.flush()
    i += 1

lons = len(data[0][0][0])
lats = len(data[0][0])
total = lons * lats
print "Lons (%s) x Lats (%s)" % (lons, lats)

print "Calculating means..."

uData = []
vData = []
tData = []

for m in range(12):
    monthData = data[m]

    print "Month %s" % (m+1)
    monthUData = []
    monthVData = []
    monthTData = []

    for lat in range(lats):
        for lon in range(lons):
            u, v, t = uvDataAt(lon, lat, monthData)
            i = lat * lons + lon
            monthUData.append(u)
            monthVData.append(v)
            monthTData.append(t)
            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*i/total*100,1))
            sys.stdout.flush()

    uData.append(monthUData)
    vData.append(monthVData)
    tData.append(monthTData)

jsonOut = {
    "u": uData,
    "v": vData,
    "t": tData,
    "lons": lons,
    "lats": lats
}

# Write to file
print "Writing data to file..."
with open(OUTPUT_FILE, 'w') as f:
    json.dump(jsonOut, f)
    print "Wrote data to %s" % OUTPUT_FILE
