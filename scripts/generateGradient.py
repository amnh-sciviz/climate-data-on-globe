# -*- coding: utf-8 -*-

import argparse
import json
from pprint import pprint
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-grad', dest="GRADIENT", default="#42a6ff,#5994af,#9e944f,#c17700,#fc0000", help="Color gradient")
parser.add_argument('-width', dest="STEPS", type=int, default=100, help="Steps in gradient")
parser.add_argument('-out', dest="OUTPUT_FILE", default="../data/colorGradientRainbow.json", help="Output JSON file")

args = parser.parse_args()

def getColor(grad, amount):
    gradLen = len(grad)
    i = (gradLen-1) * amount
    remainder = i % 1
    rgb = (0,0,0)
    if remainder > 0:
        rgb = lerpColor(grad[int(i)], grad[int(i)+1], remainder)
    else:
        rgb = grad[int(i)]
    return rgb

# Add colors
def hex2rgb(hex):
  # "#FFFFFF" -> [1,1,1]
  return [round(int(hex[i:i+2], 16)/255.0, 6) for i in range(1,6,2)]

def lerp(a, b, amount):
    return (b-a) * amount + a

def lerpColor(s, f, amount):
    rgb = [
      round(s[j] + amount * (f[j]-s[j]), 6)
      for j in range(3)
    ]
    return rgb

GRADIENT = args.GRADIENT.split(",")
STEPS = args.STEPS

GRADIENT = [hex2rgb(g) for g in GRADIENT]

grad = []

for i in range(STEPS):
    mu = 1.0 * i / (STEPS-1)
    grad.append(getColor(GRADIENT, mu))

# pprint(grad)

# Write to file
print "Writing data to file..."
with open(args.OUTPUT_FILE, 'w') as f:
    json.dump(grad, f)
    print "Wrote data to %s" % args.OUTPUT_FILE
