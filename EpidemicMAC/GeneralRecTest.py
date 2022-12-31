import config
import rfm69
import board
import time
import busio
import digitalio

spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

while True:
    args = rfm69.receive()
    if args is not None:
        packetLength, packetType, sender, destination, packet = args
        print("Packet Length: ", packetLength)
        print("Packet Type: ", packetType)
        if packetType == config.HELLO:
            print("Yes, it is a hello packet")
        print("Sender: ", sender)
        print("Destination: ", destination)
        if destination == config.BROADCAST:
            print("Yes, it is a broadcast :)")
        print("Packet: ", packet)
