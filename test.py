from machine import Pin, Timer
# 20 was for offboard LED, 25 was onboard LED
led = Pin(25, Pin.OUT)
timer = Timer()

def blink(timer):
    led.toggle()
    
timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)