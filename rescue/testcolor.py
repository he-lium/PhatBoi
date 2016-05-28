#!/usr/bin/python
'''
ENGG1000 Engineering Design and Innovation
ev3 robot rescue - a cse project
Written by:
Dominic He, Raycole Dai, Tristan Bagnulo,
Akshat Agarwal, Nikodemus Limanuel, Thomas George
'''

# Import System libraries
import sys
import os
import time
import threading

# Look for additional libraries in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Import ev3dev library
from simple_maze import *

color.mode = color.MODE_RGB_RAW
run_motors(40, 40)
while True:
    time.sleep(1)
    r = color.value(0)
    g = color.value(1)
    b = color.value(2)
    print 'r', r, 'g', g, 'b', b