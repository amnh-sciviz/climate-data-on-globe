# -*- coding: utf-8 -*-

import csv
import gzip
import sys

def clamp(value, low=0.0, high=1.0):
    if low > high:
        tmp = low
        low = high
        high = tmp
    value = min(value, high)
    value = max(value, low)
    return value

def lerp(a, b, mu):
    return (b-a) * mu + a

def mean(data):
    n = len(data)
    if n < 1:
        return 0
    else:
        return 1.0 * sum(data) / n

def norm(value, a, b, clamp=True, wrap=False):
    n = 1.0 * (value - a) / (b - a)
    if clamp:
        n = min(n, 1)
        n = max(n, 0)
    if wrap and (n < 0 or n > 1.0):
        n = n % 1.0
    return n

def parseNumber(string):
    num = 0
    try:
        num = float(string)
        if "." not in string:
            num = int(string)
    except ValueError:
        num = False
        print "Value error: %s" % string
    if num <= -9999 or num >= 9999:
        print "Value unknown: %s" % string
        num = False
    return num

def readCSVData(filename):
    # print "Reading %s" % filename
    data = []
    with gzip.open(filename, 'rb') as f:
        for line in f:
            row = [triple.split(":") for triple in line.split(",")]
            for i, triple in enumerate(row):
                triple[0] = parseNumber(triple[0])
                triple[1] = parseNumber(triple[1])
                triple[2] = parseNumber(triple[2])
                row[i] = tuple(triple)
            data.append(row)
    # print "Done reading %s" % filename
    return data

def uvDataAt(lon, lat, data):
    us = []
    vs = []
    ts = []
    for d in data:
        triple = d[lat][lon]
        u = triple[0]
        v = triple[1]
        t = triple[2]
        if u is not False and v is not False:
            us.append(u)
            vs.append(v)
        if t is not False:
            ts.append(t)
    return (mean(us), mean(vs), mean(ts))
