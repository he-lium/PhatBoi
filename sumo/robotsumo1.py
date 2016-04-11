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
btn = Button()


def charge():
    right_motor.run_direct(duty_cycle_sp=-95)
    left_motor.run_direct(duty_cycle_sp=-95)

while not btn.any():
    sleep(0.1)



# Set starting point for front
us_motor.position = 0
# Run Ultrasonic motor
us_motor.run_direct(duty_cycle_sp=40)


detector_count = 0
first_detection_val = 0

# Move clockwise up to 120 degrees
while detector_count < 3 or us_motor.position < 120:
    if us.value() < US_THRESHOLD:
        if detector_count == 0:
            # Get first reading of degrees
            first_detection_val = us_motor.position
        detector_count += 1
        print "detected, position =", us_motor.position
    else:
        detector_count = 0
    sleep(0.05)

# Print position at 90 degrees
us_motor.stop()
sleep(0.5)
print first_detection_val
sleep(0.5)

# Try move back to start position
us_motor.run_direct(duty_cycle_sp=-30)
while us_motor.position > 0:
    sleep(0.05)

us_motor.stop()

# If not found on right, try find on anti-clockwise
if detector_count < 3:
    print "looking on left"
    sleep(0.3)
    us_motor.run_direct(duty_cycle_sp=-40)
    while detector_count < 3 or us_motor.position > -120:
        if us.value() < US_THRESHOLD:
            if detector_count == 0:
                # Get first reading of degrees
                first_detection_val = us_motor.position
            detector_count += 1
            print "detected, position =", us_motor.position
        else:
            detector_count = 0
        sleep(0.05)
    # move back to start position
    us_motor.run_direct(duty_cycle_sp=30)
    while us_motor.position < 0:
        sleep(0.05)


sleep(1)

gyro.mode = 'GYRO-RATE'	# Reset gyro and
gyro.mode = 'GYRO-ANG'	# Set to return compass angle

# Spin wheels
if first_detection_val >= 0:
    right_motor.run_direct(duty_cycle_sp=-50)
    left_motor.run_direct(duty_cycle_sp=50)
else:
    right_motor.run_direct(duty_cycle_sp=50)
    left_motor.run_direct(duty_cycle_sp=-50)

while abs(gyro.value()) < abs(first_detection_val - 20):
    print gyro.value()
    sleep(0.05)

right_motor.stop()
left_motor.stop()

    charge()
while not btn.any():
    sleep(0.1)