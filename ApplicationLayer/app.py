"""
The application layer for my part II project, designed to notify a user when they are approaching an obstacle

Wiring: TODO GPS
GPS    Pico
------------
       GND
       3V3
       GP2
       GP0
       GP3
       GP1
       GP4
"""


from micropython import const
import config
import rfm69
import board
import time
import random
from busio import SPI
import digitalio
import supervisor


# Talk to epidemic - ingoing and outgoing buffers

# Get gps location (again be careful as will be fighting with the networking layer)

# Check if GPS location is near an obstacle (if yes, flash light or beep / notify user)

# Let the user add an obstacle