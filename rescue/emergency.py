# Look for additional libraries in parent dir
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# Import ev3dev library
from ev3dev.auto import *

# Connect motors
right_motor = LargeMotor(OUTPUT_B)
left_motor = LargeMotor(OUTPUT_C)
right_motor.stop()
left_motor.stop()
