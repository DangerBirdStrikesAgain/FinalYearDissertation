"""
Logs all the packets received by the node in a useful format for debugging
"""

import config
import rfm69
import board
import busio
import digitalio

def log(message):
    print(message)

spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)


while True:
    args = rfm69.receive()
    if args is not None:
        packetLength, packetType, sender, destination, packet = args
        log(("Packet Length: " + str(packetLength)))

        if packetType == config.HELLO:
            log("Packet type: HELLO")
        elif packetType == config.RTS:
            log("Packet type: RTS")
        elif packetType == config.CTS:
            log("Packet type: CTS")
        elif packetType == config.DATA:
            log("Packet type: DATA")
        elif packetType == config.ACK:
            log("Packet type: ACK")
        elif packetType == config.DS:
            log("Packet type: DS")
        else:
            log(("Unknown packet type: " + str(packetType)))

        log(("Sender: " +str(sender)))

        log(("Destination: " + str(destination)))
        
        log(("Packet: " + str(packet)))