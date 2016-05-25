#!/usr/bin/python
# This program is solely for testing if threads are the cause of the crashing
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
right_motor.position = 0
left_motor.position = 0
# Connect sensors
us = UltrasonicSensor()
gyro = GyroSensor()
color = ColorSensor()
push = TouchSensor()
btn = Button()


##################### THIS FILE IS TO CHECK IF THE THREADS ARE CAUSING THE CRASHING

class CheckUS(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.interrupt = True


    def run(self):
        try:
            while not self.interrupt:
                a = int(us.value())
                time.sleep(0.05)
        except:
            traceback.print_exc()

    def stop(self):
        self.interrupt = True


def main():
    t = CheckUS()
    try:
        t.start()
        while t.is_alive:
            b = int(us.value())
            time.sleep(0.1)
    except KeyboardInterrupt:
        traceback.print_exc()
        t.stop()
    finally:
        t.join()
