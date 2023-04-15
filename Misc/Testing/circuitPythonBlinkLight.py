"""
CircuitPython to make the LED light on the Pico blink
"""

import time
import board
import digitalio

# pin for offboard LED, 25 for onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
 
while True:
    # Does CircuitPython have a "toggle"? If not, make one? 
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)