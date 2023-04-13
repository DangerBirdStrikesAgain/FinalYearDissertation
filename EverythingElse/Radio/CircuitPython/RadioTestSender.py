"""
CircuitPython - sends hello world messages through the radio

Wiring:
Radio  Pico
-----------
GND  -> GND
VIN  -> 3V3
SCK  -> GP2
MISO -> GP0
MOSI -> GP3
CS   -> GP1
RST  -> GP4
"""

import time
import board
import busio
import digitalio
import adafruit_rfm69

# radio
FREQ = 433
spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, FREQ, fixed_length = True)
count = 1


print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))


while True:
    message = "Hello world!\r\n"+str(count)
    rfm69.send(bytes(message, "utf-8"))
    print("Sent ", count, " hello world messages!")
    count+=1
    #time.sleep(1)
