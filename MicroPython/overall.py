"""
Large MicroPython wrapper for my Part II Project `A MANET to Facilitate Collision Avoidance in Rowing Boats'
Uses Adafruit Blinka and CircuitPython with the chips

The LED should light up when the program is running

WIRING:
GPS   RFM69   Button   Pico
------------------------------
                       GND
                       3V3
                       GP0
                       GP1
                       GP2
                       GP3
                       GP4
"""

# MicroPython imports
from time import sleep
import _thread


# Light up LED on button

# Start the GPS
# def getGPS():

# Set up the global tables


# Replace core0 and core1 with the app and manet layers
#appLayer = _thread.start_new_thread(core1, ())
#core0()