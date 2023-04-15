"""
Check that the adafruit ultimate GPS breakout V3 working

Wiring:
GPS    Pico
-----------
GND -> GND
VIN -> 3V3
RX  -> GP4
TX  -> GP5
"""

import time
import board
import busio
import digitalio
import adafruit_gps

uart = busio.UART(board.GP4, board.GP5, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)  # Use UART/pyserial

# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on everything
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')


# Set update rate to once a second (1hz) which is what you typically want.
print(gps.send_command(b"PMTK220,1000"))
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!

while True:
    if gps.update():
    # Every second print out current location details if there's a fix.
        if not gps.has_fix or gps.timestamp_utc is None:
            print("Waiting for fix... ")
            continue

        print(f'<trkpt lat="{gps.latitude_degrees}{gps.latitude_minutes}" lon="{gps.longitude_degrees}{gps.longitude_minutes}"><ele>{gps.altitude_m}</ele><time>2023-04-08T{gps.timestamp_utc.tm_hour}:{gps.timestamp_utc.tm_min}:{gps.timestamp_utc.tm_sec}Z</time></trkpt>')