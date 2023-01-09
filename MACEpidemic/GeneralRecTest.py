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

def getGPS():
    """
    TODO
    """
    # TODO - should this be a string? Is there a better way of doing this?
    return ("10.284638, 89.473057")


def sendHello() -> bool:
    """
    Sends a packet of type HELLO
    
    Args: 
        None 
    
    Returns:
        bool: True if success, False if error
    """
    gps = getGPS()
    return rfm69.send(data = bytes(gps, "utf-8"), destination = config.BROADCAST, packetType = config.HELLO)


"""
# Takes and deconstructs packets

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
"""

# We send a hello then print everything we receive out so we can test anti-entropy
sendHello()
print("Sent hello")
while True:
    args = rfm69.receive()
    if args is not None:
        packetLength, packetType, sender, destination, packet = args
        if packetType == config.RTS:
            print(rfm69.send(data = bytes("well, shit", "utf_8"), destination=sender, packetType=config.CTS))
        print("Packet Length: ", packetLength)
        print("Packet Type: ", packetType)
        print("Sender: ", sender)
        print("Packet: ", packet)

