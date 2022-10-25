"""
This makes the LED on the pico blink (in MicroPython)
"""

from machine import Pin, Timer
# 20 (or number of your choice) for offboard LED
# 25 onboard LED
led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()
    
timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)