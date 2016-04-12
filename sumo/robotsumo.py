#!/usr/bin/python
'''
ENGG1000 Engineering Design and Innovation
ev3 robot sumo - cse project
Written by:
Dominic He, Raycole Dai, Tristan Bagnulo,
Akshat Agarwal, Nikodemus Limanuel, Thomas George
'''

# Import System libraries
import sys, os, time, threading

# Look for additional libraries in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

# Ultrasonic detection threshold
US_THRESHOLD = 600

# Connect motors
right_motor = LargeMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_D)
us_motor = MediumMotor(OUTPUT_B)

# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()
btn = Button()

def stop():
    right_motor.stop(stop_command='brake')
    left_motor.stop(stop_command='brake')
    us_motor.stop()

def robotsumo():
    pass

# Wait for initial button input
while not btn.any():
    pass
robotsumo()
