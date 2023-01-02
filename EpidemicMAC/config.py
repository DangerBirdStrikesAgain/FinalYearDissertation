from micropython import const

# States we can be in
LISTEN = 0
SEND_HELLO = 1
QUIET = 2
RECEIVED_HELLO = 3


# Packet types - if we needed more room for sending perhaps make this
# 4 bits and the address 4 bits? (actually I think that would really limit the network size nvm)
HELLO = const(0x00)
RTS = const(0x01)
CTS = const(0x02)
# Data Send frame - what is about to be sent
DS = const(0x03)
DATA = const(0x04)
ACK = const(0x05)

# For broadcast
BROADCAST = const(0xFF)

# Address of node - this will need to be changed each time!
ADDRESS = const(0x01)

# Radio frequency
FREQUENCY = 443

# Hello timer - a new hello message is broadcast when this time elapses 
# remember that is in ms
HELLO_TIMER = 30000

# Quantity of time to wait for the board to transmit the packet
TRANSMIT_TIMEOUT = 2.0
# Quantitiy of time to wait for the board to receive a packet
RECEIVE_TIMEOUT = 0.5
# How long to try to send RTS es 
RTS_TIMEOUT = 3.0

# The number of attempts that should be made to send packets before giving up
RTS_REENTRIES = 3
DATA_REENTRIES = 3

# self.ack_retries = 5
#         """The number of ACK retries before reporting a failure."""
#         self.ack_delay = None
#         """The delay time before attemting to send an ACK.
#            If ACKs are being missed try setting this to .1 or .2.
#         """