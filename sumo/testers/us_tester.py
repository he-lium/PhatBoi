''' Tests the ultrasonic sensor'''

# Import system libraries
from time import sleep
import sys, os
import threading

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

us = UltrasonicSensor()

while True:
    print us.value()
    sleep(0.5)
