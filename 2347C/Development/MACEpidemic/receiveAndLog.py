"""
Logs all the packets received by the node in a useful format for debugging
"""

import config
import rfm69
import board
import busio
import digitalio
import supervisor
import time
from micropython import const

class Timers():
    def __init__(self):
        # supervisor.ticks_ms() contants
        self._TICKS_PERIOD = const(1 << 29)
        self._TICKS_MAX = const(self._TICKS_PERIOD - 1)
        self._TICKS_HALFPERIOD = const(self._TICKS_PERIOD // 2)
        # To calculate timeSinceStart()
        self._start = supervisor.ticks_ms()

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

    def timeSinceStart(self) -> float:
        """
        Approximate time in seconds elapsed since the program started running
        Will only be accurate for the first 65 seconds as supervisor.ticks_ms() wraps around
        """
        msElapsed = self._ticksDiff(supervisor.ticks_ms(), self._start)
        return (msElapsed / 1000)


def log(message):
    print(message)

timer = Timers()

spi = busio.SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)


while True:
    args = rfm69.receive()
    if args is not None:
        packetLength, packetType, sender, destination, packet = args

        log(("Time since start"+ str(timer.timeSinceStart())))

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