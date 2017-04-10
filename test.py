#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Frank@Villaro-Dixon.eu - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import minimalmodbus
import serial
import time
import sys


if len(sys.argv) != 2:
	print('Usage: {} POWER_SCOUT_ID'.format(sys.argv[0]))
	sys.exit(1)


instrument = minimalmodbus.Instrument('/dev/ttyUSB0', int(sys.argv[1]))
instrument.serial.baudrate= 76800
instrument.serial.bytesize = 8
instrument.serial.parity = serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1 # seconds


wanted_values = {
	'L1_V': 4058,
	'L2_V': 4059,
	'L3_V': 4060,

	'L1_A': 4055,
	'L2_A': 4056,
	'L3_A': 4057,

	'L1_P': 4028,
	'L2_P': 4029,
	'L3_P': 4030,

	'L1_phi': 4052,
	'L2_phi': 4053,
	'L3_phi': 4054,

}

sorted_labels = []
for label in sorted(wanted_values):
	sorted_labels.append(label)
#print(','.join(sorted_labels))


read_results = {}
for wanted_value in wanted_values:
	addr = wanted_values[wanted_value]

	reading = instrument.read_register(addr, 1)
	read_results[wanted_value] = reading

csv_results = []
for label in sorted_labels:
	csv_results.append(read_results[label])
str_csv_results = [str(a) for a in csv_results]

str_csv_results.append(time.strftime("%Y/%m/%d %H:%M:%S"))
str_csv_results.append(time.strftime("%s")) #timestamp


csv_result = ','.join(str_csv_results)
print(csv_result)



# vim: set ts=4 sw=4 noet:

