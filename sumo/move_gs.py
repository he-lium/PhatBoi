# Import system libraries
from time import sleep
import sys, os
import threading

# Look for additional libraries in parent dir of program
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import ev3dev library
from ev3dev.auto import *

gs_motor = MediumMotor(OUTPUT_B)
left_motor = LargeMotor(OUTPUT_A)
right_motor = LargeMotor(OUTPUT_D)

gs = GyroSensor()

gs.mode = 'GYRO-RATE'	# Changing the mode resets the gyro
gs.mode = 'GYRO-ANG'	# Set gyro mode to return compass angle
btn = Button()		# We will need to check EV3 buttons state.

gs_motor.run_direct(duty_cycle_sp=20)

while abs(gs_motor.position) < 90:
    sleep(0.1)

gs_motor.stop()