#!/usr/bin/python
'''
ENGG1000 Engineering Design and Innovation
Robot Sumo
ev3 program to be the remaining robot left in the sumo ring
Written by:
Dominic He, Raycole Dai, Tristan Bagnulo,
Akshat Agarwal, Nikodemus Limanuel, Thomas George
'''

# Import system libraries
from time import sleep
import sys, os

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

# Connect motors
right_motor = LargeMotor(None) # TODO Find port
left_motor = LargeMotor(None)
us_motor = MediumMotor(None)

# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()

assert us.connected
assert gyro.connected

