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

path_stack = list()
rotate_offset = 0
us_value = 0
color_r = 0
color_g = 0
color_b = 0

class RunMotors(threading.Thread):
    def __init__(self, task, offset):
        threading.Thread.__init__(self)
        self.task = task
        self.interrupt = False
        self.new_path = False
        self.running_straight = True
        self.offset = offset
        self.error = False

    def run(self):
        self.start_time = time.time()
        global rotate_offset
        global us_value, color_r, color_g, color_b
        try:
            gyro.mode = 'GYRO-RATE'
            gyro.mode = 'GYRO-ANG'  # Reset gyro
            right_motor.position = 0
            left_motor.position = 0
            if self.task == FORWARD:  # running straight
                run_motors(50, 50)
                self.wall_time = time.time()
                previous_wall_dist = -1
                #os.system("start home/file.wav")
                #we need to add in the audio file and write in the location,
                #also i dont know if this is the right spot
                while not self.interrupt:
                    us_value = us.value()
                    if (not self.new_path) and (not us_value > US_THRESHOLD):
                        print "new wall on left, us=", us_value
                        time.sleep(0.1)
                        self.new_path = True
                        previous_wall_dist = us_value
                    time.sleep(0.1)
                    # N.B Comment out this section if crashes
                    if self.new_path and not us_value > US_THRESHOLD: # There's a wall on the left
                        if time.time() - self.wall_time > 0.5:
                            if us_value < 80: # If too close moving towards left wall
                                current_wall_dist = us_value
                                if current_wall_dist - previous_wall_dist < 0: # Converging with left wall
                                    print  "Too close to wall; veering right"
                                    self.wall_time = time.time()
                                    self.offset -= 8
                                    previous_wall_dist = current_wall_dist
                            elif us_value > 220: # If too far from left wall and moving away
                                current_wall_dist = us_value
                                if current_wall_dist - previous_wall_dist > 0: # Diverging from left wall
                                    print "Too far from wall; veering left"
                                    self.offset += 8
                                    self.wall_time = time.time()
                                    previous_wall_dist = current_wall_dist

                    # adjustment code for right angle
                    if self.running_straight:
                        if gyro.value() + self.offset >= 3:
                            self.running_straight = False
                            run_motors(40, 60)
                            #print "robot on right: adjusting left"
                        elif gyro.value() + self.offset <= -3:
                            self.running_straight = False
                            run_motors(60, 40)
                            #print "robot on left: adjusting right"
                    elif abs(gyro.value() + self.offset) < 3:
                        run_motors(50, 50)
                        self.running_straight = True
                        #print "robot nominal"
                rotate_offset += gyro.value()

            else:
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
        except:
            traceback.print_exc()
            self.error = True
            stop()
            return

    def stop(self):
        self.interrupt = True

def is_red():
    try:
        global color_r, color_g, color_b
        color_r = color.value(0)
        color_g = color.value(1)
        color_b = color.value(2)
        if color_r < 5:
            return False
        if color_g <=2 or color_b <= 2:
            return True
        if color_r > (color_g+color_b)/2:
            return True
        return False
    except:
        traceback.print_exc()
        return False

searchError = False

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

def search():
    fred = RunMotors(FORWARD, rotate_offset)
    try:
        while True:
            fred.start()
            while fred.isAlive():
                time.sleep(0.1)
                # check if red
                if is_red():
                    # Record the wheel distance, time taken and direction
                    path_stack.append((average_wheel_dist(), time.time() - fred.wall_time, "found"))
                    fred.stop()
                    fred.join()
                    Sound.beep()
                    time.sleep(0.5)
                    print path_stack
                    uturn()
                    return
                if fred.new_path and us_value > US_THRESHOLD:
                    print "new path on left: us=", us_value
                    path_stack.append((average_wheel_dist(), time.time() - fred.wall_time, "left"))
                    left_motor.position = 0
                    right_motor.position = 0
                    rotation_val = (left_motor.position + right_motor.position) / 2
                    while rotation_val > -360:  # Wait robot to be fully visible in path
                        time.sleep(0.1)
                        rotation_val = (left_motor.position + right_motor.position) / 2
                    fred.stop()
                    fred.join()
                    fred = RunMotors(TURN_LEFT, rotate_offset)
                    fred.start()
                    while fred.isAlive():
                        time.sleep(0.1)
                else:
                    if obstacle_ahead():
                        print "obstacle ahead"
                        fred.stop()
                        fred.join()  # Wait for thread to stop
                        print color_r, color_g, color_b
                        dist_travelled = average_wheel_dist()
                        reverse()
                        if us_value > US_THRESHOLD:
                            path_stack.append((dist_travelled, time.time() - fred.wall_time, "left"))
                            fred = RunMotors(TURN_LEFT, rotate_offset)
                        else:
                            path_stack.append((dist_travelled, time.time() - fred.wall_time, "right"))
                            fred = RunMotors(TURN_RIGHT, rotate_offset)  # Rotate clockwise
                        fred.start()
                        while fred.isAlive():
                            time.sleep(0.1) # wait for turning to complete
            if fred.error:
                searchError = True
                return
            fred = RunMotors(FORWARD, rotate_offset)
        if fred.isAlive():
            fred.stop()
            fred.join()
    except KeyboardInterrupt:
        if fred.isAlive():
            searchError = True
            fred.stop()
            fred.join()
            sys.exit()
    except:
        traceback.print_exc()
        searchError = True
        if fred.isAlive():
            fred.stop()
            fred.join()
            sys.exit()
    finally:
        print path_stack
        stop()


def rescue():
    global rotate_offset
    rotate_offset = 0
    return_thread = None
    try:
        while len(path_stack) > 0:
            # insert something here
            target_distance, target_time, direction = path_stack.pop()

            if direction == "left":
                # Turn right
                return_thread = RunMotors(TURN_RIGHT, rotate_offset)
                return_thread.start()
                while return_thread.isAlive():
                    time.sleep(0.1)
                time.sleep(0.5)
            elif direction == "right":
                # Turn left
                return_thread.start()
                while return_thread.isAlive():
                    time.sleep(0.1)
                time.sleep(0.5)
            #elif direction == "found":

            target_distance += 200

            # Go back pre-determined distance
            return_thread = RunMotors(FORWARD, rotate_offset)
            return_thread.start()
            while average_wheel_dist() < target_distance or target_time > 0:
                time.sleep(0.1)
                target_time -= 0.1
            return_thread.stop()
            return_thread.join()
    except KeyboardInterrupt:
        if return_thread != None and return_thread.isAlive():
            return_thread.stop()
            return_thread.join()
        sys.exit()
    except:
        traceback.print_exc()
        if return_thread != None and return_thread.isAlive():
            return_thread.stop()
            return_thread.join()
        sys.exit()
    finally:
        stop()


if __name__ == '__main__':
    search()
    if not searchError:
        rescue()
