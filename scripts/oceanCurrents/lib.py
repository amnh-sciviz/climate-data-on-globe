import math
import numpy as np
import numpy.ma as ma

def clamp(value, low=0.0, high=1.0):
    if low > high:
        tmp = low
        low = high
        high = tmp
    value = min(value, high)
    value = max(value, low)
    return value

def getColor(gradient, mu, start=0.0, end=1.0):
    gradientLen = len(gradient)
    start = int(round(start * gradientLen))
    end = int(round(end * gradientLen))
    gradient = gradient[start:end]

    index = int(round(mu * (gradientLen-1)))
    rgb = tuple([int(round(v*255.0)) for v in gradient[index]])
    return rgb

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
