"""
The overall program for any nodes with the RFM69 and button but without GPS or buzzer

Includes Circuit Python implmentation of the epidemic routing protocol with media access control
Based on the paper by Amin Vahdat and David Becker: https://issg.cs.duke.edu/epidemic/epidemic.pdf

Uses Raspberry Pi Pico with RFM69HCW Radio breakout
Requires rfm69 library and config files

WIRING
Button    RFM69     Pico
--------------------------
+          VIN        3V3
-          GND        GND
L                     3V3
R                     GP7
           SCK        GP2
           MISO       GP0
           MOSI       GP3
           CS         GP1
           RST        GP4



TODO 
Logging -- make better and fit with the logging in the evaluation 
Button -- log when pressed :)

Now just the radio one
"""

from micropython import const
import config
import rfm69
import board
import time
import random
from busio import SPI
import digitalio
import supervisor
 
"""
Initialisation
"""
# Button 
button = digitalio.DigitalInOut(board.GP7)
button.switch_to_input(pull=digitalio.Pull.DOWN)

# RFM69
spi = SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP6)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

class Timers:
    def __init__(self):
        # supervisor.ticks_ms() contants
        self._TICKS_PERIOD = const(1 << 29)
        self._TICKS_MAX = const(self._TICKS_PERIOD - 1)
        self._TICKS_HALFPERIOD = const(self._TICKS_PERIOD // 2)

        # Initialise timers
        nextIncrement = config.HELLO_TIMER + random.uniform(-10.0, 10.0)
        self._nextHello = self._ticksAdd(supervisor.ticks_ms(), nextIncrement)
        self._contacted = self._ticksAdd(supervisor.ticks_ms(), config.CONTACTED_TIMER)
        self._ACKTimeout: int

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
    

    def hello(self) -> bool:
        """
        Checks if the timer for sending a hello has elapsed

        Args:
            None

        Returns:
            bool: True if the timer has elapsed, otherwise False
        """
        if self._ticksDiff(self._nextHello, supervisor.ticks_ms()) < 0:
            nextIncrement = config.HELLO_TIMER + random.uniform(-10.0, 10.0)
            self._nextHello = self._ticksAdd(supervisor.ticks_ms(), nextIncrement)
            return True
        return False

    def startQuietState(self):
        """
        Generates the timer to wait for an ACK

        Args:
            None

        Returns:
            None
        """
        nextIncrement = config.QUIET_STATE_TIMER + random.uniform(-5.0, 5.0)
        self._ACKTimeout = self._ticksAdd(supervisor.ticks_ms(), nextIncrement)

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
        return False
        

class Logging:
    """
    Class with multiple functions to handle logging
    
    Logs in form
    Node Address, Time, Time Since Node Startup, Event Type, Event Information
    """

    def __init__(self):
        # Printing turned on if we have a USB connection
        self._printing = supervisor.runtime.serial_connected

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
            print("Logging will be printed")
    
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



def getGPS():
    """
    Returns empty values due to absence of GPS chip
    """
    return (0.00000, 0.00000)