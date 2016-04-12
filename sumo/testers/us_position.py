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
import threading

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

US_THRESHOLD = 700

# Connect motors
right_motor = LargeMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_D)
us_motor = MediumMotor(OUTPUT_B)

# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()


# Set starting point for front
us_motor.position = 0
# Run Ultrasonic motor
us_motor.run_direct(duty_cycle_sp=40)


detector_count = 0
first_detection_val = 0

# Move clockwise
while detector_count < 3:
    if us.value() < US_THRESHOLD:
        if detector_count == 0:
            # Get first reading of degrees
            first_detection_val = us_motor.position
        detector_count += 1
        print "detected, position =", us_motor.position
    else:
        detector_count = 0
    sleep(0.05)

#while us_motor.position < 180:
#    sleep(0.05)

# Print position at 90 degrees
us_motor.stop()
sleep(0.5)
print first_detection_val
sleep(0.5)

us_motor.run_direct(duty_cycle_sp=-30)
# Try move back to start position
while us_motor.position > 0:
    sleep(0.05)

us_motor.stop()