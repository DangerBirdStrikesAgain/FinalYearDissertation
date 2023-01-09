from micropython import const

# ADDRESSES
# Address of node - this will need to be changed each time!
ADDRESS = const(0x01)
# Broadcast
BROADCAST = const(0xFF)


# RADIO FREQUENCY 
FREQUENCY = 443


# STATES WE CAN BE IN 
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
# Data Send frame - what is about to be sent
DS = const(0x03)
DATA = const(0x04)
ACK = const(0x05)


# TIMERS (in seconds) 
# Seconds to wait for the board to transmit the packet
TRANSMIT_TIMEOUT = 0.1
# Seconds to wait for the board to receive a packet
RECEIVE_TIMEOUT = 1
# How often to transmit a new hello message 
HELLO_TIMER = 30
# How long to remain in quiet mode when waiting for an ACK 
QUIET_STATE_TIMER = 20
# How often to decrement the contacted / do not contact list
CONTACTED_TIMER  = 20
# How many times an entry in contacted / do not contact should be decremented 
CONTACTED_LIVES = 3 


# REENTRIES (The number of attempts that should be made to send packets)
RTS_REENTRIES = 3
DATA_REENTRIES = 3




# self.ack_retries = 5
#         """The number of ACK retries before reporting a failure."""
#         self.ack_delay = None
#         """The delay time before attemting to send an ACK.
#            If ACKs are being missed try setting this to .1 or .2.
#         """