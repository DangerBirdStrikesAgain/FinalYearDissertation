"""
This should get the damn radio working
"""

import time
import board
import busio
import digitalio
import adafruit_rfm69

# radio
FREQ = 433.0
spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = adafruit_rfm69.RFM69(spi, cs, reset, FREQ)


print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))

while True:
    print ("Got here!")
    packet = rfm69.receive()
    if packet is not None:
        packet_text = str(packet, 'ascii')
        print('Received: {0}'.format(packet_text))
        count = count + 1
    else:
        print("no packet")
