#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Frank@Villaro-Dixon.eu - DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE, etc.

import minimalmodbus
import serial
import time
import sys, os

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
	return instrument.read_register(4200, 1)

def PS_read_measurment(instrument):
	wanted_values = {
		'V1': 4058,
		'V2': 4059,
		'V3': 4060,

		'A1': 4055,
		'A2': 4056,
		'A3': 4057,

		'P1': 4028,
		'P2': 4029,
		'P3': 4030,

		'phi1': 4052,
		'phi2': 4053,
		'phi3': 4054,

		'CI1': 10099,
		'CI2': 10199,
		'CI3': 10299,
	}

	multipliers = {
		'phi1': lambda x: x*10,
		'phi2': lambda x: x*10,
		'phi3': lambda x: x*10,

		'CI1': lambda x: x*10,
		'CI2': lambda x: x*10,
		'CI3': lambda x: x*10,
	}



	scalar_divider = {
		'V': lambda scalar: .1 if scalar <=3 else 1,
		'A': lambda scalar: .1 if scalar == 0 else .1 if scalar <= 3 else 1,
	}

	scalars = {
		'V1': 'V',
		'V2': 'V',
		'V3': 'V',

		'A1': 'A',
		'A2': 'A',
		'A3': 'A',
	}


	scalar_value = instrument.read_register(4601)

	read_results = {}
	for wanted_value in wanted_values:
		addr = wanted_values[wanted_value]

		reading = instrument.read_register(addr, 1)
		if wanted_value in multipliers:
			reading = multipliers[wanted_value](reading)

#		if wanted_value in scalars:
#			print('SCALAR VAL: {}, div: {}'.format(scalar_value, scalar_divider[scalars[wanted_value]](scalar_value)))
#			print('READING: {} {}'.format(wanted_value, reading))
#			reading = reading * scalar_divider[scalars[wanted_value]](scalar_value)
#			print('RESULT: {}'.format(reading))

		read_results[wanted_value] = reading
	return read_results


def get_alive_power_scouts():
	modbus_alives = []
	print('Scanning power scouts…')
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
	f.write('\n')

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
	f.write('\n')


def display_results(results):
	def _display_units():
		print('|id | |V1 |A1  |P1  |φ1 | |V2 |A2  |P2  |φ2 | |V3 |A3  |P3  |φ3 | | |CT1|CT2|CT3|')
	def _display_separator():
		print('|---| |---|----|----|---| |---|----|----|---| |---|----|----|---| | |---|---|---|')

	os.system('clear')

	_display_separator()
	_display_units()
	_display_separator()
	_display_separator()

	for ps in results.keys():
		r = results[ps]
		print('|{:3d}| ' \
		'|{:3.3}|{:4.4}|{:4.4}|{:3.3}| ' \
		'|{:3.3}|{:4.4}|{:4.4}|{:3.3}| ' \
		'|{:3.3}|{:4.4}|{:4.4}|{:3.3}| | '
		'|{:3.3}|{:3.3}|{:3.3}|'.format(ps, \
				str(r['V1']), str(r['A1']), str(r['P1']), str(r['phi1']), \
				str(r['V2']), str(r['A2']), str(r['P2']), str(r['phi2']), \
				str(r['V3']), str(r['A3']), str(r['P3']), str(r['phi3']), \
				str(r['CI1']), str(r['CI2']), str(r['CI3']), \
		))
		_display_separator()


modbus_alive = get_alive_power_scouts()

ps_files = {}
for ps in modbus_alive:
	ps_files[ps] = open('LOGS/PS_log_{}.csv'.format(ps), 'a')

ps_instruments = {}
for ps in modbus_alive:
	ps_instruments[ps] = _get_instrument(ps)

#Write labels
for ps in ps_instruments:
	results = PS_read_measurment(ps_instruments[ps])
	print_header(results, ps_files[ps])

while True:
	results = {}
	try:
		for ps in ps_instruments:
			ps_results = PS_read_measurment(ps_instruments[ps])
			save_results(results, ps_files[ps])
			results[ps] = ps_results
	except:
		pass
	display_results(results)

	time.sleep(interval)

# vim: set ts=4 sw=4 noet:

