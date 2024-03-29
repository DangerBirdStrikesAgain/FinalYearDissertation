from micropython import const

"""
CONSTANTS
"""
# Should the node use a contacted list?
USECONTACTED = True


"""
RADIO FREQUENCY
""" 
FREQUENCY = 443


"""
TRANSMIT POWER 
20 is max safely supported
"""
TX_POWER = 13


"""
ADDRESSES
1 byte long
"""
# Address of node - this is different for each node!
ADDRESS = const(0x01)
BROADCAST = const(0xFF)


"""
STATES 
States we can be in
Ideally would be enums but CP doesn't support them
"""
LISTEN = 0
SEND_HELLO = 1
QUIET = 2
RECEIVED_HELLO = 3
RECEIVED_RTS = 4


"""
PACKET TYPES
All follow structure

|  length  | packetType |  sender  | destination | 
|                   payload                      | 
"""
# Payload is GPS location
HELLO = const(0x00)
# Payload contains the keys for message dict
RTS = const(0x01)
# Payload contains the keys for message dict
CTS = const(0x02)
# First byte of payload is the total number of DATA packets, second is the number of the DATA packet, then the messages themselves
DATA = const(0x03)
# Empty payload
ACK = const(0x04)


"""
TIMERS
in seconds 
"""
# Seconds to wait for the board to transmit the packet
TRANSMIT_TIMEOUT = 2.0
# Seconds to wait for the board to receive a packet
RECEIVE_TIMEOUT = 0.5
# How often to transmit a new hello message 
HELLO_TIMER = 5.0
# How long to remain in quiet mode when waiting for an ACK 
QUIET_STATE_TIMER = 15.0
# How often to decrement the contacted / do not contact list and the obstacles 
CONTACTED_TIMER  = 20.0
# How many times an entry in contacted / do not contact should be decremented 
CONTACTED_LIVES = 3
# How many times a message should be forwarded 
MESSAGE_NORMAL_TTL = 6
# How many times an important message should be forwarded
MESSAGE_IMPORTANT_TTL = 12
# How many times an obstacle should be decremented (5 minutes)
OBSTACLE_TTL = 15

"""
REENTRIES 
The number of attempts that should be made to send packets
"""
TS_REENTRIES = 3
DATA_REENTRIES = 8
ACK_REENTRIES = 3



"""
GPS 
Values for the specification of the GPS
"""
GPS_DISTANCE = 100