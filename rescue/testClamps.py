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
from ev3dev.auto import *

# Ultrasonic detection threshold
US_THRESHOLD = 400
FORWARD = 0
TURN_RIGHT = 1
TURN_LEFT = 2

# Clamp
OPEN = -1
CLOSE = 1

# Connect motors
clamp_motor = MediumMotor(OUTPUT_A)
#right_motor = LargeMotor(OUTPUT_B)
#left_motor = LargeMotor(OUTPUT_C)
#assert right_motor.connected
#assert left_motor.connected
assert clamp_motor.connected
# Connect sensors
btn = Button()

def move_clamp(change):
    #change = -1 to open, change = 1 to close
    clamp_motor.run_direct(duty_cycle_sp=change*60)

def main():
    
    clampState = OPEN
    while True:
        if btn.any():
            if clampState == OPEN:
                move_clamp(CLOSE)
                clampState = CLOSE
                time.sleep(1)
            else:
                move_clamp(OPEN)
                clampState = OPEN
                time.sleep(1)

if __name__ == '__main__':
    main()
