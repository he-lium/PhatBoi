#!/usr/bin/python
'''
ENGG1000 Engineering Design and Innovation
Robot Sumo Tester
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


# Connect motors
right_motor = LargeMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_D)

# Connect sensors
#us = UltrasonicSensor()
#gyro = GyroSensor()

#assert gyro.connected

#gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
#gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle
btn = Button()		# We will need to check EV3 buttons state.
#while not btn.any()
#    sleep(0.1)

right_motor.run_direct(duty_cycle_sp=-75)
left_motor.run_direct(duty_cycle_sp=-75)
counter = 5
# Run for 5 seconds or until button press
while counter > 0 or not btn.any():
    counter -= 1
    sleep(0.5)

# Stop the motors
left_motor.stop()
right_motor.stop()
