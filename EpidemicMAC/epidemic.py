"""
A Circuit Python implmentation of the epidemic routing protocol with media access control
TODO - put the paper it is based on here
 
Uses Raspberry Pi Pico with the Adafruit Ultimate GPS Breakout V3 and RFM69HCW Radio breakout
Requires rfm69 library and config files
 
Wiring:
Radio   GPS   Pico
------------------
GND            GND
VIN            3V3
SCK            GP2
MISO           GP0
MOSI           GP3
CS             GP1
RST            GP4
"""

# TODO - Error handling



import config
import rfm69
import board
import time
import busio
import digitalio

# Set up the radio
spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)
# TODO - Initialise GPS? 

# List of nodes we have contacted recently
contacted = []

# Set the state to the starting state 
state = 0

def log(message):
    # TODO - perhaps change to adding to a logging file 
    print(message)

def getGPS():
    # TODO - should this be a string? Is there a better way of doing this?
    return ("10.284638, 89.473057")

def sendHello():
    gps = getGPS()
    return rfm69.send(data = bytes(gps, "utf-8"), destination = config.BROADCAST, packetType = config.HELLO)

def sendRTS(sender):
    # TODO - Something about a dict of the messages that we have and how to deal with them - key could be first 4 bytes as the node then the time - we can get this from the GPS? 
    data = "hello!! This is an RTS"
    return rfm69.send(data = bytes(data, "utf-8"), destination = sender, packetType = config.RTS)

def antiEntropy(sender):
    RTSCount = 0 
    #something about the RTS timeout and checking it for interrupt
    while RTSCount<config.RTS_REENTRIES:
        sendRTS(sender)
        RTSCount+=1

def sendToAppLayer(item):
    # TODO - implement this using global variable
    return True

def handleReceive(args):
    if args == None:
        return config.LISTEN
    elif args[1] == config.HELLO:
        return config.RECEIVED_HELLO
    elif args[1] == config.CTS and args[2]!=config.ADDRESS:
        # TODO - implment a timer so we don't happen to just zone out
        return config.QUIET

while True:
    if state == config.LISTEN:
        args = rfm69.receive()
        state = handleReceive(args)

    elif state == config.SEND_HELLO:
        if sendHello():
            state = config.LISTEN
        else:
            log("Failed to send hello")

    elif state == config.RECEIVED_HELLO:
        sender = args[2]
        packet = args[4]
        sendToAppLayer(packet)
        if sender not in contacted:
            if sender>config.ADDRESS:
                antiEntropy(sender) # This returns true or false let's use it for logging
                # TODO - move on the state
                """
                You're implementing the antiEntropy stuff here :) and making sure that all the packets are 
                """

    elif state==config.QUIET:
        # TODO - timer
        pass