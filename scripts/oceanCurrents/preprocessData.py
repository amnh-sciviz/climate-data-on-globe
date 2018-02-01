# -*- coding: utf-8 -*-

import argparse
import json
from lib import *
import math
from netCDF4 import Dataset
import sys

parser = argparse.ArgumentParser()
# Source: https://podaac.jpl.nasa.gov/dataset/OSCAR_L4_OC_third-deg
# Doc: ftp://podaac-ftp.jpl.nasa.gov/allData/oscar/preview/L4/oscar_third_deg/docs/oscarthirdguide.pdf
parser.add_argument('-in', dest="INPUT_FILE", default="../../data/ocean_currents/oscar_vel2016.nc", help="Input NetCDF data file")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../../data/ocean_currents/oscar_vel2016_monthly.json", help="Output json file")

args = parser.parse_args()

INPUT_FILE = args.INPUT_FILE
OUTPUT_FILE = args.OUTPUT_FILE

ds = Dataset(INPUT_FILE, 'r')

# Extract data from NetCDF file
us = ds.variables['u'][:]
vs = ds.variables['v'][:]
depth = 0

timeCount = len(us) # this should be 72, i.e. ~5 day interval
lats = len(us[0][depth]) # this should be 481
lons = len(us[0][depth][0]) # this should be 1201;
total = lats * lons
print "%s measurements found with %s degrees (lng) by %s degrees (lat)" % (timeCount, lons, lats)

uData = []
vData = []

# go through each time interval
for month in range(12):

    print "Month %s" % (month+1)
    monthUData = []
    monthVData = []

    for lat in range(lats):
        for lon in range(lons):
            u, v = uvDataAt(month, lon, lat, us, vs)
            i = lat * lons + lon
            monthUData.append(u)
            monthVData.append(v)
            sys.stdout.write('\r')
            sys.stdout.write("%s%%" % round(1.0*i/total*100,1))
            sys.stdout.flush()

    uData.append(monthUData)
    vData.append(monthVData)

jsonOut = {
    "u": uData,
    "v": vData,
    "lats": lats,
    "lons": lons
}

# Write to file
print "Writing data to file..."
with open(OUTPUT_FILE, 'w') as f:
    json.dump(jsonOut, f)
    print "Wrote data to %s" % OUTPUT_FILE
