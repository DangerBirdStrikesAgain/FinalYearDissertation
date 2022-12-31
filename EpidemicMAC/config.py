from micropython import const

# Packet types - if we needed more room for sending perhaps make this
# 4 bits and the address 4 bits?
HELLO = const(0x00)

# For broadcast
BROADCAST = const(0xFF)

# Address of node - this will need to be changed each time!
ADDRESS = const(0x01)

# Radio frequency
FREQUENCY = 443

# Hello timer - a new hello message is broadcast when this time elapses 
# remember that is in ms
HELLOTIMER = 30000

# Quantity of time to wait for the board to transmit the packet
TRANSMIT_TIMEOUT = 2.0

# Quantitiy of time to wait for the board to receive a packet
RECEIVE_TIMEOUT = 0.5


# self.ack_retries = 5
#         """The number of ACK retries before reporting a failure."""
#         self.ack_delay = None
#         """The delay time before attemting to send an ACK.
#            If ACKs are being missed try setting this to .1 or .2.
#         """