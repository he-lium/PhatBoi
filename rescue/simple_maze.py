#!/usr/bin/python
'''
ENGG1000 Engineering Design and Innovation
ev3 robot rescue - a cse project
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
right_motor = LargeMotor(OUTPUT_B); assert right_motor.connected
left_motor = LargeMotor(OUTPUT_C); assert left_motor.connected
#us_motor = MediumMotor(OUTPUT_B); assert us_motor.connected

# Connect sensors
us = UltrasonicSensor(); assert us.connected
gyro = GyroSensor(); #assert gyro.connected
color = ColorSensor(); assert color.connected
push = TouchSensor(); assert push.connected
btn = Button()

def run_motors(left, right):
    left_motor.run_direct(duty_cycle_sp=left)
    right_motor.run_direct(duty_cycle_sp=right)

def stop():
    # Stop both motors
	left_motor.stop(stop_command='brake')
    right_motor.stop(stop_command='brake')

path_on_left = lambda : us.value() > US_THRESHOLD
obstacle_ahead = lambda : push.value() == 1
red_head = lambda : color.value() == 5
color.mode = color.MODE_COL_COLOR
run_motors(60, 60)
while not btn.any():
    if obstacle_ahead():
        stop()
        time.sleep(0.3)
        if red_head:
            Sound.beep()
            time.sleep(0.3)
        break
    time.sleep(0.1)
stop()