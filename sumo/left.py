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

def charge():
    # TODO More intelligent robot? e.g. Live Tracking
    right_motor.run_direct(duty_cycle_sp=-100)
    left_motor.run_direct(duty_cycle_sp=-100)
    while not btn.any():
        time.sleep(0.1)

def stop():
    right_motor.stop(stop_command='brake')
    left_motor.stop(stop_command='brake')
    us_motor.stop()

def play(opponent_initial):
    # Rotate robot to position
    gyro.mode = 'GYRO-RATE'  # Reset gyro and
    gyro.mode = 'GYRO-ANG'  # Set to return compass angle
    # Spin wheels to rotate robot to opponent
    if opponent_initial >= 0:
        right_motor.run_direct(duty_cycle_sp=-95)
        left_motor.run_direct(duty_cycle_sp=95)
    else:
        right_motor.run_direct(duty_cycle_sp=95)
        left_motor.run_direct(duty_cycle_sp=-95)
    while abs(gyro.value()) < abs(opponent_initial) - 45: # compensating 40 in or out of brace?
        time.sleep(0.01)
    Sound.beep()
    right_motor.stop(stop_command='brake')
    left_motor.stop(stop_command='brake')
    print gyro.value()
    charge()
    stop()
    pass


def robotsumo(right=True):
    # Set 3 second timer
    t = time.time()
    time.sleep(0.7)
    # Set starting point for front
    us_motor.position = 0
    # Run Ultrasonic motor
    if right:
        us_motor.run_direct(duty_cycle_sp=35)
    else:
        us_motor.run_direct(duty_cycle_sp=-35)

    detector_count = 0
    first_detection_val = 0

    if right:
        pass
    else:
        # Move anticlockwise(left) up to 180 degrees
        # Until ultrasonic gets two consecutive readings below threshold
        while detector_count < 2 and us_motor.position > -180:
            if us.value() < US_THRESHOLD:
                if detector_count == 0:
                    # Get first reading of degrees
                    first_detection_val = us_motor.position
                detector_count += 1
                print "detected, position =", us_motor.position, us.value()
            else:
                detector_count = 0
            time.sleep(0.05)

        us_motor.stop(stop_command='brake')
        print first_detection_val
        # Move back into start position
        us_motor.run_direct(duty_cycle_sp=35)
        while us_motor.position < 0:
            time.sleep(0.05)
        us_motor.stop(stop_command='brake')

    # Wait for the remaining 3 seconds
    while time.time() - t < 3:
        time.sleep(0.01)

    # Get to work!
    play(first_detection_val)


right = True
# System argument to search for left?
if len(sys.argv) == 2 and sys.argv[1] == 'l':
    right = False
Sound.beep()
# Wait for initial button input
while not btn.any():
    pass
robotsumo(right=0)
