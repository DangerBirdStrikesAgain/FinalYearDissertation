"""
Alex Riddell-Webster
Modified from adafruit_rmf69 by Tony DiCola, Jerry Needell

Designed to send and recieve packets with Adafruit's RFM69HCW transceiver radio breakout, to support an implementation of Epidemic routing
with media access control

Software and Dependencies:
    Adafruit CircuitPython firmware for the ESP8622 and M0-based boards: https://github.com/adafruit/circuitpython/releases
    Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""


import time
import adafruit_bus_device.spi_device as spidev
from micropython import const
import config 
from digitalio import DigitalInOut
from busio import SPI

# Supervisor for timing
import supervisor
HAS_SUPERVISOR = hasattr(supervisor, "ticks_ms")


# Internal constants:
_REG_FIFO = const(0x00)
_REG_OP_MODE = const(0x01)
_REG_DATA_MOD = const(0x02)
_REG_BITRATE_MSB = const(0x03)
_REG_BITRATE_LSB = const(0x04)
_REG_FDEV_MSB = const(0x05)
_REG_FDEV_LSB = const(0x06)
_REG_FRF_MSB = const(0x07)
_REG_FRF_MID = const(0x08)
_REG_FRF_LSB = const(0x09)
_REG_VERSION = const(0x10)
_REG_PA_LEVEL = const(0x11)
_REG_RX_BW = const(0x19)
_REG_AFC_BW = const(0x1A)
_REG_RSSI_VALUE = const(0x24)
_REG_DIO_MAPPING1 = const(0x25)
_REG_IRQ_FLAGS1 = const(0x27)
_REG_IRQ_FLAGS2 = const(0x28)
_REG_PREAMBLE_MSB = const(0x2C)
_REG_PREAMBLE_LSB = const(0x2D)
_REG_SYNC_CONFIG = const(0x2E)
_REG_SYNC_VALUE1 = const(0x2F)
_REG_PACKET_CONFIG1 = const(0x37)
_REG_FIFO_THRESH = const(0x3C)
_REG_PACKET_CONFIG2 = const(0x3D)
_REG_AES_KEY1 = const(0x3E)
_REG_TEMP1 = const(0x4E)
_REG_TEMP2 = const(0x4F)
_REG_TEST_PA1 = const(0x5A)
_REG_TEST_PA2 = const(0x5C)
_REG_TEST_DAGC = const(0x6F)

_TEST_PA1_NORMAL = const(0x55)
_TEST_PA1_BOOST = const(0x5D)
_TEST_PA2_NORMAL = const(0x70)
_TEST_PA2_BOOST = const(0x7C)

# The crystal oscillator frequency and frequency synthesizer step size.
_FXOSC = 32000000.0
_FSTEP = _FXOSC / 524288


# User facing constants:
SLEEP_MODE = 0b000
STANDBY_MODE = 0b001
FS_MODE = 0b010
TX_MODE = 0b011
RX_MODE = 0b100

# supervisor.ticks_ms() constants
_TICKS_PERIOD = const(1 << 29)
_TICKS_MAX = const(_TICKS_PERIOD - 1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD // 2)


def ticks_diff(ticks1: int, ticks2: int) -> int:
    """
    Compute the signed difference between two ticks values
    Assumes that they are within 2**28 ticks

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
        limit (float): The 

    Returns:
        bool: True if timeout, otherwise False
    """
    temp = 0
    start = supervisor.ticks_ms()
    while not flag():
        temp = ticks_diff(supervisor.ticks_ms(), start)
        if temp >= limit * 1000:
            # timeout
            return True

    return False


class RFM69:
    """
    Interface to a RFM69 series packet radio.  Allows simple sending and
    receiving of wireless data at supported frequencies of the radio
    (433/915mhz).

    Note: The D0/interrupt line is currently unused by this module and can remain unconnected.

    Remember this library makes a best effort at receiving packets with pure Python code.  Trying
    to receive packets too quickly will result in lost data so limit yourself to simple scenarios
    of sending and receiving single packets at a time.
    """

    # Global buffer for SPI commands.
    _BUFFER = bytearray(4)

    class _RegisterBits:
        # Class to simplify access to the many configuration bits available
        # on the chip's registers.  This is a subclass here instead of using
        # a higher level module to increase the efficiency of memory usage
        # (all of the instances of this bit class will share the same buffer
        # used by the parent RFM69 class instance vs. each having their own
        # buffer and taking too much memory).


        def __init__(self, address: int, *, offset: int = 0, bits: int = 1) -> None:
            assert 0 <= offset <= 7
            assert 1 <= bits <= 8
            assert (offset + bits) <= 8
            self._address = address
            self._mask = 0
            for _ in range(bits):
                self._mask <<= 1
                self._mask |= 1
            self._mask <<= offset
            self._offset = offset

        def __get__(self, obj: Optional["RFM69"], objtype: Type["RFM69"]):
            reg_value = obj._read_u8(self._address)
            return (reg_value & self._mask) >> self._offset

        def __set__(self, obj: Optional["RFM69"], val: int) -> None:
            reg_value = obj._read_u8(self._address)
            reg_value &= ~self._mask
            reg_value |= (val & 0xFF) << self._offset
            obj._write_u8(self._address, reg_value)

    # Control bits from the registers of the chip:
    data_mode = _RegisterBits(_REG_DATA_MOD, offset=5, bits=2)
    modulation_type = _RegisterBits(_REG_DATA_MOD, offset=3, bits=2)
    modulation_shaping = _RegisterBits(_REG_DATA_MOD, offset=0, bits=2)
    temp_start = _RegisterBits(_REG_TEMP1, offset=3)
    temp_running = _RegisterBits(_REG_TEMP1, offset=2)
    sync_on = _RegisterBits(_REG_SYNC_CONFIG, offset=7)
    sync_size = _RegisterBits(_REG_SYNC_CONFIG, offset=3, bits=3)
    aes_on = _RegisterBits(_REG_PACKET_CONFIG2, offset=0)
    pa_0_on = _RegisterBits(_REG_PA_LEVEL, offset=7)
    pa_1_on = _RegisterBits(_REG_PA_LEVEL, offset=6)
    pa_2_on = _RegisterBits(_REG_PA_LEVEL, offset=5)
    output_power = _RegisterBits(_REG_PA_LEVEL, offset=0, bits=5)
    rx_bw_dcc_freq = _RegisterBits(_REG_RX_BW, offset=5, bits=3)
    rx_bw_mantissa = _RegisterBits(_REG_RX_BW, offset=3, bits=2)
    rx_bw_exponent = _RegisterBits(_REG_RX_BW, offset=0, bits=3)
    afc_bw_dcc_freq = _RegisterBits(_REG_AFC_BW, offset=5, bits=3)
    afc_bw_mantissa = _RegisterBits(_REG_AFC_BW, offset=3, bits=2)
    afc_bw_exponent = _RegisterBits(_REG_AFC_BW, offset=0, bits=3)
    packet_format = _RegisterBits(_REG_PACKET_CONFIG1, offset=7, bits=1)
    dc_free = _RegisterBits(_REG_PACKET_CONFIG1, offset=5, bits=2)
    crc_on = _RegisterBits(_REG_PACKET_CONFIG1, offset=4, bits=1)
    crc_auto_clear_off = _RegisterBits(_REG_PACKET_CONFIG1, offset=3, bits=1)
    address_filter = _RegisterBits(_REG_PACKET_CONFIG1, offset=1, bits=2)
    mode_ready = _RegisterBits(_REG_IRQ_FLAGS1, offset=7)
    dio_0_mapping = _RegisterBits(_REG_DIO_MAPPING1, offset=6, bits=2)


    def __init__(  
        self,
        spi: SPI,
        cs: DigitalInOut,
        reset: DigitalInOut,
        frequency: int,
        *,
        sync_word: bytes = b"\x2D\xD4",
        baudrate: int = 2000000,
        fixed_length: bool = True
    ) -> None:
        """
        Initialise the RFM69 chip 

        Args:
            spi (busio.SPI): The SPI bus
            cs (digitalio.DigitalInOut): A DigitalInOut object connected to the chip's CS/chip select line
            reset (digitalio.DigitalInOut): A DigitalInOut object connected to the chip's RST/reset line
            frequency (int): The center frequency to configure for radio transmission and reception, must be supported by hardware (i.e. either 433 or 915mhz).
            sync_word (bytes): A network wide byte string up to 8 bytes long which represents the syncronization
            word used by received and transmitted packets
            fixed_length (bool): A bool choosing if the length of the packets is fixed, default True
        """    
        self._tx_power = config.TX_POWER
        self.high_power = True
        # Device support SPI mode 0 (polarity & phase = 0) up to a max of 10mhz.
        self._device = spidev.SPIDevice(spi, cs, baudrate=baudrate, polarity=0, phase=0)
        # Setup reset as a digital output that's low.
        self._reset = reset
        self._reset.switch_to_output(value=False)
        # Reset chip
        self.reset() 
        # Check the version of the chip.
        version = self._read_u8(_REG_VERSION)
        if version != 0x24:
            raise RuntimeError("Failed to find RFM69 with expected version, check wiring, soldering, gremlins and if you're using Blinka with MicroPython")

        # Enter idle state
        self.idle() 

        # Set FIFO TX condition to not empty and the default FIFO threshold to 15.
        self._write_u8(_REG_FIFO_THRESH, 0b10001111)
        # Configure low beta off.
        self._write_u8(_REG_TEST_DAGC, 0x30)
        self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
        self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        self.sync_word = sync_word
        self.frequency_mhz = frequency  # Set frequency
        self.encryption_key = None  # Set encryption key
        self.modulation_shaping = 0b01  # Gaussian filter, BT=1.0
        self.bitrate = 250000  # 250kbs
        self.frequency_deviation = 250000  # 250khz
        self.rx_bw_dcc_freq = 0b111  # RxBw register = 0xE0
        self.rx_bw_mantissa = 0b00
        self.rx_bw_exponent = 0b000
        self.afc_bw_dcc_freq = 0b111  # AfcBw register = 0xE0
        self.afc_bw_mantissa = 0b00
        self.afc_bw_exponent = 0b000
        if fixed_length:
            self.packet_format = 0  
        else:
            self.packet_format = 1 # Variable length.
        
        self.dc_free = 0b10  # Whitening
        # Set transmit power to 13 dBm, a safe value any module supports.
        self.tx_power = config.TX_POWER

        # initialize last RSSI reading
        self.last_rssi = 0.0
        """
        The RSSI of the last received packet. Stored when the packet was received.
        This instantaneous RSSI value may not be accurate once the
        operating mode has been changed.
        """     
        # initialize sequence number counter for reliabe datagram mode
        self.sequence_number = 0
        # create seen Ids list
        self.seen_ids = bytearray(256)

    def _read_into(self, address: int, buf: WriteableBuffer, length: Optional[int] = None) -> None:
        """
        Read a number of bytes from the specified address into the provided buffer
        If length is not specified, the entire buffer will be filled
        """
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = address & 0x7F  # Strip out top bit to set 0
            # value (read).
            device.write(self._BUFFER, end=1)
            device.readinto(buf, end=length)

    def _read_u8(self, address: int) -> int:
        """
        Read a single byte from the provided address and return it
        """

        self._read_into(address, self._BUFFER, length=1)
        return self._BUFFER[0]

    def _write_from(self, address: int, buf: ReadableBuffer, length: Optional[int] = None) -> None:
        """
        Write a number of bytes to the provided address and taken from the provided buffer
        If no length is specified (the default) the entire buffer is written
        """
        if length is None:
            length = len(buf)
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            device.write(self._BUFFER, end=1)
            device.write(buf, end=length)  # send data

    def _write_u8(self, address: int, val: int) -> None:
        # Write a byte register to the chip.  Specify the 7-bit address and the
        # 8-bit value to write to that address.
        with self._device as device:
            self._BUFFER[0] = (address | 0x80) & 0xFF  # Set top bit to 1 to
            # indicate a write.
            self._BUFFER[1] = val & 0xFF
            device.write(self._BUFFER, end=2)

    def reset(self) -> None:
        """
        Performs a reset of the chip as defined in section 7.2.2 of the datasheet
        """
        self._reset.value = True
        time.sleep(0.0001)  # 100 us
        self._reset.value = False
        time.sleep(0.005)  # 5 ms

    def idle(self) -> None:
        """
        Enter idle standby mode 
        (switching off high power amplifiers / mode / boost  if on)
        """
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        self.operation_mode = STANDBY_MODE

    def sleep(self) -> None:
        """
        Enter sleep mode
        """
        self.operation_mode = SLEEP_MODE

    def listen(self) -> None:
        """
        Listen for packets to be received by the chip
        Used by receive()
        """
        # Turn off high power boost if enabled.
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_NORMAL)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_NORMAL)
        # Enable payload ready interrupt for D0 line
        self.dio_0_mapping = 0b01
        # Enter RX mode (will clear FIFO!)
        self.operation_mode = RX_MODE

    def transmit(self) -> None:
        """
        Transmit a packet which is queued in the FIFO
        This is a low level function for entering transmit mode and more
        """
        # Turn on high power boost if enabled
        if self._tx_power >= 18:
            self._write_u8(_REG_TEST_PA1, _TEST_PA1_BOOST)
            self._write_u8(_REG_TEST_PA2, _TEST_PA2_BOOST)
        # Enable packet sent interrupt for D0 line.
        self.dio_0_mapping = 0b00
        # Enter TX mode (will clear FIFO!).
        self.operation_mode = TX_MODE

    @property
    def temperature(self) -> float:
        """
        Returns the internal temperature of the chip in degrees Celsius
        Not calibrated or very accurate

        Reading this will STOP any receiving/sending that might be happening!
        """
        # Start a measurement then poll the measurement finished bit
        self.temp_start = 1
        while self.temp_running > 0:
            pass
        # Grab the temperature value and convert it to Celsius
        temp = self._read_u8(_REG_TEMP2)
        return 166.0 - temp

    @property
    def operation_mode(self) -> int:
        """
        The operation mode value
        Unless you're manually controlling the chip you shouldn't change the operation_mode with this property 
        as other side-effects are required for changing logical modes
        use :py:func:`idle`, :py:func:`sleep`, :py:func:`transmit`, :py:func:`listen` instead to signal intent for explicit logical mode
        """
        op_mode = self._read_u8(_REG_OP_MODE)
        return (op_mode >> 2) & 0b111

    @operation_mode.setter
    def operation_mode(self, val: int) -> None:
        """
        Sets the operation mode of the chip 
        """
        assert 0 <= val <= 4
        # Set the mode bits inside the operation mode register.
        op_mode = self._read_u8(_REG_OP_MODE)
        op_mode &= 0b11100011
        op_mode |= val << 2
        self._write_u8(_REG_OP_MODE, op_mode)
        # Wait for mode to change by polling interrupt bit.
        if HAS_SUPERVISOR:
            start = supervisor.ticks_ms()
            while not self.mode_ready:
                if ticks_diff(supervisor.ticks_ms(), start) >= 1000:
                    raise TimeoutError("Operation Mode failed to set")
        else:
            start = time.monotonic()
            while not self.mode_ready:
                if time.monotonic() - start >= 1:
                    raise TimeoutError("Operation Mode failed to set")

    @property
    def sync_word(self) -> bytearray:
        """
        The synchronization word value
        This is a byte string up to 8 bytes long (64 bits) which indicates the synchronization word for transmitted and received packets
        Any received packet which does not include this sync word will be ignored
        Setting a value of None will disable synchronization word matching
        """
        # When sync word is disabled
        if not self.sync_on:
            return None

        # Sync word is not disabled so read the current value
        sync_word_length = self.sync_size + 1  # Sync word size is offset by 1
        # According to datasheet
        sync_word = bytearray(sync_word_length)
        self._read_into(_REG_SYNC_VALUE1, sync_word)
        return sync_word

    @sync_word.setter
    def sync_word(self, val: Optional[bytearray]) -> None:
        """
        Sets the synchronisation word
        """
        # Handle disabling sync word when None value is set.
        if val is None:
            self.sync_on = 0
        else:
            # Check sync word is at most 8 bytes.
            assert 1 <= len(val) <= 8
            # Update the value, size and turn on the sync word.
            self._write_from(_REG_SYNC_VALUE1, val)
            self.sync_size = len(val) - 1  # Again sync word size is offset by
            # 1 according to datasheet.
            self.sync_on = 1

    @property
    def preamble_length(self) -> int:
        """
        The length of the preamble for sent and received packets, an unsigned 16-bit value
        Received packets must match this length or they are ignored! Set to 4 to match the
        RadioHead RFM69 library.
        """
        msb = self._read_u8(_REG_PREAMBLE_MSB)
        lsb = self._read_u8(_REG_PREAMBLE_LSB)
        return ((msb << 8) | lsb) & 0xFFFF

    @preamble_length.setter
    def preamble_length(self, val: int) -> None:
        """
        Set the preamble length
        """
        assert 0 <= val <= 65535
        self._write_u8(_REG_PREAMBLE_MSB, (val >> 8) & 0xFF)
        self._write_u8(_REG_PREAMBLE_LSB, val & 0xFF)

    @property
    def frequency_mhz(self) -> float:
        """
        The frequency of the radio in Megahertz
        Only the allowed values for your radio must be specified (i.e. 433 vs. 915 mhz)
        FRF register is computed from the frequency following the datasheet
        See section 6.2 and FRF register description
        """
        # Read bytes of FRF register and assemble into a 24-bit unsigned value.
        msb = self._read_u8(_REG_FRF_MSB)
        mid = self._read_u8(_REG_FRF_MID)
        lsb = self._read_u8(_REG_FRF_LSB)
        frf = ((msb << 16) | (mid << 8) | lsb) & 0xFFFFFF
        frequency = (frf * _FSTEP) / 1000000.0
        return frequency

    @frequency_mhz.setter
    def frequency_mhz(self, val: float) -> None:
        """
        Sets chip frequency 
        """
        assert 290 <= val <= 1020
        # Calculate FRF register 24-bit value using section 6.2 of the datasheet.
        frf = int((val * 1000000.0) / _FSTEP) & 0xFFFFFF
        # Extract byte values and update registers.
        msb = frf >> 16
        mid = (frf >> 8) & 0xFF
        lsb = frf & 0xFF
        self._write_u8(_REG_FRF_MSB, msb)
        self._write_u8(_REG_FRF_MID, mid)
        self._write_u8(_REG_FRF_LSB, lsb)

    @property
    def tx_power(self) -> int:
        """
        The transmit power in dBm. Can be set to a value from -2 to 20 for high power devices
        (RFM69HCW, high_power=True) or -18 to 13 for low power devices
        Only integer power levels are actually set (i.e. 12.5 will result in a value of 12 dBm)
        """
        # Follow table 10 truth table from the datasheet for determining power
        # level from the individual PA level bits and output power register.
        pa0 = self.pa_0_on
        pa1 = self.pa_1_on
        pa2 = self.pa_2_on
        if pa0 and not pa1 and not pa2:
            # -18 to 13 dBm range
            return -18 + self.output_power
        if not pa0 and pa1 and not pa2:
            # -2 to 13 dBm range
            return -18 + self.output_power
        if not pa0 and pa1 and pa2 and not self.high_power:
            # 2 to 17 dBm range
            return -14 + self.output_power
        if not pa0 and pa1 and pa2 and self.high_power:
            # 5 to 20 dBm range
            return -11 + self.output_power
        raise RuntimeError("Power amplifiers in unknown state!")

    @tx_power.setter
    def tx_power(self, val: float):
        val = int(val)
        # Determine power amplifier and output power values depending on
        # high power state and requested power.
        pa_0_on = 0
        pa_1_on = 0
        pa_2_on = 0
        output_power = 0
        if self.high_power:
            # Handle high power mode.
            assert -2 <= val <= 20
            if val <= 13:
                pa_1_on = 1
                output_power = val + 18
            elif 13 < val <= 17:
                pa_1_on = 1
                pa_2_on = 1
                output_power = val + 14
            else:  # power >= 18 dBm
                # Note this also needs PA boost enabled separately!
                pa_1_on = 1
                pa_2_on = 1
                output_power = val + 11
        else:
            # Handle non-high power mode.
            assert -18 <= val <= 13
            # Enable only power amplifier 0 and set output power.
            pa_0_on = 1
            output_power = val + 18
        # Set power amplifiers and output power as computed above.
        self.pa_0_on = pa_0_on
        self.pa_1_on = pa_1_on
        self.pa_2_on = pa_2_on
        self.output_power = output_power
        self._tx_power = val

    @property
    def rssi(self) -> float:
        """
        The received strength indicator (in dBm).
        May be inaccuate if not read immediately 
        last_rssi contains the value read from receipt of the last packet
        """
        # Read RSSI register and convert to value using formula in datasheet.
        return -self._read_u8(_REG_RSSI_VALUE) / 2.0

    @property
    def bitrate(self) -> float:
        """
        The modulation bitrate in bits/second (or chip rate if Manchester encoding is enabled).
        Can be a value from ~489 to 32mbit/s, but see the datasheet for the exact supported
        values
        """
        msb = self._read_u8(_REG_BITRATE_MSB)
        lsb = self._read_u8(_REG_BITRATE_LSB)
        return _FXOSC / ((msb << 8) | lsb)

    @bitrate.setter
    def bitrate(self, val: float) -> None:
        assert (_FXOSC / 65535) <= val <= 32000000.0
        # Round up to the next closest bit-rate value with addition of 0.5.
        bitrate = int((_FXOSC / val) + 0.5) & 0xFFFF
        self._write_u8(_REG_BITRATE_MSB, bitrate >> 8)
        self._write_u8(_REG_BITRATE_LSB, bitrate & 0xFF)

    @property
    def frequency_deviation(self) -> float:
        """
        The frequency deviation in Hertz
        """
        msb = self._read_u8(_REG_FDEV_MSB)
        lsb = self._read_u8(_REG_FDEV_LSB)
        return _FSTEP * ((msb << 8) | lsb)

    @frequency_deviation.setter
    def frequency_deviation(self, val: float) -> None:
        assert 0 <= val <= (_FSTEP * 16383)  # fdev is a 14-bit unsigned value
        # Round up to the next closest integer value with addition of 0.5.
        fdev = int((val / _FSTEP) + 0.5) & 0x3FFF
        self._write_u8(_REG_FDEV_MSB, fdev >> 8)
        self._write_u8(_REG_FDEV_LSB, fdev & 0xFF)

    def packet_sent(self) -> bool:
        """
        Transmit status
        """
        return (self._read_u8(_REG_IRQ_FLAGS2) & 0x8) >> 3

    def payload_ready(self) -> bool:
        """
        Receive status
        """
        return (self._read_u8(_REG_IRQ_FLAGS2) & 0x4) >> 2

    def send(
        self,
        data: ReadableBuffer,
        destination: int,
        packetType: int
    ) -> bool:
        """
        Send a string of data using the transmitter
        Can only send 60 bytes at a time - limited by chip's FIFO size of 64 bytes and headers
        
        Args: 
            data (ReadableBuffer): The data to be transmitted
            destination (int): The destination address for the packet
            packetType (int): The type of the packet

        Returns: 
            bool: True if success and False if failure
        """

        # Variable length
        if self.packet_format == 1:
            if not (len(data) <= 60):
                return False
        # Fixed length
        else:
            if len(data) < 60:
                data = data + b'0'*(60-len(data))
            if len(data) != 60:
                return False
        
        # Stop receiving to clear FIFO and keep it clear
        self.idle()
        
        payload = bytearray(4)
        payload[0] = 4 + len(data)
        payload[1] = packetType
        payload[2] = config.ADDRESS
        payload[3] = destination
        payload = payload + data
        
        # Write payload to transmit fifo
        self._write_from(_REG_FIFO, payload)
        time.sleep(0.1)
        # Turn on transmit mode to send out the packet
        self.transmit()
        # Wait for packet sent interrupt with explicit polling
        # (not ideal but best that can be done without interrupts)
        timed_out = check_timeout(self.packet_sent, config.TRANSMIT_TIMEOUT)
        # Enter idle mode to stop transmitting everything
        self.idle()
        
        return not timed_out


    def receive(self, timeout: Optional[int] = config.RECEIVE_TIMEOUT) -> tuple[Any]:
        """
        Listen for packets 
        If a packet is recieved, it is returned, otherwise None is returned
        (which indicates the timeout elapsed with no reception)

        Args:
            None

        Returns:
            int: The length of the packet in bytes (including 4 byte headers)
            int: The type of the packet
            int: The address of the sender
            int: The destination address
            bytearray: The packet data
        """
        
        packet = None
        packetLength = None
        packetType = None
        sender = None
        destination = None

        timed_out = False
        self.idle()
        # Listen for packets
        self.listen()
        
        # Wait for the payload_ready signal.  This is not ideal and will
        # surely miss or overflow the FIFO when packets aren't read fast
        # enough, however it's the best that can be done from Python without
        # interrupt supports
        timed_out = check_timeout(self.payload_ready, timeout)

        
        if not timed_out:
            # Read the length of the FIFO - requires the first byte to be the length
            # Fairly sure this is a destructive read 
            packetLength = self._read_u8(_REG_FIFO)
            # read and clear the FIFO if anything in 
            if packetLength > 0:
                packet = bytearray(packetLength-1)
                self._read_into(_REG_FIFO, packet, (packetLength-1))
                packetType = packet[0]
                sender = packet[1]
                destination = packet[2]

        # Enter idle mode to stop receiving other packets
        self.idle()
        time.sleep(0.1)

        if packet is not None:
            return (packetLength, packetType, sender, destination, packet[3:]) 
        else: 
            return packet