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
US_THRESHOLD = 400
# RunMotors directions
FORWARD = 0
TURN_RIGHT = 1
TURN_LEFT = -1

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
ignore_left = True


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


def reset_gyro():
    gyro.mode = gyro.MODE_GYRO_RATE
    gyro.mode = gyro.MODE_GYRO_ANG

l_motor_pos = 0
r_motor_pos = 0

def average_wheel_dist():
    return (l_motor_pos + r_motor_pos) / -2

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
        global l_motor_pos, r_motor_pos
        try:
            reset_gyro()
            right_motor.position = 0
            left_motor.position = 0
            l_motor_pos = 0
            r_motor_pos = 0
            if self.task == FORWARD:  # running straight
                run_motors(50, 50)
                self.wall_time = time.time()
                previous_wall_dist = -1
                while not self.interrupt:
                    l_motor_pos = left_motor.position
                    r_motor_pos = right_motor.position
                    us_value = us.value()
                    if (not self.new_path) and (not us_value > US_THRESHOLD):
                        print "new wall on left, us=", us_value
                        time.sleep(0.1)
                        self.new_path = True
                        previous_wall_dist = us_value
                    time.sleep(0.1)
                    # N.B Comment out this section if crashes
                    if self.new_path and us_value < US_THRESHOLD: # There's a wall on the left
                        if time.time() - self.wall_time > 0.5:
                            if us_value < 100: # If too close moving towards left wall
                                current_wall_dist = us_value
                                if current_wall_dist - previous_wall_dist < 0: # Converging with left wall
                                    print  "\nToo close to wall; veering right"
                                    print "offset =", self.offset
                                    self.wall_time = time.time()
                                    self.offset -= 5
                                    previous_wall_dist = current_wall_dist
                            elif us_value > 180: # If too far from left wall and moving away
                                current_wall_dist = us_value
                                if current_wall_dist - previous_wall_dist > 0: # Diverging from left wall
                                    print "\nToo far from wall; veering left"
                                    print "offset =", self.offset
                                    self.offset += 3
                                    self.wall_time = time.time()
                                    previous_wall_dist = current_wall_dist

                    # adjustment code for right angle
                    gyro_value = gyro.value()
                    if gyro_value + self.offset >= 3:
                        self.running_straight = False
                        run_motors(45, 60)
                        print "robot on right: adjusting left"
                    elif gyro_value + self.offset <= -3:
                        self.running_straight = False
                        run_motors(60, 45)
                        print "robot on left: adjusting right"
                    elif abs(gyro_value + self.offset) < 3 and self.running_straight:
                        run_motors(50, 50)
                        self.running_straight = True
                        print "robot nominal"
                rotate_offset += gyro.value()

            else:
                if self.task == TURN_RIGHT:
                    print "-- turning right\n"
                    run_motors(40, -40)
                elif self.task == TURN_LEFT:
                    print "-- turning left\n"
                    run_motors(-40, 40)
                while abs(gyro.value()) < 85 and not self.interrupt:
                    time.sleep(0.06)
                stop()
                if self.task == TURN_RIGHT:
                    rotate_offset = gyro.value() + self.offset - 90
                elif self.task == TURN_LEFT:
                    rotate_offset = gyro.value() + self.offset + 90
                #rotate_offset = 0
            stop()
            time.sleep(0.5)
            print "offset =", rotate_offset
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
    reset_gyro()

    # Turn 180 degrees
    run_motors(-40, 40)
    while abs(gyro.value()) < 175:
        time.sleep(0.05)
    stop()
    time.sleep(0.3)

    # Open clamps
    move_clamp(1)
    time.sleep(0.7)
    clamp_motor.stop()
    time.sleep(0.2)

    # Slightly reverse into can
    run_motors(-30, -30)
    time.sleep(1.5)
    move_clamp(-1) # Close clamps
    time.sleep(1.2)
    stop()
    clamp_motor.run_direct(duty_cycle_sp=-95)
    time.sleep(0.5)

    run_motors(50, -50)
    time.sleep(0.1)
    stop()


def search():
    global searchError, path_stack, ignore_left
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
                    print "-------------- FOUND --------------------"
                    print "rgb", color_r, color_g, color_b
                    fred.stop()
                    fred.join()
                    Sound.beep()
                    time.sleep(0.5)
                    print path_stack
                    uturn()
                    return
                if fred.new_path and us_value > US_THRESHOLD and not ignore_left:
                    print "new path on left: us=", us_value
                    init_rotation_val = average_wheel_dist()
                    threshold_check = 0
                    false_alarm = False
                    while average_wheel_dist() - init_rotation_val < 360:  # Wait robot to be fully visible in path
                        time.sleep(0.1)
                        if threshold_check == 0.5 and us_value < US_THRESHOLD:
                            false_alarm = True
                    if not false_alarm and us_value > US_THRESHOLD: # Still path on left
                        fred.stop()
                        fred.join()
                        path_stack.append((average_wheel_dist() - 360, time.time() - fred.wall_time, TURN_LEFT))
                        fred = RunMotors(TURN_LEFT, rotate_offset)
                        fred.start()
                        while fred.isAlive():
                            time.sleep(0.1)
                    else:
                        print "***** false alarm, keep going", us_value
                else:
                    if obstacle_ahead() or color_b >= 60:
                        print "obstacle ahead"
                        fred.stop()
                        while fred.isAlive():
                            fred.new_path = False
                        dist_travelled = average_wheel_dist()
                        print color_r, color_g, color_b
                        reverse()
                        print color_r, color_g, color_b
                        if us_value > US_THRESHOLD:
                            if not ignore_left:
                                path_stack.append((dist_travelled, time.time() - fred.wall_time, TURN_LEFT))
                                fred = RunMotors(TURN_LEFT, rotate_offset)
                            else:
                                path_stack.append((dist_travelled, time.time() - fred.wall_time, TURN_RIGHT))
                                fred = RunMotors(TURN_RIGHT, rotate_offset)  # Rotate clockwise
                                ignore_left = False
                        else:
                            path_stack.append((dist_travelled, time.time() - fred.wall_time, TURN_RIGHT))
                            fred = RunMotors(TURN_RIGHT, rotate_offset)  # Rotate clockwise
                        fred.start()
                        while fred.isAlive():
                            time.sleep(0.1) # wait for turning to complete
            if fred.error:
                searchError = True
                return
            stack_len = len(path_stack)
            '''if stack_len >= 8 and stack_len % 2 == 0:
                # Detect that's in a loop
                net_sum = sum((n[3] for n in path_stack))
                print "net_sum =", net_sum
                if net_sum <= -8: # Loop on the left; anti-clockwise loop
                    loop1 = sum((x[3] for x in path_stack[0:stack_len/2]))
                    loop2 = sum((x[3] for x in path_stack[stack_len/2:]))
                    if loop1 == loop2: # We're in a loop
                        path_stack = list()
                        reset_gyro() # turn 180 degrees
                        run_motors(-40, 40)
                        while abs(gyro.value()) <= 175:
                            time.sleep()
                        stop()
                        time.sleep(0.4)
                if net_sum >= 8:
                    pass # TODO'''
            fred = RunMotors(FORWARD, rotate_offset)
        if fred.isAlive():
            fred.stop()
            fred.join()
    except KeyboardInterrupt:
        searchError = True
        if fred.isAlive():
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

# when returning, goes back along straight path if we
# hit the wall while turning right
def right_buffer():
    reverse()

    # turn left
    t = RunMotors(TURN_LEFT, rotate_offset)
    t.start()
    while t.isAlive():
        time.sleep(0.1)
    time.sleep(0.5)
    # Go forward 0.5 s
    t = RunMotors(FORWARD, rotate_offset)
    t.start()
    time.sleep(0.5)
    # Turn left
    t = RunMotors(TURN_RIGHT, rotate_offset)
    t.start()
    while t.isAlive():
        time.sleep(0.1)
    time.sleep(0.3)

def rescue():
    global rotate_offset
    rotate_offset = 0
    return_thread = None
    try:
        while len(path_stack) > 0:
            target_distance, target_time, direction = path_stack.pop()

            if direction == TURN_LEFT:
                # Turn right
                return_thread = RunMotors(TURN_RIGHT, rotate_offset)
                return_thread.start()
                while return_thread.isAlive():
                    time.sleep(0.1)
                time.sleep(0.5)
            elif direction == TURN_RIGHT:
                if us.value() < US_THRESHOLD: # If there still isn't a path on the left
                    return_thread = RunMotors(FORWARD, rotate_offset)
                    return_thread.start()
                    while us_value < US_THRESHOLD:
                        time.sleep(0.1)
                    return_thread.stop()
                    return_thread.join()
                # Turn left
                return_thread = RunMotors(TURN_LEFT, rotate_offset)
                return_thread.start()
                while return_thread.isAlive():
                    time.sleep(0.1)
                time.sleep(0.5)
            #elif direction == "found":
            if len(path_stack) >= 1:
                target_distance += 200

            # Go back pre-determined distance
            return_thread = RunMotors(FORWARD, rotate_offset)
            time_elapsed = 0
            return_thread.start()
            while average_wheel_dist() < target_distance or time_elapsed < target_time:
                if push.value() == 1:
                    return_thread.stop()
                    return_thread.join()
                    if average_wheel_dist() < 150:
                        right_buffer()
                        return_thread = RunMotors(FORWARD, rotate_offset)
                        time_elapsed = 0
                        return_thread.start()
                        continue
                    else:
                        break
                time.sleep(0.1)
                time_elapsed += 0.1

            return_thread.stop()
            return_thread.join()
        Sound.beep()
    except KeyboardInterrupt:
        if return_thread != None and return_thread.isAlive():
            return_thread.stop()
            return_thread.join()
        Sound.beep()
        sys.exit()
    except:
        traceback.print_exc()
        if return_thread != None and return_thread.isAlive():
            return_thread.stop()
            return_thread.join()
        sys.exit()
    finally:
        stop()

def release_clamps():
    move_clamp(1)
    time.sleep(1.5)

if __name__ == '__main__':
    search()
    if not searchError:
        rescue()
        release_clamps()
        time.sleep(2)
