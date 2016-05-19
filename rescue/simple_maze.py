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
color.mode = color.MODE_COL_COLOR

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


rotate_offset = 0

class RunMotors(threading.Thread):
    def __init__(self, task, offset=0):
        threading.Thread.__init__(self)
        self.task = task
        self.adjust = 0
        self.interrupt = False
        self.new_path = False
        self.running_straight = True
        self.offset = offset

    def run(self):
        global rotate_offset
        directions = []
        gyro.mode = 'GYRO-RATE'
        gyro.mode = 'GYRO-ANG'  # Reset gyro
        if self.task == FORWARD:  # running straight
            run_motors(50, 50)
            while not self.interrupt:
                if not (self.new_path or path_on_left()):
                    time.sleep(0.3)
                    self.new_path = True
                    print "new wall on left", us.value()
                time.sleep(0.1)
                # add adjustment code
                if self.running_straight:
                    if gyro.value() + self.offset >= 3:
                        self.running_straight = False
                        run_motors(45, 60)
                        print "robot on right: adjusting left"
                    elif gyro.value() + self.offset <= -3:
                        self.running_straight = False
                        run_motors(60, 45)
                        print "robot on left: adjusting right"
                elif abs(gyro.value() + self.offset) < 3:
                    run_motors(50, 50)
                    self.running_straight = True
                    print "robot nominal"
            rotate_offset += gyro.value()

        else:
            #new_offset = 0
            if self.task == TURN_RIGHT:
                run_motors(30, -30)
                directions.append['right']
            elif self.task == TURN_LEFT:
                run_motors(-30, 30)
                directions.append['left']
            
            while abs(gyro.value() + self.offset) < 85 and not self.interrupt:
                time.sleep(0.06)
            stop()
            if self.task == TURN_RIGHT:
                rotate_offset = gyro.value() + self.offset - 90
            elif self.task == TURN_LEFT:
                rotate_offset = gyro.value() + self.offset + 90
        stop()
        time.sleep(0.5)
        print gyro.value()

    def stop(self):
        self.interrupt = True


def main():
    #Sound.beep()
    #while not btn.any():
    #    time.sleep(0.3)
    fred = RunMotors(FORWARD)
    try:
        while True:
            fred.start()
            #os.system("start home/path of the file  )
            while fred.isAlive():
                time.sleep(0.1)
                if obstacle_ahead():
                    print "obstacle ahead"
                    fred.stop()
                    fred.join()  # Wait for thread to stop
                    # check if red
                    if red_obstacle():
                        Sound.beep()
                        time.sleep(0.5)
                        int pickedUp = TRUE
                        return
                    reverse()
                    if path_on_left():
                        fred = RunMotors(TURN_LEFT)
                    else:
                        fred = RunMotors(TURN_RIGHT)  # Rotate clockwise
                    fred.start()
                    while fred.isAlive():
                        time.sleep(0.1) # wait for turning to complete
                elif fred.new_path and path_on_left():
                    #Sound.beep()
                    print "new path on left: us=", us.value()
                    left_motor.position = 0
                    right_motor.position = 0
                    rotation_val = (left_motor.position + right_motor.position) / 2
                    while rotation_val > -360:  # Wait robot to be fully visible in path
                        time.sleep(0.1)
                        rotation_val = (left_motor.position + right_motor.position) / 2
                    fred.stop()
                    fred.join()
                    fred = RunMotors(TURN_LEFT)
                    fred.start()
                    while fred.isAlive():
                        time.sleep(0.1)
            fred = RunMotors(FORWARD, rotate_offset)

    except KeyboardInterrupt:
        #rotation_val = (left_motor.position + right_motor.position) / 2
        #print "rotation: ", rotation_val
        if fred.isAlive():
            fred.stop()
            fred.join()

if __name__ == '__main__':
    main()
    
    # if picked up = 1 , then look at revesred Directions[]
    # if 1st direction =
