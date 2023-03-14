"""
Large MicroPython wrapper for my Part II Project `A MANET to Facilitate Collision Avoidance in Rowing Boats'
Uses Adafruit Blinka and CircuitPython with the chips

The LED will light up when there is power to the Pico

WIRING:
GPS   RFM69   Button   Pico
------------------------------
              - , L    GND
                +      3V3
                       GP0
                       GP1
                       GP2
                       GP3
                       GP4
                       GP14
                R      GP15
"""

# MicroPython imports
import time
import _thread
import machine

button = machine.Pin(13, machine.Pin.IN)


while True:
    print(button.value())
    
# Start the GPS
# def getGPS():

# Set up the global tables


# Replace core0 and core1 with the app and manet layers
#appLayer = _thread.start_new_thread(core1, ())
#core0()