"""
A Circuit Python implmentation of the epidemic routing protocol with media access control
TODO - put the paper it is based on here
 
Uses Raspberry Pi Pico with the Adafruit Ultimate GPS Breakout V3 and RFM69HCW Radio breakout
Requires rfm69 library and config files
 
Wiring: TODO
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
# TODO - Random backoff for the timers
# You have a bunch of global variables and I feel like they're bad practice

from micropython import const
import config
import rfm69
import board
import time
import random
# from busio import SPI
import busio
import digitalio

import supervisor

class Timers:
    def __init__(self):
        # supervisor.ticks_ms() contants
        self._TICKS_PERIOD = const(1 << 29)
        self._TICKS_MAX = const(self._TICKS_PERIOD - 1)
        self._TICKS_HALFPERIOD = const(self._TICKS_PERIOD // 2)

        # Initialise timers
        self._nextHello = self._ticksAdd(supervisor.ticks_ms(), config.HELLO_TIMER)
        self._contacted = self._ticksAdd(supervisor.ticks_ms(), config.CONTACTED_TIMER)
        self._ACKTimeout: int


    def _ticksAdd(self, ticks: int, delta: float) -> int:
        """
        Add delta multiplied by 1000 to a base number of ticks,
        performing wraparound at 2**29ms
        (i.e. ticks + delta*1000)
        Multiplying by 1000 allows for delta to be passed in as seconds and handled as milliseconds 
        
        Args:
            ticks (int): The base value of ticks 
            delta (float): The increment for ticks
        
        Returns:
            int: The new value for ticks
        """
        return (ticks + (delta*1000)) % self._TICKS_PERIOD


    def _ticksDiff(self, ticks1: int, ticks2: int) -> int:
        """
        Compute the signed difference between two ticks values
        Assumes that they are within 2**28 ticks
        (i.e. tick1-tick2)

        Args:
            ticks1 (int): The first value
            ticks2 (int): The second value

        Returns:
            int: The signed difference between ticks 1 and 2
        """
        diff = (ticks1 - ticks2) & self._TICKS_MAX
        diff = ((diff + self._TICKS_HALFPERIOD) & self._TICKS_MAX) - self._TICKS_HALFPERIOD
        return diff


    def _checkTimeout(self, flag: Callable, limit: float) -> bool:
        """
        Test for timeout waiting for specified flag

        Args:
            flag (Callable): The flag to be checked for timeout
            limit (float): The number of seconds to wait for the timeout

        Returns:
            bool: True if timeout, otherwise False
        """
        timed_out = False
        
        start = supervisor.ticks_ms()
        while not timed_out and not flag():
            if self.ticks_diff(supervisor.ticks_ms(), start) >= limit * 1000:
                timed_out = True
        
        return timed_out

    
    def hello(self) -> bool:
        """
        Checks if the timer for sending a hello has elapsed

        Args:
            None

        Returns:
            bool: True if the timer has elapsed, otherwise False
        """

        if self._ticksDiff(self._nextHello, supervisor.ticks_ms()) < 0:
            self._nextHello = self._ticksAdd(supervisor.ticks_ms(), config.HELLO_TIMER)
            return True
        else: 
            return False


    def startQuietState(self):
        """
        Generates the timer to wait for an ACK

        Args:
            None

        Returns:
            None
        """
        self._ACKTimeout = self._ticksAdd(supervisor.ticks_ms(), config.QUIET_STATE_TIMER)

    def quiet(self) -> bool:
        """
        Checks if the timer for waiting for an ACK has elapsed

        Args:
            None

        Returns:
            bool: True if the timer has elapsed, otherwise False
        """

        if self._ticksDiff(self._ACKTimeout, supervisor.ticks_ms()) < 0:
            return True
        else:
            return False

    
    def contacted(self) -> bool:
        """
        Checks if the timer for decrementing the contacted list has elapsed

        Args:
            None

        Returns:
            bool: True if the timer has elapsed, otherwise False
        """

        if self._ticksDiff(self._contacted, supervisor.ticks_ms()) < 0:
            self._contacted = self._ticksAdd(supervisor.ticks_ms(), config.CONTACTED_TIMER)
            return True
        else: 
            return False




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


def sendRTS(dest: int) -> bool:
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


def handleReceive(args: Tuple[Any], quietState: Optional[bool] = False):
    """
    TODO explain this
    """
    global quietNode
    global timers 
    # Quietmode ensures that we don't accidentally break out of the quiet state
    # TODO Actually should we be taking the state as input? 
    if not quietState:
        if args == None or args[1] == config.DS or args[1] == config.DATA or args[1] == config.ACK:
            return config.LISTEN
        elif args[1] == config.HELLO:
            return config.RECEIVED_HELLO
        elif args[1] == config.CTS: # and args[2]!=config.ADDRESS:
            # Record the sender so we know when the correct ACK comes along
            quietNode = args[3]
            # Start the timer to ensure if an ACK is not heard, we do not remain in quiet mode forever
            timers.startQuietState()
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
        elif timers.quiet() or (args[1] == config.ACK and args[2] == quietNode):
            # Note that the exit from quiet is listen
            return config.LISTEN
        else:
            message = "Saw an unknown packet type: ", args[1]
            log(message)


def decrementContacted(contacted: dict[int, int]) -> dict[int, int]:
    """"
    Decrements the TTL for each key in contacted, removing anything with a TTL of 0

    Args:
        contacted (dict[int, int]): The dictionary of contacted nodes, key is node address, value is TTL

    Returns:
        dict[int, int]: The modified dictionary
    """

    for key in contacted:
        contacted[key]+=-1
        if contacted[key]==0:
            del(contacted[key])
    
    return contacted


# Initialise the radio
spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

# TODO - Initialise GPS? 

# List of nodes we have contacted recently
contacted: dict[int, int]
contacted = {}

# Node we waiting to overhear an ACK from before we can exit QUIET state
quietNode: int

# Set the state to the starting state 
state = config.LISTEN

# Logging turned on if we have a USB connections
logging = supervisor.runtime.serial_connected
if logging:
    print("Logging")

# TODO is this bad programming practice? It's a global variable that is called from in handle recieve
timers = Timers()

while True:
    log(state)
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


    # Poll timers (best we can do due to lack of interrupt support in CircuitPython)
    if timers.contacted():
        contacted = decrementContacted(contacted)
    if timers.hello():
        state=config.SEND_HELLO