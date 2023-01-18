"""
A Circuit Python implmentation of the epidemic routing protocol with media access control
Based on the paper by Amin Vahdat and David Becker: https://issg.cs.duke.edu/epidemic/epidemic.pdf

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

# TODO - Restructure the messages data structure to be {int : [int int int]}
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

#TODO make time to live the number of times the packet is forwarded 
# ADd to contacted only if successful
# Move to fixed length and have 64 bytes every time / padded

def sendToAppLayer(item):
    """
    TODO - implement this using global variable(s)
    """
    return True


def getFromAppLayer(item):
    """
    TODO - make this work and poll it every so often (no interupts) to make sure we don't miss anything
    """


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
        self._messages = self._ticksAdd(supervisor.ticks_ms(), config.MESSAGES_TIMER)
        self._ACKTimeout: int

        log(("Supervisor time at start: " + str(supervisor.ticks_ms())))
        


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
        else: 
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
        else:
            return False

    def messages(self) -> bool:
        """
        Checks if the timer for decrementing the messages TTL has elapsed

        Args:
            None

        Returns:
            bool: True if the timer has elapsed, otherwise False
        """

        if self._ticksDiff(self._messages, supervisor.ticks_ms()) < 0:
            self._messages = self._ticksAdd(supervisor.ticks_ms(), config.MESSAGES_TIMER)
            return True
        else: 
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
        else: 
            return False


def log(message: str):
    """ 
    If global variable logging is true, prints message
    
    Args:
        message (str): The string to be printed
    
    Returns:
        None
    """
    
    global logging
    if logging:
        print(message)


def getGPS():
    """
    TODO
    """
    # TODO - should this be a string? Is there a better way of doing this?
    return ("10.284638,89.473057")


def sendHello() -> bool:
    """
    Sends a packet of type HELLO
    
    Args: 
        None 
    
    Returns:
        bool: True if success, False if error
    """

    gps = getGPS()
    return rfm69.send(data = bytes(gps, "utf-8"), destination = config.BROADCAST, packetType = config.HELLO)


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
    lowestTTL = messagesList[0][1][1]

    for item in messagesList:
        if item[1][1] < lowestTTL:
            lowestTTL = item[1][1]
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
            messages.update({temp[0] : [str(temp[1]+","+temp[2]), temp[3]]})
    
    return messages


def getData(sender: int, packet: Optional[str] = None) -> tuple(bool, dict):
    """
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
            if args[1] == config.DATA and args[2] == sender: 
                packet = args[4]
            dataCount+=1
    
    if packet is None:
        log("No DATA packets received")
        return (False, {})

    dataCount = 0

    # Construct a list of zeros from the packet, if more than one packet will be sent
    totalLen = packet[0]
    if totalLen != 0:
        seen = [0]*(totalLen-1)
        receivedMessages.append(packet[2:])
        seen[packet[1]]=1
    else: 
        seen = [0]
        receivedMessages=str(packet[2:], "utf_8")

    while sum(seen) != totalLen and dataCount<config.DATA_REENTRIES:
        args = rfm69.receive()
        if args[1] == config.DATA and args[2] == sender: 
            packet = args[4]
            if seen[packet[1]] == 0:
                receivedMessages.append(str(packet[2:], "utf_8"))
                seen[packet[1]]=1
        dataCount+=1

    messages = decodeMessages(receivedMessages)

    if sum(seen) == totalLen:
        return(True, messages)
    else:
        return (False, messages)


def sendDataFrames(dest: int, messages: dict):
    """
    Sends data frames until an ACK or another data frame (indicating receipt) is received from the destination
    
    Args:
        dest (int): The destination of the data frames
        messages (dict): The dictionary of messages to be sent

    Returns:
        bool: True if success, False otherwise
    """

    dataCount = 0
    ACK = False
    
    log("In send data frames function")

    # If there are no messages to send
    if len(messages) == 0:
        log("starting to send now")
        while dataCount<=config.DATA_REENTRIES and not ACK:
            prefix = bytearray(2)
            prefix[0] = 0
            prefix[1] = 0
            rfm69.send(data = prefix, destination = dest, packetType = config.DATA)
            time.sleep(0.1)
            args = rfm69.receive(timeout = 3)
            if args is not None and args[2] == dest and (args[1] == config.DATA or args[1] == config.ACK):
                ACK = True
        
        if ACK:
            return (True, args)
        else:
            log("ACK or data frame not received")
            return (False, None)

    else:
        # Generate the data frames to be sent and put them into a list
        toSend = []
        string=""
        for key in messages:
            msg = str(key)+","+messages[key][0]+","+str(messages[key][1])+"\n"
            if len(string) + len(msg) > 58:
                toSend.append(string)
                string = msg
            else: 
                string = string + msg

        total = len(toSend)
        log("starting to send NOW")
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
                time.sleep(0.2)

            dataCount+=1
            args = rfm69.receive(timeout = 3)
            if args is not None and args[2] == dest and (args[1] == config.DATA or args[1] == config.ACK):
                ACK = True
    
        if ACK:
            return (True, args)
        else:
            log("ACK or data frame not received")
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
        log(("args: " + str(args)))
        if args is not None and args[1] == config.CTS and args[2] == dest:
            CTS = True
    
    # Indicates failure to receive a CTS
    if RTSCount>=config.TS_REENTRIES and not CTS:
        log("No CTS received, RTS timeout!!")
        return (False, messages)
    
    # We receive a CTS from the desired node
    else:
        log("CTS recieved")
        log("Sending data frames")
        packet = args[4]
        destKeys = []
        messagesToSend = {}
        if len(packet) != 0:
            for x in range (0, len(packet), 2):
                destKeys.append(int.from_bytes(packet[x:(x+2)], "utf_8"))
            for key in messages:
                if key not in destKeys:
                    messagesToSend.update({key : messages[key]})
        success, args = sendDataFrames(dest, messagesToSend)
        if not success:
            return (False, messages)
        else: 
            success, newMessages = getData(args[4])
            if success:
                param = None
                sendCount = 0
                while param is None and sendCount<config.ACK_REENTRIES:
                    time.sleep(0.1)
                    rfm69.send(data = b'', destination = dest, packetType = config.ACK)
                    param = rfm69.receive(timeout = 2)
            
            if newMessages != {}:
                sendToAppLayer(newMessages)
                messages.update(newMessages)
                while len(messages)>30:
                    messages = removeLowestMessage(messages = messages)

            return (success, messages)        


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


def CTSAntiEntropy(sender: int, messages: dict, packet: bytearray) -> dict:
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
    data = False

    while CTSCount<config.TS_REENTRIES and not data:
        sendCTS(sender, messages)
        CTSCount+=1
        args = rfm69.receive(timeout=2)
        log(("args: " + str(args)))
        if args is not None and args[1] == config.DATA and args[2] == sender:
            data = True
        time.sleep(0.2)

    # Indicates failure to receive a data frame
    if not data:
        log("No data frames received, CTS timeout!!")
        return messages
    
    # We receive a data frame from the desired node
    else:
        log("first DATA recieved, moving onto receving all data")
        success, newMessages = getData(sender = sender, packet = args[4])


        if success:
            log("All data frames received, now sending out data")
            # Generate keys the other node wants
            destKeys = []
            messagesToSend = {}
            if len(packet) != 0:
                for x in range (0, len(packet), 2):
                    destKeys.append(int.from_bytes(packet[x:(x+2)], "utf_8"))
                for key in messages:
                    if key not in destKeys:
                        messagesToSend.update({key : messages[key]})
            success, args = sendDataFrames(sender, messagesToSend)

        if newMessages != {}:
            sendToAppLayer(newMessages)
            messages.update(newMessages)
            while len(messages)>30:
                messages = removeLowestMessage(messages = messages)

        return messages


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
        elif params[1] == config.CTS: # and args[2]!=config.ADDRESS:
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
            message = "Saw an unknown packet type: ", params[1]
            log(message)
            return config.LISTEN
            
    elif state==config.QUIET: 
        if timers.quiet():
            return config.LISTEN
        elif params == None or params[1] == config.DATA or params[1]==config.HELLO or params[1]==config.RTS:
            return config.QUIET
        elif (params[1] == config.ACK and params[2] == quietNode):
            return config.LISTEN
        elif params[1] == config.CTS: # and args[2]!=config.ADDRESS: 
            # TODO - should we actually be doing something about this? Currently we just assume that we won't see two CTSs from different nodes
            return config.QUIET
        else:
            message = "Saw an unknown packet type: ", params[1]
            log(message)
            return config.QUIET
    
    else:
        log(("handleReceive was called in state: " + str(state)))
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


def decrementMessages(messages: dict) -> dict:
    """"
    Decrements the TTL for each item in messages, removing anything with a TTL of 0

    Args:
        contacted (dict): The dictionary of messages, where the second item in the value is the TLL

    Returns:
        dict: The modified messages dictionary
    """

    for key in messages:
        messages[key][1]+=-1
        if messages[key][1]==0:
            del(messages[key])
    
    return messages



# Initialise the radio
spi = SPI(board.GP2, MOSI=board.GP3, MISO=board.GP0)
cs = digitalio.DigitalInOut(board.GP1)
reset = digitalio.DigitalInOut(board.GP4)
rfm69 = rfm69.RFM69(spi, cs, reset, config.FREQUENCY)

# TODO - Initialise GPS (ah fuck this is gonna be a nightmare bc we're gonna have to put it in a seperate file with a lock so that both the app and networking layer can read from it)

# Set to True if we want to use the contacted list
useContacted = False

# List of nodes we have contacted recently
contacted: dict[int, str]
contacted = {}

# Dictionary of messages that we have - similar to the list of obstacles in the application layer
# The key is two bytes long, source (1byte) and time (1byte) then the list contains the message (GPS location, TTL of location) and the message's TTL
messages: dict[int, list[str, int]]
messages = {}


# Node we waiting to overhear an ACK from before we can exit QUIET state
quietNode: int

# Initialise state to the starting state 
state = config.LISTEN

# Logging turned on if we have a USB connection
logging = supervisor.runtime.serial_connected
log("Logging")

timers = Timers()
print(messages)

while True:
    # log(message = "State: " + str(state))
    if state == config.LISTEN:
        args = rfm69.receive()
        state = handleReceive(args)

    elif state == config.SEND_HELLO:
        if sendHello():
            log("Sent hello")
            state = config.LISTEN
        else:
            log("Failed to send hello")

    elif state == config.RECEIVED_HELLO:
        log("Received hello")
        sender = args[2]
        packet = args[4]
        sendToAppLayer(packet)
        if sender not in contacted:
            if sender>config.ADDRESS:
                success, messages = RTSAntiEntropy(dest = sender, messages = messages)
                if useContacted and success:
                    contacted.update({sender : config.CONTACTED_LIVES})
                print(messages)
        state = config.LISTEN

    elif state == config.QUIET:
        args = rfm69.receive()
        if args is not None:
            log(args)
        state = handleReceive(args)

    elif state == config.RECEIVED_RTS:
        print("Received RTS")
        print(messages)
        messages = CTSAntiEntropy(sender = args[2], messages = messages, packet = args[4])
        state = config.LISTEN
        # No point updating contacted as will not attempt to contact a node with larger address
        print(messages)

    else:
        log(("Saw an unknown state: " + str(state)))
        state = config.LISTEN


    # Poll timers (best we can do due to lack of interrupt support in CircuitPython)
    if useContacted and timers.contacted():
        contacted = decrementContacted(contacted)
    if timers.messages():
        messages = decrementMessages(messages)

    # This is lazy and timers.hello is not called if state!=LISTEN  (important timers.hello() as has side effects on the state of the hello timer)
    if state == config.LISTEN and timers.hello():
        state = config.SEND_HELLO