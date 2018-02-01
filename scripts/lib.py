# -*- coding: utf-8 -*-

import math

def clamp(value, low=0.0, high=1.0):
    if low > high:
        tmp = low
        low = high
        high = tmp
    value = min(value, high)
    value = max(value, low)
    return value

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def getLat(mu, r):
    lat = lerp(r[0], r[1], mu)
    return lat

def getLon(mu, r):
    lon = lerp(r[0], r[1], mu)
    return lon

def lerp(a, b, mu):
    return (b-a) * mu + a

def norm(value, a, b, clamp=True, wrap=False):
    n = 1.0 * (value - a) / (b - a)
    if clamp:
        n = min(n, 1)
        n = max(n, 0)
    if wrap and (n < 0 or n > 1.0):
        n = n % 1.0
    return n

def normLat(lat, r):
    return norm(lat, r[0], r[1])

def normLon(lon, r):
    if lon < r[0]:
        lon += 360
    if lon > r[1]:
        lon -= 360
    return norm(lon, r[0], r[1], clamp=False, wrap=True)

def uvDataAt(month, lon, lat, udata, vdata, lons, lats):
    index = lons * lat + lon
    return (udata[month][index], vdata[month][index])
