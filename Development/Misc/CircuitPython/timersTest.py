"""
Testing out the timers on the RPi Pico with Circuit Python
"""

import rfm69
import board
import time
import busio
import digitalio
import supervisor
HAS_SUPERVISOR = hasattr(supervisor, "ticks_ms")


"""
# Learning what the supervisor is and its uses
if supervisor.runtime.serial_connected:
    print("Hello World!")
"""


HELLO_TIMER = 30

# supervisor.ticks_ms() contants
_TICKS_PERIOD = const(1 << 29)
_TICKS_MAX = const(_TICKS_PERIOD - 1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD // 2)



def ticks_add(ticks: int, delta: float) -> int:
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
    return (ticks + (delta*1000)) % _TICKS_PERIOD


def ticks_diff(ticks1: int, ticks2: int) -> int:
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
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff


def check_timeout(flag: Callable, limit: float) -> bool:
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
        if ticks_diff(supervisor.ticks_ms(), start) >= limit * 1000:
            timed_out = True
    
    return timed_out


helloEnd = ticks_add(supervisor.ticks_ms(), 20*1000)
 
print(_TICKS_PERIOD)

print("Started!")
while ticks_diff(helloEnd, supervisor.ticks_ms()) > 0:
    pass
print("HELL YES HELLO")