import time
import board
import digitalio

# from machine import Pin, Timer
# 20 was for offboard LED, 25 was onboard LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
 
while True:
    led.value = True
    time.sleep(0.5)
    led.value = False
    time.sleep(0.5)