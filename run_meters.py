#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Frank@Villaro-Dixon.eu - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import minimalmodbus
import serial
import time
import sys

if len(sys.argv) != 2:
	print('Usage: {} interval[s]'.format(sys.argv[0]))
	sys.exit(1)

interval = int(sys.argv[1])

def _get_instrument(modbus_id):
	instrument = minimalmodbus.Instrument('/dev/ttyUSB0', modbus_id)
	instrument.serial.baudrate= 76800
	instrument.serial.bytesize = 8
	instrument.serial.parity = serial.PARITY_NONE
	instrument.serial.stopbits = 1
	instrument.serial.timeout = .1 # seconds
	return instrument

def PS_get_hardwareid(instrument):
	return instrument.read_register(4209, 1)

def PS_read_measurment(instrument):
	wanted_values = {
		'L1_V': 4058,
		'L2_V': 4059,
		'L3_V': 4060,

		'L1_A': 4055,
		'L2_A': 4056,
		'L3_A': 4057,

		'L1_P': 4028,
		'L2_P': 4028,
		'L3_P': 4028,

		'L1_phi': 4052,
		'L2_phi': 4053,
		'L3_phi': 4054,
	}

	read_results = {}
	for wanted_value in wanted_values:
		addr = wanted_values[wanted_value]

		reading = instrument.read_register(addr, 1)
		read_results[wanted_value] = reading
	return read_results


def get_alive_power_scouts():
	modbus_alives = []
	for mid in range(0xff+1):
		i = _get_instrument(mid)
		try:
			hid = PS_get_hardwareid(i)
			modbus_alives.append(mid)
			print('PS on modbus {} is alive !'.format(mid))
		except Exception:
			pass
	return modbus_alives

def print_header(results, f):
	sorted_labels = []
	for label in sorted(results):
		sorted_labels.append(label)

	csv_result = ','.join(sorted_labels)
	print(csv_result)
	f.write(csv_result)

def save_results(results, f):
	sorted_labels = []
	for label in sorted(results):
		sorted_labels.append(label)

	csv_results = []
	for label in sorted_labels:
		csv_results.append(results[label])
	str_csv_results = [str(a) for a in csv_results]

	str_csv_results.append(time.strftime("%Y/%m/%d %H:%M:%S"))
	str_csv_results.append(time.strftime("%s")) #timestamp

	csv_result = ','.join(str_csv_results)

	print(csv_result)
	f.write(csv_result)



modbus_alive = get_alive_power_scouts()
ps_files = {}
for ps in modbus_alive:
	ps_files[ps] = open('PS_log_{}.csv'.format(ps), 'a')

ps_instruments = {}
for ps in modbus_alive:
	ps_instruments[ps] = _get_instrument(ps)

#Write labels
for ps in ps_instruments:
	results = PS_read_measurment(ps_instruments[ps])
	print_header(results, ps_files[ps])

while True:
	for ps in ps_instruments:
		results = PS_read_measurment(ps_instruments[ps])
		save_results(results, ps_files[ps])
		print(results)

	time.sleep(interval)

# vim: set ts=4 sw=4 noet:

