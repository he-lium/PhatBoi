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
US_THRESHOLD = 600
FORWARD = 0
TURN_RIGHT = 1
TURN_LEFT = 2

# Connect motors
right_motor = LargeMotor(OUTPUT_B)
left_motor = LargeMotor(OUTPUT_C)
assert right_motor.connected
assert left_motor.connected
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


def run_motors(left, right):
    left_motor.run_direct(duty_cycle_sp=left * -1)
    right_motor.run_direct(duty_cycle_sp=right * -1)


def reverse():
    run_motors(-35, -35)
    time.sleep(0.5)
    stop()
    time.sleep(0.4)


def stop():
    left_motor.stop(stop_command='brake')
    right_motor.stop(stop_command='brake')


def path_on_left():
    return us.value() > US_THRESHOLD


def obstacle_ahead():
    return push.value() == 1


def red_obstacle():
    return color.value() == 5


class RunMotors(threading.Thread):
    def __init__(self, task):
        threading.Thread.__init__(self)
        self.task = task
        # self.bearing = gyro.value()
        self.adjust = 0
        self.interrupt = False
        self.new_path = False

    def run(self):
        gyro.mode = 'GYRO-RATE'
        gyro.mode = 'GYRO-ANG'  # Reset gyro
        if self.task == FORWARD:  # running straight
            run_motors(50, 50)
            while not self.interrupt:
                if not (self.new_path or path_on_left()):
                    self.new_path = True
                time.sleep(0.1)
                # add adjustment code
        else:
            if self.task == TURN_RIGHT:
                run_motors(40, -40)
            elif self.task == TURN_LEFT:
                run_motors(-40, 40)
            while abs(gyro.value()) < 85 and not self.interrupt:
                time.sleep(0.06)
            stop()

        stop()
        time.sleep(0.5)
        print gyro.value()

    def stop(self):
        self.interrupt = True


def main():
    fred = RunMotors(FORWARD)
    try:
        while True:
            fred.start()
            while fred.isAlive():
                time.sleep(0.1)
                if obstacle_ahead():
                    fred.stop()
                    fred.join()  # Wait for thread to stop
                    reverse()
                    fred = RunMotors(TURN_RIGHT) # Rotate clockwise
                    fred.start()
                    fred.join() # wait for turning to complete
                elif fred.new_path and path_on_left():
                    time.sleep(0.3) # Wait robot to be fully visible in path
                    fred.stop()
                    fred.join()
                    fred = RunMotors(TURN_LEFT)
                    fred.start()
                    fred.join()
            fred = RunMotors(FORWARD)

    except KeyboardInterrupt:
        if fred.isAlive():
            fred.stop()
            fred.join()

if __name__ == '__main__':
    main()