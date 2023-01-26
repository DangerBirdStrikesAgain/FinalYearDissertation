"""
A Circuit Python implmentation of the epidemic routing protocol with media access control
Based on the paper by Amin Vahdat and David Becker: https://issg.cs.duke.edu/epidemic/epidemic.pdf

A 'clean' version of the epidemic implementation with no logging

Uses Raspberry Pi Pico with the Adafruit Ultimate GPS Breakout V3 and rfm69HCW Radio breakout
Requires rfm69 library and config files
 
Wiring: TODO GPS
Radio   GPS   Pico
------------------
GND            GND
VIN            3V3
SCK            GP2
MISO           GP0
MOSI           GP3
CS             GP1
RST            GP4
"""

# TODO - get from app layer function to add to messages

from micropython import const
import config
import rfm69
import board
import time
import random
from busio import SPI
import digitalio
import supervisor


def sendToAppLayer(item):
    """
    TODO - implement this using global variable(s)
    """
    return True

def getFromAppLayer(item):
    """
    TODO - make this work and poll it every so often (no interupts) to make sure we don't miss anything
    """
    # This is called when a timer goes 
    # Checks if something is empty and if so returns None or something
    # If not empty, return a new dictionary entry to be added to the dictionary entries
    # Perhaps if this returns something we should clear contacted sp will be forwarded to all neighbours who send a hello? Actually will only work for very small 
    # numerical nodes



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
        

def getGPS():
    """
    TODO
    """
    
    return (10.284638, 89.473057)


def sendHello() -> bool:
    """
    Sends a packet of type HELLO
    
    Args: 
        None 
    
    Returns:
        bool: True if success, False if error
    """
    gps = getGPS()
    return rfm69.send(data = bytes((str(gps[0])+"," + str(gps[1])), "utf-8"), destination = config.BROADCAST, packetType = config.HELLO)


def sendRTS(dest: int, messages: dict) -> bool:
    """
    Sends a packet of type RTS to the given sender

    Args:
        dest (int): The address of the node the RTS should be sent to
        messages (dict): The messages that the node holds

    Returns:
        bool: True if success, False if error
    """
    data = 0

    # Iterate through the keys to generate byte array of the keys to send to the 
    for key in messages:
        data = data << 16 | key
    
    data = data.to_bytes(len(messages)*2, "utf_8")

    return rfm69.send(data, destination = dest, packetType = config.RTS)


def removeLowestMessage(messages: dict) -> dict:
    """
    Removes the item in the messages dict with the lowest TTL 

    Args: 
        messages (dict): The dictionary of messages

    Returns:
        dict: The dictionary of messages, with the message with the lowest TTL removed
    """

    messagesList = list(messages.items())
    lowest = messagesList[0][0]
    lowestTTL = messagesList[0][1][2]

    for item in messagesList:
        if item[1][1] < lowestTTL:
            lowestTTL = item[1][2]
            lowest = item[0]

    del(messages[lowest])
    return messages


def decodeMessages(receivedMessages: str) -> dict:
    """
    Takes a series of strings that came through data packets and turns them into a dictionary 
    Assumes the data arrives comes in the form
    key,gpsA,gpsB,TTL\n

    Args:
        receivedMessages (str): The string of received messages

    Returns: 
        dict: The dictionary of messages, ready to be integrated
    """

    messages={}

    lines = receivedMessages.split("\n")
    for line in lines:
        if line != "":
            temp = line.split(",")
            # Drops any messages that have been forwarded too many times
            if len(temp)!=1 and int(temp[3])!=0:
                messages.update({int(temp[0]) : [float(temp[1]),float(temp[2]),(int(temp[3])-1)]})
    
    return messages


def RTSGetData(sender: int, packet: Optional[str] = None) -> tuple(bool, dict):
    """
    Called from RTSAntiEntropy
    Listens for data packets and extracts the messages from them
    Assumes the data arrives comes in the form
    total, number
    key,gpsA,gpsB,TTL\n

    Args:
        sender (int): The sender of the DATA packets
        packet (Optional[str]): A previously received DATA packet, if exists

    Returns:
        bool: True if all expected packets seen, otherwise false
        dict: The dictionary of new values
    """
    dataCount = 0
    receivedMessages = ""

    if packet is None:
        while packet is None and dataCount<config.DATA_REENTRIES:
            args = rfm69.receive(timeout = 3)
            if args is not None and args[1] == config.DATA and args[2] == sender: 
                packet = args[4]
            dataCount+=1
    
    if packet is None:
        return (False, {})

    dataCount = 0

    # Construct a list of zeros from the packet, if more than one packet will be sent
    totalLen = packet[0]
    if totalLen != 0:
        seen = [0]*(totalLen)
        receivedMessages += packet[2:].decode("utf_8")
        seen[packet[1]]=1
    else: 
        seen = [0]
        receivedMessages = packet[2:].decode("utf_8")

    while dataCount<config.DATA_REENTRIES and sum(seen) != totalLen:
        args = rfm69.receive(timeout=2)
        if args is not None and args[1] == config.DATA and args[2] == sender: 
            packet = args[4]
            if seen[packet[1]] == 0:
                receivedMessages += packet[2:].decode("utf_8")
                seen[packet[1]]=1
        dataCount+=1

    messages = decodeMessages(receivedMessages)

    # Indicates success so send an ACK
    if sum(seen) == totalLen:
        flag = True
        sendCount = 0
        while flag and sendCount<config.ACK_REENTRIES:
            rfm69.send(data = b'', destination = sender, packetType = config.ACK)
            param = rfm69.receive(timeout = 2)
            # If we are still receiving data then resend the ACK
            if param is None or not param[1]==config.DATA:
                flag = False 
        return(True, messages)

    return (False, messages)


def RTSSendDataFrames(dest: int, messages: dict):
    """
    Called from RTSAntiEntropy
    Sends data frames until an ACK or another data frame (indicating receipt) is received from the destination
    
    Args:
        dest (int): The destination of the data frames
        messages (dict): The dictionary of messages to be sent

    Returns:
        bool: True if success, False otherwise
    """
    dataCount = 0
    DATA = False

    # If there are no messages to send
    if len(messages) == 0:
        while dataCount<=config.DATA_REENTRIES and not DATA:
            prefix = bytearray(2)
            prefix[0] = 0
            prefix[1] = 0
            rfm69.send(data = prefix, destination = dest, packetType = config.DATA)
            args = rfm69.receive(timeout = 3)
            dataCount += 1
            if args is not None and args[2] == dest and args[1] == config.DATA:
                DATA = True
        
        if DATA:
            return (True, args)
        
        return (False, None)

    # Generate the data frames to be sent and put them into a list
    toSend = []
    string=""
    for key in messages:
        msg = str(key)+","+str(messages[key][0])+","+str(messages[key][1])+","+str(messages[key][2])+"\n"
        if len(string) + len(msg) > 58:
            toSend.append(string)
            string = msg
        else: 
            string = string + msg
    toSend.append(string)

    total = len(toSend)
    while dataCount<=config.DATA_REENTRIES and not DATA:
        # Send all the data frames
        number = 0
        for packet in toSend:
            prefix = bytearray(2)
            prefix[0] = total
            prefix[1] = number
            number+=1
            prefix = prefix + bytes(packet, "utf_8")
            rfm69.send(data = prefix, destination = dest, packetType = config.DATA)
            time.sleep(0.1)

        dataCount+=1
        args = rfm69.receive(timeout = 3)
        if args is not None and args[2] == dest and (args[1] == config.DATA or args[1] == config.ACK):
            DATA = True

    if DATA:
        return (True, args)

    return (False, None)


def RTSAntiEntropy(dest: int, messages: dict) -> tuple(bool, dict):
    """
    Starts the transfer of messages from one node to another
    
    Args:
        dest (int): The second node anti-entropy should be initiated with
        messages (dict): The dictionary of messages the node holds

    Returns:
        bool: True if successful message transfer, otherwise false
        dict: The updated messages dictionary 
    """
    RTSCount = 0 
    CTS = False

    while RTSCount<config.TS_REENTRIES and not CTS:
        sendRTS(dest, messages)
        time.sleep(0.2)
        RTSCount+=1
        args = rfm69.receive(timeout=2)
        if args is not None and args[1] == config.CTS and args[2] == dest:
            CTS = True
    
    # Indicates failure to receive a CTS
    if RTSCount>=config.TS_REENTRIES and not CTS:
        return (False, messages)
    
    # We receive a CTS from the desired node
    else:
        packet = args[4]
        destKeys = []
        messagesToSend = {}
        if len(packet) != 0:
            for x in range (0, len(packet), 2):
                destKeys.append(int.from_bytes(packet[x:(x+2)], "utf_8"))
            for key in messages:
                if key not in destKeys:
                    messagesToSend.update({key : messages[key]})
        success, args = RTSSendDataFrames(dest, messagesToSend)
        if not success:
            return (False, messages)

        success, newMessages = RTSGetData(sender=dest, packet = args[4])

        if newMessages != {}:
            sendToAppLayer(newMessages)
            messages.update(newMessages)
            while len(messages)>30:
                messages = removeLowestMessage(messages = messages)

        return (success, messages)        


def CTSSendDataFrames(dest: int, messages: dict):
    """
    Called from CTSAntiEntropy
    Sends data frames until an ACK or another data frame (indicating receipt) is received from the destination
    
    Args:
        dest (int): The destination of the data frames
        messages (dict): The dictionary of messages to be sent

    Returns:
        bool: True if success, False otherwise
    """
    dataCount = 0
    ACK = False

    # If there are no messages to send
    if len(messages) == 0:
        while dataCount<=config.DATA_REENTRIES and not ACK:
            prefix = bytearray(2)
            prefix[0] = 0
            prefix[1] = 0
            rfm69.send(data = prefix, destination = dest, packetType = config.DATA)
            args = rfm69.receive(timeout = 3)
            if args is not None and args[2] == dest and (args[1] == config.DATA or args[1] == config.ACK):
                ACK = True
        
        if ACK:
            return (True, args)
        else:
            return (False, None)

    # Generate the data frames to be sent and put them into a list
    toSend = []
    string=""
    for key in messages:
        msg = str(key)+","+str(messages[key][0])+","+str(messages[key][1])+","+str(messages[key][2])+"\n"
        if len(string) + len(msg) > 58:
            toSend.append(string)
            string = msg
        else: 
            string = string + msg
    toSend.append(string)

    total = len(toSend)
    while dataCount<=config.DATA_REENTRIES and not ACK:
        # Send all the data frames
        number = 0
        for packet in toSend:
            prefix = bytearray(2)
            prefix[0] = total
            prefix[1] = number
            number+=1
            prefix = prefix + bytes(packet, "utf_8")
            rfm69.send(data = prefix, destination = dest, packetType = config.DATA)
            time.sleep(0.1)

        dataCount+=1
        args = rfm69.receive(timeout = 3)
        if args is not None and args[2] == dest and args[1] == config.ACK:
            ACK = True

    if ACK:
        return (True, args)

    return (False, None)


def CTSGetData(sender: int, packet: Optional[str] = None) -> tuple(bool, dict):
    """
    Called from CTSAntiEntropy
    Listens for data packets and extracts the messages from them
    Assumes the data arrives comes in the form
    total, number
    key,gpsA,gpsB,TTL\n

    Args:
        sender (int): The sender of the DATA packets
        packet (Optional[str]): A previously received DATA packet, if exists

    Returns:
        bool: True if all expected packets seen, otherwise false
        dict: The dictionary of new values
    """
    dataCount = 0
    receivedMessages = ""

    if packet is None:
        while packet is None and dataCount<config.DATA_REENTRIES:
            args = rfm69.receive(timeout = 3)
            if args is not None and args[1] == config.DATA and args[2] == sender: 
                packet = args[4]
            dataCount+=1
    
    if packet is None:
        return (False, {})

    dataCount = 0

    # Construct a list of zeros from the packet, if more than one packet will be sent
    totalLen = packet[0]
    if totalLen != 0:
        seen = [0]*(totalLen)
        receivedMessages += packet[2:].decode("utf_8")
        seen[packet[1]]=1
    else: 
        seen = [0]
        receivedMessages = packet[2:].decode("utf_8")

    while dataCount<config.DATA_REENTRIES and sum(seen) != totalLen:
        args = rfm69.receive()
        if args is not None and args[1] == config.DATA and args[2] == sender: 
            packet = args[4]
            if seen[packet[1]] == 0:
                receivedMessages += packet[2:].decode("utf_8")
                seen[packet[1]]=1
        dataCount+=1

    messages = decodeMessages(receivedMessages)

    # Indicates success
    if sum(seen) == totalLen:
        return(True, messages)

    return (False, messages)


def sendCTS(sender: int, messages: dict):
    """
    Sends a packet of type CTS to the given sender

    Args:
        sender (int): The address of the node the RTS should be sent to
        messages (dict): The messages that the node holds

    Returns:
        bool: True if success, False if error
    """
    data = 0

    # Iterate through the keys to generate byte array of the keys to send to the 
    for key in messages:
        data = data << 16 | key
    
    data = data.to_bytes(len(messages)*2, "utf_8")
    return rfm69.send(data = data, destination = sender, packetType = config.CTS)


def CTSAntiEntropy(sender: int, messages: dict, RTSpacket: bytearray) -> dict:
    """
    Allows and continues the transfer of messages from one node to another
    
    Args:
        dest (int): The node that is initiating anti-entropy 
        messages (dict): The dictionary of messages the node holds
        packet (bytearray): The payload of the RTS packet, containing the keys the other node has

    Returns:
        dict: The updated messages dictionary
    """
    CTSCount = 0 
    DATA = False

    while CTSCount<config.TS_REENTRIES and not DATA:
        sendCTS(sender, messages)
        CTSCount+=1
        args = rfm69.receive(timeout=2)
        if args is not None and args[1] == config.DATA and args[2] == sender:
            DATA = True
        time.sleep(0.1)

    # Indicates failure to receive a data frame
    if not DATA:
        return False, messages
    
    # We receive a data frame from the desired node
    success, newMessages = CTSGetData(sender = sender, packet = args[4])

    if success:
        # Generate keys the other node wants
        destKeys = []
        messagesToSend = {}
        if len(RTSpacket) != 0:
            for x in range (0, len(RTSpacket), 2):
                destKeys.append(int.from_bytes(RTSpacket[x:(x+2)], "utf_8"))
            for key in messages:
                if key not in destKeys:
                    messagesToSend.update({key : messages[key]})
        success, args = CTSSendDataFrames(sender, messagesToSend)

    if newMessages != {}:
        sendToAppLayer(newMessages)
        messages.update(newMessages)
        while len(messages)>30:
            messages = removeLowestMessage(messages = messages)

    return success, messages


def handleReceive(params: tuple[any]) -> int:
    """
    Takes the return value of the receive function (rfm69) and updates the state accordingly

    Args:
        params (tuple[Any]): The value(s) returned from receive

    Returns:
        int: The new state
    """
    global quietNode
    global timers 
    global state

    if state==config.LISTEN:
        if params == None or params[1] == config.DATA or params[1] == config.ACK:
            return config.LISTEN
        elif params[1] == config.HELLO:
            return config.RECEIVED_HELLO
        elif params[1] == config.CTS: 
            # Record the sender so we know when the correct ACK comes along
            quietNode = params[3]
            # Start the timer to ensure if an ACK is not heard, we do not remain in quiet mode forever
            timers.startQuietState()
            return config.QUIET
        elif params[1] == config.RTS:
            if params[3] == config.ADDRESS:
                return config.RECEIVED_RTS
            else:
                return config.LISTEN
        else:
            return config.LISTEN
            
    elif state==config.QUIET: 
        if timers.quiet():
            return config.LISTEN
        elif params == None or params[1] == config.DATA or params[1]==config.HELLO or params[1]==config.RTS:
            return config.QUIET
        elif (params[1] == config.ACK and params[2] == quietNode):
            # All nodes after they recieve an ACK should not talk for 3 seconds
            time.sleep(3)
            return config.LISTEN
        elif params[1] == config.CTS: 
            return config.QUIET
        else:
            return config.QUIET
    
    return config.LISTEN


def decrementContacted(contacted: dict[int, int]) -> dict[int, int]:
    """"
    Decrements the TTL for each key in contacted, removing anything with a TTL of 0

    Args:
        contacted (dict[int, int]): The dictionary of contacted nodes, key is node address, value is TTL

    Returns:
        dict[int, int]: The modified dictionary
    """

    for key in contacted:
        contacted[key]+=-1
        if contacted[key]==0:
            del(contacted[key])
    
    return contacted




# Initialise the radio
spi = SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

# TODO - Initialise GPS (ah fuck this is gonna be a nightmare bc we're gonna have to put it in a seperate file with a lock so that both the app and networking layer can read from it)

# Set to True if we want to use the contacted list
useContacted = True

# List of nodes we have contacted recently
contacted: dict[int, str]
contacted = {}

# Dictionary of messages that we have - similar to the list of obstacles in the application layer
# The key is two bytes long, source (1byte) and time (1byte) then the list contains the message (GPS location, TTL of location) and the message's TTL
# {key : [GPS1, GPS2, TTL]}
messages: dict[int, list[int]]
messages = {}


# Node we waiting to overhear an ACK from before we can exit QUIET state
quietNode: int

# Initialise state to the starting state 
state = config.LISTEN

timers = Timers()
while True:
    if state == config.LISTEN:
        args = rfm69.receive()
        state = handleReceive(args)

    elif state == config.SEND_HELLO:
        if sendHello():
            state = config.LISTEN

    elif state == config.RECEIVED_HELLO:
        sender = args[2]
        packet = args[4]
        sendToAppLayer(packet)
        if sender not in contacted:
            if sender>config.ADDRESS:
                success, messages = RTSAntiEntropy(dest = sender, messages = messages)
                if useContacted and success:
                    contacted.update({sender : config.CONTACTED_LIVES})
        state = config.LISTEN

    elif state == config.QUIET:
        args = rfm69.receive()
        if args is not None:
            pass
        state = handleReceive(args)

    elif state == config.RECEIVED_RTS:
        success, messages = CTSAntiEntropy(sender = args[2], messages = messages, RTSpacket = args[4])
        state = config.LISTEN
        # No point updating contacted as will not attempt to contact a node with larger address

    state = config.LISTEN


    # Poll timers (best we can do due to lack of interrupt support in CircuitPython)
    if useContacted and timers.contacted():
        contacted = decrementContacted(contacted)

    # This is lazy and timers.hello is not called if state!=LISTEN  (timers.hello() has side effects on the state of the hello timer)
    if state == config.LISTEN and timers.hello():
        state = config.SEND_HELLO