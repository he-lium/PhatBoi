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
import traceback

# Look for additional libraries in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Import ev3dev library
from ev3dev.auto import *

# Ultrasonic detection threshold
US_THRESHOLD = 450
FORWARD = 0
TURN_RIGHT = 1
TURN_LEFT = 2

# Wall adjustment modes
VEERING_RIGHT = 1
VEERING_LEFT = -1

# Connect motors
right_motor = LargeMotor(OUTPUT_C)
left_motor = LargeMotor(OUTPUT_D)
clamp_motor = MediumMotor(OUTPUT_B)
assert right_motor.connected
assert left_motor.connected
assert clamp_motor.connected
# Reset motor positions
right_motor.position = 0
left_motor.position = 0
# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()
color = ColorSensor()
push = TouchSensor()
btn = Button()
assert us.connected
assert gyro.connected
assert color.connected
assert push.connected
color.mode = color.MODE_RGB_RAW

path_stack = list()

def run_motors(left, right):
    left_motor.run_direct(duty_cycle_sp=left * -1)
    right_motor.run_direct(duty_cycle_sp=right * -1)


def move_clamp(direction):
    clamp_motor.run_direct(duty_cycle_sp=direction*60)


def reverse():
    run_motors(-35, -35)
    time.sleep(0.5)
    stop()
    time.sleep(0.4)


def stop():
    left_motor.stop(stop_command='brake')
    right_motor.stop(stop_command='brake')

def stop_clamps():
    clamp_motor.stop()


def obstacle_ahead():
    return push.value() == 1


def average_wheel_dist():
    return (left_motor.position + right_motor.position) / -2


def path_on_left():
    return us.value() < US_THRESHOLD


def is_red():
    r = color.value(0)
    g = color.value(1)
    b = color.value(2)
    if r < 5:
        return False
    if g <= 2 or b <= 2:
        return True
    if r > (g+b)/2:
        return True
    return False

wall_time = time.time()
prev_wall_dist = -1
running_straight = True

def go_forward(offset = 0):
    global wall_time, prev_wall_dist, running_straight

    # Account for if robot is moving towards side walls
    if not path_on_left() and time.time() - wall_time > 0.5:
        current_wall_dist = us.value()
        if us.value() < 80 and \
            current_wall_dist - prev_wall_dist < 0:
            print  "Too close to wall; veering right"
            wall_time = time.time()
            offset -= 5
            prev_wall_dist = current_wall_dist
        elif us.value() > 220 and \
            current_wall_dist + prev_wall_dist > 0:
            print "Too far from wall; veering left"
            wall_time = time.time()
            offset += 5
            prev_wall_dist = current_wall_dist

    # Adjustment code for going straight
    if running_straight:
        if gyro.value() + offset >= 3: # Robot too far to right
            running_straight = False
            run_motors(45, 60)
        elif gyro.value() + offset <= 3: # Robot too far to left
            running_straight = False
            run_motors(60, 45)
    elif abs(gyro.value() + offset) < 3: # Robot is running straight again
        run_motors(50, 50)
        running_straight = True

    return offset

def rotate(direction, offset=0):
    if direction == TURN_RIGHT:
        run_motors(40, -40)
    else:  # direction = TURN_LEFT
        run_motors(-40, 40)
    while abs(gyro.value() + offset) < 85:
        time.sleep(0.05)
    stop()
    if direction == TURN_RIGHT:
        offset += gyro.value() - 90
    else:
        offset += gyro.value() + 90
    time.sleep(0.5)
    return offset

def start_moving():
    # Reset all the things
    gyro.mode = gyro.MODE_GYRO_RATE
    gyro.mode = gyro.MODE_GYRO_ANG
    right_motor.position = 0
    left_motor.position = 0

def search():
    global prev_wall_dist, path_stack

    offset = 0
    new_path = False
    found = False
    run_motors(50, 50)

    while not found:
        time.sleep(0.1)
        if not new_path and not path_on_left():
            print "new wall on left, us=", us.value()
            time.sleep(0.3)
            new_path = True
            prev_wall_dist = us.value()
        offset = go_forward(offset)
        if is_red():
            stop()
            Sound.beep()
            return
        if new_path and path_on_left():
            print "new path on left: us=", us.value()
            path_stack = [(average_wheel_dist(), "left")] + path_stack

############### TBC