''' Tests the gyro sensor'''

# Import system libraries
from time import sleep
import sys, os
import threading

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *


gs = GyroSensor()

gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle
btn = Button()		# We will need to check EV3 buttons state.

while True:
    sleep(1)
    print gs.value()