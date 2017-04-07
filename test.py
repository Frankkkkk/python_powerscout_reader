#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Frank@Villaro-Dixon.eu - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import minimalmodbus
import serial


# serial line
instrument = minimalmodbus.Instrument('/dev/ttyUSB0',1)
instrument.serial.baudrate= 9600
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1 # seconds

# modbus reading 0 - start, 56 - count, 4 - input register function
# offset 5 is wind speed - we will provide you an XML file with definition of all registers so you can use it in your program
# offset 6 is wind direction
data = instrument.read_register(4058, 1)
print(data)



# vim: set ts=4 sw=4 noet:

