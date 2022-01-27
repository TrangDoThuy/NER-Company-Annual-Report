from random import random
from random import seed
import colorsys

seed(1)

def getRandomColor(): 
    N = 18
    HSV_tuples = [(x * 1.0 / N, 0.5, 0.8) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    print(hex_out)
    return hex_out

getRandomColor()
