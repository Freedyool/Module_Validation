# The MIT License (MIT)
#
# Copyright (c) 2019 Barbudor (IRL Jean-Michel Mercier)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Driver for the Texas Instruments INA3221 3 channels current sensor

CircuitPython Author : Barbudor (Jean-Michel Mercier)
Python mods : Modified for standard Python (removed MicroPython dependencies)

Implementation Notes
--------------------

In order to be coherent with the datasheet, the channel index in the below API start at 1.
Value of ``channel`` parameter must be ``1``, ``2`` or ``3``. **Do not use** ``0``

**Hardware:**

* Device: `INA3221 <http://www.ti.com/product/INA3221>`_ Triple, Low-/High-Side, I2C Out
  Current/Voltage Monitor.

"""
# imports
# Removed micropython dependency

_DEFAULT_ADDRESS                 = 0x40

#
# Registers and bits definitions
#

# Config register
C_REG_CONFIG                      = 0x00

C_RESET                           = 0x8000
C_ENABLE_CH                       = (None, 0x4000, 0x2000, 0x1000) # default set

C_AVERAGING_MASK                  = 0x0E00
C_AVERAGING_NONE                  = 0x0000     # 1 sample, default
C_AVERAGING_4_SAMPLES             = 0x0200
C_AVERAGING_16_SAMPLES            = 0x0400
C_AVERAGING_64_SAMPLES            = 0x0600
C_AVERAGING_128_SAMPLES           = 0x0800
C_AVERAGING_256_SAMPLES           = 0x0A00
C_AVERAGING_512_SAMPLES           = 0x0C00
C_AVERAGING_1024_SAMPLES          = 0x0E00

C_VBUS_CONV_TIME_MASK             = 0x01C0
C_VBUS_CONV_TIME_140US            = 0x0000
C_VBUS_CONV_TIME_204US            = 0x0040
C_VBUS_CONV_TIME_332US            = 0x0080
C_VBUS_CONV_TIME_588US            = 0x00C0
C_VBUS_CONV_TIME_1MS              = 0x0100     # 1.1ms, default
C_VBUS_CONV_TIME_2MS              = 0x0140     # 2.116ms
C_VBUS_CONV_TIME_4MS              = 0x0180     # 4.156ms
C_VBUS_CONV_TIME_8MS              = 0x01C0     # 8.244ms

C_SHUNT_CONV_TIME_MASK            = 0x0038
C_SHUNT_CONV_TIME_140US           = 0x0000
C_SHUNT_CONV_TIME_204US           = 0x0008
C_SHUNT_CONV_TIME_332US           = 0x0010
C_SHUNT_CONV_TIME_588US           = 0x0018
C_SHUNT_CONV_TIME_1MS             = 0x0020     # 1.1ms, default
C_SHUNT_CONV_TIME_2MS             = 0x0028     # 2.116ms
C_SHUNT_CONV_TIME_4MS             = 0x0030     # 4.156ms
C_SHUNT_CONV_TIME_8MS             = 0x0038     # 8.244ms

C_MODE_MASK                       = 0x0007
C_MODE_POWER_DOWN                 = 0x0000     # Power-down
C_MODE_SHUNT_VOLTAGE_TRIGGERED    = 0x0001     # Shunt voltage, single-shot (triggered)
C_MODE_BUS_VOLTAGE_TRIGGERED      = 0x0002     # Bus voltage, single-shot (triggered)
C_MODE_SHUNT_AND_BUS_TRIGGERED    = 0x0003     # Shunt and bus, single-shot (triggered)
C_MODE_POWER_DOWN2                = 0x0004     # Power-down
C_MODE_SHUNT_VOLTAGE_CONTINUOUS   = 0x0005     # Shunt voltage, continous
C_MODE_BUS_VOLTAGE_CONTINUOUS     = 0x0006     # Bus voltage, continuous
C_MODE_SHUNT_AND_BUS_CONTINOUS    = 0x0007     # Shunt and bus, continuous (default)

# Other registers
C_REG_SHUNT_VOLTAGE_CH            = (None, 0x01, 0x03, 0x05)
C_REG_BUS_VOLTAGE_CH              = (None, 0x02, 0x04, 0x06)
C_REG_CRITICAL_ALERT_LIMIT_CH     = (None, 0x07, 0x09, 0x0B)
C_REG_WARNING_ALERT_LIMIT_CH      = (None, 0x08, 0x0A, 0x0C)
C_REG_SHUNT_VOLTAGE_SUM           = 0x0D
C_REG_SHUNT_VOLTAGE_SUM_LIMIT     = 0x0E

# Mask/enable register
C_REG_MASK_ENABLE                 = 0x0F
C_SUM_CONTROL_CH                  = (None, 0x4000, 0x2000, 0x1000) # def. not set
C_WARNING_LATCH_ENABLE            = 0x0800     # default not set
C_CRITICAL_LATCH_ENABLE           = 0x0400     # default not set
C_CRITICAL_FLAG_CH                = (None, 0x0200, 0x0100, 0x0080)
C_SUM_ALERT_FLAG                  = 0x0040
C_WARNING_FLAG_CH                 = (None, 0x0020, 0x0010, 0x0008)
C_POWER_ALERT_FLAG                = 0x0004
C_TIMING_ALERT_FLAG               = 0x0002
C_CONV_READY_FLAG                 = 0x0001

# Other registers
C_REG_POWER_VALID_UPPER_LIMIT     = 0x10
C_REG_POWER_VALID_LOWER_LIMIT     = 0x11
C_REG_MANUFACTURER_ID             = 0xFE
C_REG_DIE_ID                      = 0xFF

# Constants for manufacturer and device ID
C_MANUFACTURER_ID                 = 0x5449     # "TI"
C_DIE_ID                          = 0x3220

# General constants
C_BUS_ADC_LSB                     = 0.008             # VBus ADC LSB is 8mV
C_SHUNT_ADC_LSB                   = 0.00004           # VShunt ADC LSB is 40µV


class INA3221:
    """Driver class for Texas Instruments INA3221 3 channel current sensor device"""

    IS_FULL_API = True

    @staticmethod
    def _to_signed(val):
        if val > 32767:
            return val - 65536
        return val

    @staticmethod
    def _to_unsigned(val):
        if val < 0:
            return val + 65536
        return val

    def write(self, reg, value):
        """Write value in device register"""
        seq = bytearray([reg, (value >> 8) & 0xFF, value & 0xFF])
        self.i2c_device.write(seq)

    def read(self, reg):
        """Return value from device register"""
        buf = bytearray(3)
        buf[0] = reg
        self.write_then_readinto(buf, buf, out_end=1, in_start=1)
        value = (buf[1] << 8) | (buf[2])
        return value

    def update(self, reg, mask, value):
        """Read-modify-write value in register"""
        regvalue = self.read(reg)
        regvalue &= ~mask
        value &= mask
        self.write(reg, regvalue | value)

    def writeto_then_readfrom(
        self,
        address,
        buffer_out,
        buffer_in,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None,
        stop=False
    ):
        """Write data from buffer_out to an address and then
        read data from an address and into buffer_in
        """
        if out_end:
            self.i2c_device.writeto(address, buffer_out[out_start:out_end], stop)
        else:
            self.i2c_device.writeto(address, buffer_out[out_start:], stop)

        if not in_end:
            in_end = len(buffer_in)
        read_buffer = memoryview(buffer_in)[in_start:in_end]
        self.i2c_device.readfrom_into(address, read_buffer, stop)
        

    def write_then_readinto(
        self,
        out_buffer,
        in_buffer,
        *,
        out_start=0,
        out_end=None,
        in_start=0,
        in_end=None
    ):
        """
        Write the bytes from ``out_buffer`` to the device, then immediately
        reads into ``in_buffer`` from the device. The number of bytes read
        will be the length of ``in_buffer``.

        If ``out_start`` or ``out_end`` is provided, then the output buffer
        will be sliced as if ``out_buffer[out_start:out_end]``. This will
        not cause an allocation like ``buffer[out_start:out_end]`` will so
        it saves memory.

        If ``in_start`` or ``in_end`` is provided, then the input buffer
        will be sliced as if ``in_buffer[in_start:in_end]``. This will not
        cause an allocation like ``in_buffer[in_start:in_end]`` will so
        it saves memory.

        :param bytearray out_buffer: buffer containing the bytes to write
        :param bytearray in_buffer: buffer containing the bytes to read into
        :param int out_start: Index to start writing from
        :param int out_end: Index to read up to but not include; if None, use ``len(out_buffer)``
        :param int in_start: Index to start writing at
        :param int in_end: Index to write up to but not include; if None, use ``len(in_buffer)``
        """
        if out_end is None:
            out_end = len(out_buffer)
        if in_end is None:
            in_end = len(in_buffer)

        self.writeto_then_readfrom(
            self.i2c_addr,
            out_buffer,
            in_buffer,
            out_start=out_start,
            out_end=out_end,
            in_start=in_start,
            in_end=in_end,
        )


    def __init__(self, i2c_instance, i2c_addr = _DEFAULT_ADDRESS, shunt_resistor = (0.1, 0.1, 0.1)):
        self.i2c_device = i2c_instance
        self.i2c_addr = i2c_addr
        self.shunt_resistor = shunt_resistor
        self.write(C_REG_CONFIG,  C_AVERAGING_16_SAMPLES | \
                                  C_VBUS_CONV_TIME_1MS | \
                                  C_SHUNT_CONV_TIME_1MS | \
                                  C_MODE_SHUNT_AND_BUS_CONTINOUS )


    def is_channel_enabled(self, channel=1):
        """Returns if a given channel is enabled or not"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        bit = C_ENABLE_CH[channel]
        return self.read(C_REG_CONFIG) & bit != 0

    def enable_channel(self, channel=1, enable=True):
        """Enables or disable a given channel"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        bit = C_ENABLE_CH[channel]
        value = 0
        if enable:
            value = bit
        self.update(C_REG_CONFIG, bit, value)

    def shunt_voltage(self, channel=1):
        """Returns the channel's shunt voltage in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_signed(self.read(C_REG_SHUNT_VOLTAGE_CH[channel])) / 8.0
        # convert to volts - LSB = 40uV
        return value * C_SHUNT_ADC_LSB

    def current(self, channel=1):
        """Return's the channel current in Amps"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        return self.shunt_voltage(channel) / self.shunt_resistor[channel-1]

    def bus_voltage(self, channel=1):
        """Returns the channel's bus voltage in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_signed(self.read(C_REG_BUS_VOLTAGE_CH[channel])) / 8
        # convert to volts - LSB = 8mV
        return value * C_BUS_ADC_LSB

    def shunt_critical_alert_limit(self, channel=1):
        """Returns the channel's shunt voltage critical alert limit in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_signed(self.read(C_REG_CRITICAL_ALERT_LIMIT_CH[channel])) / 8
        # convert to volts - LSB = 40uV
        return value * C_SHUNT_ADC_LSB

    def set_shunt_critical_alert_limit(self, channel, voltage):
        """Sets the channel's shunt voltage critical alert limit in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_unsigned(round(voltage * C_SHUNT_ADC_LSB) * 8)
        self.write(C_REG_CRITICAL_ALERT_LIMIT_CH[channel], value)

    def shunt_warning_alert_limit(self, channel=1):
        """Returns the channel's shunt voltage warning alert limit in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_signed(self.read(C_REG_WARNING_ALERT_LIMIT_CH[channel])) / 8
        # convert to volts - LSB = 40uV
        return value * C_SHUNT_ADC_LSB

    def set_shunt_warning_alert_limit(self, channel, voltage):
        """Sets the channel's shunt voltage warning alert limit in Volts"""
        assert 1 <= channel <= 3, "channel argument must be 1, 2, or 3"
        value = self._to_unsigned(round(voltage * C_SHUNT_ADC_LSB) * 8)
        self.write(C_REG_WARNING_ALERT_LIMIT_CH[channel], value)

    @property
    def is_ready(self):
        """Returns the CVRF (ConVersion Ready Flag) from the mask/enable register """
        regvalue = self.read(C_REG_MASK_ENABLE)
        return (regvalue & C_CONV_READY_FLAG) != 0
    
