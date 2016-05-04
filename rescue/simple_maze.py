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
gyro = GyroSensor(); assert gyro.connected
color = ColorSensor(); assert color.connected
push = TouchSensor(); assert push.connected
btn = Button()

def run_motors(left, right):
    left_motor.run_direct(duty_cycle_sp=left*-1)
    right_motor.run_direct(duty_cycle_sp=right*-1)

def stop():
    left_motor.stop(stop_command='brake')
    right_motor.stop(stop_command='brake')

path_on_left = lambda : us.value() > US_THRESHOLD
obstacle_ahead = lambda : push.value() == 1
red_head = lambda : color.value() == 5

# color.mode = color.MODE_COL_COLOR
# run_motors(40, 40)
# while not btn.any():
#     if obstacle_ahead():
#         stop()
#         time.sleep(0.3)
#         print color.value()
#         if red_head():
#             Sound.beep()
#             time.sleep(0.3)
#         break
#     time.sleep(0.1)
# stop()

class RunMotors(threading.Thread):
    def __init__(self, rotation):
        threading.Thread.__init__(self)
        self.rotation = rotation
        #self.bearing = gyro.value()
        self.adjust = 0
        self.interrupt = False
        self.new_path = False

    def run(self):
        gyro.mode = 'GYRO-RATE'
        gyro.mode = 'GYRO-ANG'  # Reset gyro
        if self.rotation == 0: # running straight
            run_motors(50, 50)
            while not self.interrupt:
                if not (self.new_path or path_on_left()):
                    self.new_path = True
                time.sleep(0.1)
                # add adjustment code
        else:
            if self.rotation == 1: # rotating right
                run_motors(40, -40)
            elif self.rotation == -1: # rotating left
                run_motors(-40, 40)
            while abs(gyro.value()) < 85 and not self.interrupt:
                    #print(gyro.value())
                    time.sleep(0.06)
            stop()
            time.sleep(1)
            print gyro.value()
        stop()
        time.sleep(0.5)

    def stop(self):
        self.interrupt = True

try:
    while True:
        fred = RunMotors(0)
        fred.start()
        while fred.isAlive():
            if obstacle_ahead():
                fred.stop()
                fred.join() # Stop thread, wait to join
                run_motors(-35, -35)
                time.sleep(0.5)
                stop()
                time.sleep(0.4)
                fred = RunMotors(1)
                fred.start()
                fred.join()


except KeyboardInterrupt:
    fred.stop()
    fred.join()

print gyro.value()