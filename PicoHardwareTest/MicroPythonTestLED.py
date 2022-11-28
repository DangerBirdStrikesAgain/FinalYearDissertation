"""
This makes the LED on the pico blink (in MicroPython)

If there is an LED, put one end to the pin number and the other to ground
"""

from machine import Pin, Timer
# pin number for offboard LED
# 25 onboard LED
led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()
    
timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)