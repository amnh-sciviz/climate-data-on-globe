import math
import numpy as np
import numpy.ma as ma

def clamp(value, low=0.0, high=1.0):
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
    if lon >= 360:
        lon = lon - 360
    elif lon < 0:
        lon = 360 + lon
    lon = lon - 180
    return lon

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

def normLat(lat, r):
    return norm(lat, r[0], r[1])

def normLon(lon, r):
    if lon < r[0]:
        lon += 360
    if lon > r[1]:
        lon -= 360
    return norm(lon, r[0], r[1], clamp=False, wrap=True)

def uvDataAt(month, lng, lat, udata, vdata):
    depth = 0
    tLen = len(udata)
    mus = []
    mvs = []
    for t in range(tLen):
        tmonth = int(round(1.0 * t / (tLen-1) * 11.0))
        if tmonth == month:
            # retrieve velocity
            u = udata[t][depth][lat][lng]
            v = vdata[t][depth][lat][lng]
            if not (np.isnan(u) or u is ma.masked or np.isnan(v) or v is ma.masked):
                mus.append(u)
                mvs.append(v)
    u = mean(mus)
    v = mean(mvs)
    return (u, v)
