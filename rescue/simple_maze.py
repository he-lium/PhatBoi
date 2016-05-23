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

def path_on_left():
    return us.value() > US_THRESHOLD


def obstacle_ahead():
    return push.value() == 1


rotate_offset = 0

class RunMotors(threading.Thread):
    def __init__(self, task, offset=0):
        threading.Thread.__init__(self)
        self.task = task
        self.interrupt = False
        self.new_path = False
        self.running_straight = True
        self.offset = offset
        self.wall_move = None


    def run(self):
        measure_prev = -1
        measure_time = -1.0
        global rotate_offset
        gyro.mode = 'GYRO-RATE'
        gyro.mode = 'GYRO-ANG'  # Reset gyro
        if self.task == FORWARD:  # running straight
            run_motors(50, 50)
            self.wall_time = time.time()
            #os.system("start home/file.wav") we need to add in the audio file and write in the location, also i dont know if this is the right spot
            while not self.interrupt:
                if (not self.new_path) and (not path_on_left()):
                    print "new wall on left", us.value()
                    time.sleep(0.3)
                    self.new_path = True
                    #measure_prev = us.value();
                    #measure_time = time.time();
                time.sleep(0.1)
                if self.new_path and not path_on_left(): # There's a wall on the left
                    if time.time() - self.wall_time > 1.3:
                        if us.value() < 80:
                            print  "Too close to wall; veering right"
                            self.wall_move = VEERING_RIGHT
                            self.wall_time = time.time()
                            self.offset -= 8
                        elif us.value() > 220:
                            print "Too far from wall; veering left"
                            self.offset += 8
                            self.wall_move = VEERING_LEFT
                            self.wall_time = time.time()
                # adjustment code for right angle
                if self.running_straight:
                    if gyro.value() + self.offset >= 3:
                        self.running_straight = False
                        run_motors(45, 60)
                        #print "robot on right: adjusting left"
                    elif gyro.value() + self.offset <= -3:
                        self.running_straight = False
                        run_motors(60, 45)
                        #print "robot on left: adjusting right"
                elif abs(gyro.value() + self.offset) < 3:
                    run_motors(50, 50)
                    self.running_straight = True
                    #print "robot nominal"
            rotate_offset += gyro.value()

        else:
            #new_offset = 0
            if self.task == TURN_RIGHT:
                run_motors(40, -40)
            elif self.task == TURN_LEFT:
                run_motors(-30, 30)
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

def is_red():
    r = color.value(0)
    g = color.value(1)
    b = color.value(2)
    if r < 5:
        return False
    if g <=2 or b <= 2:
        return True
    if r > (g+b)/2:
        return True
    return False

def uturn():
    reverse()
    gyro.mode = 'GYRO-RATE'
    gyro.mode = 'GYRO-ANG'  # Reset gyro
    run_motors(-40, 40)
    while abs(gyro.value()) < 175:
        time.sleep(0.05)
    stop()
    time.sleep(0.3)
    move_clamp(1)
    time.sleep(0.7)
    clamp_motor.stop()
    time.sleep(0.2)

    run_motors(-30, -30)
    time.sleep(1.5)
    move_clamp(-1)
    time.sleep(1.2)
    stop()
    clamp_motor.run_direct(duty_cycle_sp=-95)
    time.sleep(1)
    #stop_clamps()
    run_motors(50, 50)
    time.sleep(2)
    stop()
    time.sleep(0.5)
    run_motors(-50, 50)
    time.sleep(5)

def main():
    fred = RunMotors(FORWARD)
    try:
        while True:
            fred.start()
            while fred.isAlive():
                time.sleep(0.1)
                # check if red
                if is_red():
                    fred.stop()
                    fred.join()
                    Sound.beep()
                    time.sleep(0.5)

                    uturn()
                    return

                if obstacle_ahead():
                    print "obstacle ahead"
                    fred.stop()
                    fred.join()  # Wait for thread to stop

                    reverse()
                    if path_on_left():
                        fred = RunMotors(TURN_LEFT)
                    else:
                        fred = RunMotors(TURN_RIGHT)  # Rotate clockwise
                    fred.start()
                    while fred.isAlive():
                        time.sleep(0.1) # wait for turning to complete
                elif fred.new_path and path_on_left():
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
        if fred.isAlive():
            fred.stop()
            fred.join()
    except KeyboardInterrupt:
        if fred.isAlive():
            fred.stop()
            fred.join()
    except Exception, e:
        stop()
        print str(e)
        if fred.isAlive():
            fred.stop()
            fred.join()


if __name__ == '__main__':
    main()
