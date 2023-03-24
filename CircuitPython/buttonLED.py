"""
Turns LED on and off as a button is pressed

WIRING:

Led:
GP14, GND 

Button:
3V3, GP13 (diagonally opposite legs)
"""

import time
import board
import digitalio

def toggle(value):
    if value:
        return False
    return True

button = digitalio.DigitalInOut(board.GP15)
button.switch_to_input(pull=digitalio.Pull.DOWN)
#led = digitalio.DigitalInOut(board.GP14)
#led.direction = digitalio.Direction.OUTPUT


while True:
    if button.value:
        #led.value = toggle(led.value)
        # To debounce we sleep
        print("BITCH")
        time.sleep(0.5)

"""
while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)
"""