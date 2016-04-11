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

US_THRESHOLD =700

# Connect motors
right_motor = LargeMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_D)
us_motor = MediumMotor(OUTPUT_B)

# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()

#gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
#gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle
btn = Button()		# We will need to check EV3 buttons state.

def charge():
    right_motor.run_direct(duty_cycle_sp=-95)
    left_motor.run_direct(duty_cycle_sp=-95)

# Spin robot
detector_count = 0
right_motor.run_direct(duty_cycle_sp=-80)
left_motor.run_direct(duty_cycle_sp=80)
while (detector_count < 5):
    sleep(0.05)
    if us.value() < US_THRESHOLD:
        detector_count += 1
    elif detector_count > 0:
        detector_count = 0
print us.value()

right_motor.stop()
left_motor.stop()
sleep(0.3)
charge()
while not btn.any():
    sleep(0.1)
