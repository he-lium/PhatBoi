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
import sys, os, time
import threading

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

US_THRESHOLD = 600

# Connect motors
right_motor = LargeMotor(OUTPUT_A)
left_motor = LargeMotor(OUTPUT_D)
us_motor = MediumMotor(OUTPUT_B)

# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()
btn = Button()


def charge():
    right_motor.run_direct(duty_cycle_sp=-100)
    left_motor.run_direct(duty_cycle_sp=-100)

while not btn.any():
    pass
t = time.time()
#time.sleep(0.2)

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
    time.sleep(0.05)

# Print position
us_motor.stop(stop_command='brake')
time.sleep(0.3)
print first_detection_val

# Try move back to start position
us_motor.run_direct(duty_cycle_sp=-30)
while us_motor.position > 0:
    time.sleep(0.05)

us_motor.stop(stop_command='brake')

# If not found on right, try find on anti-clockwise
if detector_count < 3:
    print "looking on left"
    time.sleep(0.2)
    us_motor.run_direct(duty_cycle_sp=-40)
    while detector_count < 3 or us_motor.position > -120:
        if us.value() < US_THRESHOLD:
            if detector_count == 0:
                # Get first reading of degrees
                first_detection_val= us_motor.position
            detector_count += 1
            print "detected, position =", us_motor.position
        else:
            detector_count = 0
        time.sleep(0.05)
    # move back to start position
    us_motor.run_direct(duty_cycle_sp=30)
    while us_motor.position < 0:
        time.sleep(0.05)

while time.time() - t < 3:
    time.sleep(0.01)


gyro.mode = 'GYRO-RATE'	# Reset gyro and
gyro.mode = 'GYRO-ANG'	# Set to return compass angle


# Spin wheels
if first_detection_val >= 0:
    right_motor.run_direct(duty_cycle_sp=-95)
    left_motor.run_direct(duty_cycle_sp=95)
else:
    right_motor.run_direct(duty_cycle_sp=95)
    left_motor.run_direct(duty_cycle_sp=-95)

while abs(gyro.value()) < abs(first_detection_val - 30) and (us.value() > US_THRESHOLD):
    time.sleep(0.01)
Sound.beep()

right_motor.stop(stop_command='brake')
left_motor.stop(stop_command='brake')
charge()
while not btn.any():
    time.sleep(0.1)