from micropython import const

# ADDRESSES
# Address of node - this will need to be changed each time!
ADDRESS = const(0x01)
# Broadcast
BROADCAST = const(0xFF)


# RADIO FREQUENCY 
FREQUENCY = 443

# TRANSMIT POWER (max safely supported)
TX_POWER = 20


# STATES WE CAN BE IN 
# (ideally would be enums but CP doesn't support them)
LISTEN = 0
SEND_HELLO = 1
QUIET = 2
RECEIVED_HELLO = 3
RECEIVED_RTS = 4


# PACKET TYPES
# TODO - put the packet structures in the comments here
HELLO = const(0x00)
RTS = const(0x01)
CTS = const(0x02)
# Data frame - first one contains what is about to be sent (the DS frame was shoved in there) the structure if properly detailed in your notebook
DATA = const(0x03)
ACK = const(0x04)


# TIMERS (in seconds) 
# Seconds to wait for the board to transmit the packet
TRANSMIT_TIMEOUT = 2.0
# Seconds to wait for the board to receive a packet
RECEIVE_TIMEOUT = 0.5
# How often to transmit a new hello message 
HELLO_TIMER = 20.0
# How long to remain in quiet mode when waiting for an ACK 
QUIET_STATE_TIMER = 20.0
# How often to decrement the contacted / do not contact list
CONTACTED_TIMER  = 20.0
# How many times an entry in contacted / do not contact should be decremented 
CONTACTED_LIVES = 3 

# REENTRIES (The number of attempts that should be made to send packets)
TS_REENTRIES = 10
DATA_REENTRIES = 10