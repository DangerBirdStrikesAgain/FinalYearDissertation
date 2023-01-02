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
# Also perhaps use some form of typing


import config
import rfm69
import board
import time
import busio
import digitalio
from typing import Callable, Optional, Type


def log(message: str):
    """ 
    If global variable logging is true, prints message
    
    Args:
        message (str): The string to be printed
    
    Returns:
        None
    """
    global logging

    if logging:
        print(message)


def getGPS():
    """
    TODO
    """
    # TODO - should this be a string? Is there a better way of doing this?
    return ("10.284638, 89.473057")


def sendHello():
    """
    Sends a packet of type HELLO
    
    Args: 
        None 
    
    Returns:
        bool: True if success, False if error
    """
    gps = getGPS()
    return rfm69.send(data = bytes(gps, "utf-8"), destination = config.BROADCAST, packetType = config.HELLO)


def sendRTS(dest):
    """
    Sends a packet of type RTS to the given sender

    Args:
        sender (int): The address of the node the RTS should be sent to

    Returns:
        bool: True if success, False if error
    """
    # TODO - Something about a dict of the messages that we have and how to deal with them - key could be first 4 bytes as the node then the time - we can get this from the GPS? 
    data = "hello!! This is an RTS"
    return rfm69.send(data = bytes(data, "utf-8"), destination = dest, packetType = config.RTS)


def antiEntropy(dest):
    """
    Starts the transfer of messages from one node to another
    
    Args:
        dest (int): The second node anti-entropy should be initiated with

    Returns:
        TODO
    """
    RTSCount = 0 
    #something about the RTS timeout and checking it for interrupt
    while RTSCount<config.RTS_REENTRIES:
        sendRTS(dest)
        RTSCount+=1


def sendToAppLayer(item):
    """
    TODO
    """
    # TODO - implement this using global variable
    return True


def handleReceive(args, quietState = False):
    global quietNode
    # Quietmode ensures that we don't accidentally break out of the quiet state
    # TODO Actually should we be taking the state as input? 
    if not quietState:
        if args == None or args[1] == config.DS or args[1] == config.DATA or args[1] == config.ACK:
            return config.LISTEN
        elif args[1] == config.HELLO:
            return config.RECEIVED_HELLO
        elif args[1] == config.CTS: # and args[2]!=config.ADDRESS:
            # TODO - implment a timer so we don't just zone out forever if there's an error
            # Record the sender so we know when the correct ACK comes along
            quietNode = args[3]
            return config.QUIET
        elif args[1] == config.RTS:
            if args[3] == config.ADDRESS:
                return config.RECEIVED_RTS
            else:
                return config.LISTEN
        else:
            message = "Saw an unknown packet type: ", args[1]
            log(message)
            
    else: 
        if args == None or args[1] == config.DS or args[1] == config.DATA or args[1]==config.HELLO or args[1]==config.RTS:
            return config.QUIET
        elif args[1] == config.CTS: # and args[2]!=config.ADDRESS: 
            # TODO - should we actually be doing something about this? 
            # Currently we just assume that we won't see two CTSs from different nodes
            return config.QUIET
        elif args[1] == config.ACK and args[2] == quietNode:
            # Note that the exit from quiet is listen
            return config.LISTEN
        else:
            message = "Saw an unknown packet type: ", args[1]
            log(message)



# Initialise the radio
spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

# TODO - Initialise GPS? 

# List of nodes we have contacted recently
contacted = []

# Node we waiting to overhear an ACK from before we can exit QUIET state
quietNode: int

# Set the state to the starting state 
state = 0

# Set this to true or false if we want to log errors
logging = True


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
                You're implementing the antiEntropy stuff here :)
                """

    elif state == config.QUIET:
        
        args = rfm69.receive()
        state = handleReceive(args, quietState=True)


    # Ok we're going to put our timers down here because I'm like 90% sure we can't generate interrupts in CircuitPython (TODO check this)
    # Check the timers