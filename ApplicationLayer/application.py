"""
The application layer for my part II project, designed to notify a user when they are approaching an obstacle

Wiring: TODO GPS
GPS    Pico
------------
       GND
       3V3
       GP2
       GP0
       GP3
       GP1
       GP4
"""
# TODO - prioritise messages that are propagated by epidemic - messages with higher TTL (no of hops) get passed through the network faster


from micropython import const
import config
import board
import time
import random
from busio import SPI
import digitalio
import supervisor


class Logging:
    """
    Class with multiple functions to handle logging
    """

    def __init__(self):
        # Printing turned on if we have a USB connection
        self._printing = supervisor.runtime.serial_connected
        # self._printing = True

        # Log into file if not connected to device
        if not self._printing:
            import storage
            storage.remount("/", False)
            self._fp = open("/logging.txt", "a")
        
        self._red = "\033[91m"
        self._end = "\033[0m"
        self._blue = "\033[94m"
        self._green = "\033[92m"
        
        if self._printing:
            print("Logging")
    
    def log(self, message: str):
        global timers
        if self._printing:
            print(f"[{timers.timeSinceStart()}] {message}")
        else: 
            self._fp.write(f"[{timers.timeSinceStart()}] {message}")

    def logFunction(self, function: str, message: str):
        global timers
        if self._printing:
            print(f"{self._green}[{timers.timeSinceStart()}] [{function}] {message}{self._end}")
        else:
            self._fp.write(f"[{timers.timeSinceStart()}] [{function}] {message}")

    def logPacket(self, function: str, src: int, dst: int, pckType: int):
        global timers
        if self._printing:
            print(f"{self._blue}[{timers.timeSinceStart()}] [{function}] Source: {src} Dest: {dst} Type: {pckType}{self._end}")
        else:
            self._fp.write(f"[{timers.timeSinceStart()}] [{function}] Source: {src} Dest: {dst} Type: {pckType}")
        
    def logError(self, function: str, message: str):
        global timers
        if self._printing:
            print (f"{self._red}[{timers.timeSinceStart()}] [{function}] {message}{self._end}")
        else:
            self._fp.write(f"[{timers.timeSinceStart()}] [{function}] {message}")


class Timers:
    def __init__(self):
        # supervisor.ticks_ms() contants
        self._TICKS_PERIOD = const(1 << 29)
        self._TICKS_MAX = const(self._TICKS_PERIOD - 1)
        self._TICKS_HALFPERIOD = const(self._TICKS_PERIOD // 2)

        # Initialise timers

        # For time since start
        self._start = supervisor.ticks_ms()        


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
        diff = int(ticks1 - ticks2) & self._TICKS_MAX
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


    def timeSinceStart(self) -> float:
        """
        Approximate time in seconds elapsed since the program started running
        Will only be accurate for the first 65 seconds as supervisor.ticks_ms() wraps around
        """
        msElapsed = self._ticksDiff(supervisor.ticks_ms(), self._start)
        return (msElapsed / 1000)
    

def getGPS():
    """
    TODO (will be moved up)
    """
    
    return (10.284638, 89.473057)



while True: 
    location = getGPS()

    # Check if GPS location is near an obstacle (if yes, flash light or beep / notify user)

    # Talk to epidemic - ingoing and outgoing buffers

    # Let the user add an obstacle