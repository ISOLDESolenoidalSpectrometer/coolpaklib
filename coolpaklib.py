# -*- coding: utf-8 -*-
"""
A library for communicating with Leybold COOLPAK 6000 compressor units
using the serial RS232 interface

Protocol data format is 4800 baud 8N1 (8 bit, no parity check, 1 stop bit)
"""
__author__ = "Joonas Konki"
__license__ = "MIT, see LICENSE for more details"
__copyright__ = "2018 Joonas Konki"

import logging
import serial
import time

# Set the minimum safe time interval between sent commands that is required according to the user manual
START_CHR = '\x02'
END_CHR   = '\x0D'

# Interpretation of the status character string response from the unit
INTERP = {
        0 : 'Software version',
        1 : 'Leybold internal use only',
        2 : 'COOLPAK hours counter',
        3 : 'Leybold internal use only',
        4 : 'Leybold internal use only',
        5 : 'Leybold internal use only',
        6 : 'Switch-ON delay timer [seconds]',
        7 : 'Command status (0==OFF, 1==ON, 2==SYSTEM ERROR)',
        8 : 'Actual compressor status (0==OFF, 1==ON)',
        9 : 'Not used',
        10 : 'Not used',
        11 : 'Number of still active errors',
        12 : 'Error bit map (1==error active, 0==error not active)',
        13 : 'Number of recorded and logged errors'
}

class COOLPAK():
	def __init__(self,port,baud=4800):
		self.port = port
		self.ser = serial.Serial( port=self.port,
					  bytesize=serial.EIGHTBITS,
					  parity=serial.PARITY_NONE,
					  stopbits=serial.STOPBITS_ONE,
					  baudrate=baud,
					  xonxoff=False,
					  rtscts=False,
					  timeout=1 )

		logging.basicConfig(format='coolpaklib: %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.WARNING)
		#logging.basicConfig(format='coolpaklib: %(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', level=logging.DEBUG)
		logging.debug('Serial port ' + self.port + ' opened at speed ' + str(baud))

		time.sleep(0.1) # Wait 100 ms after opening the port before sending commands
		self.ser.flushOutput() # Flush the output buffer of the serial port before sending any new commands
		self.ser.flushInput() # Flush the input buffer of the serial port before sending any new commands

	def close(self):
		"""The function closes and releases the serial port connection attached to the unit.

		"""
		if self.ser != None :
			self.ser.close()

	def send_command(self, command=''):
		"""The function sends a command to the unit and returns the response string.

		"""
		if command == '': return ''
		full_cmd = START_CHR + command + END_CHR
		self.ser.write( full_cmd.encode('ascii') )
		time.sleep(0.1)
		logging.debug('Command sent to the unit: ' + command)
		response = self.ser.readline().decode('ascii')
		clean_response = response.replace(START_CHR+'DAT', '').replace(END_CHR,'') #strip out START_CHR and END_CHR
		logging.debug('Response from unit: ' + response)
		return clean_response # return response from the unit as string

	def flush_input_buffer(self):
		""" Flush the input buffer of the serial port.
		"""
		self.ser.flushInput()

	def flush_output_buffer(self):
		""" Flush the output buffer of the serial port.
		"""
		self.ser.flushOutput()


	def set_power_on(self):
		""" The function turns the power ON.

		"""
		response = self.send_command( 'SYS%d' % 1 )

	def set_power_off(self):
		""" The function turns the power OFF.

		"""
		response = self.send_command( 'SYS%d' % 0 )

	def get_actual_power(self):
		""" The function gets the actual power state of the unit.
			0 == OFF
			1 == ON
		"""
		response = self.send_command( 'DAT' )
		split_res = response.split('/')
		if len(split_res) != 14 :
			result = 'Unknown'
		else:
			result = split_res[8]
		return result

	def get_command_power(self):
		""" The function gets the commanded power state of the unit.
			0 == OFF
			1 == ON
			2 == SYSTEM ERROR
		"""
		response = self.send_command( 'DAT' )
		split_res = response.split('/')
		if len(split_res) != 14 :
			result = 'Unknown'
		else:
			result = split_res[7]
		return result

	def get_status(self):
		""" The function gets the full status message from the unit.

		"""
		response = self.send_command( 'DAT')
		return response

	def print_status(self):
		""" The function prints the interpreted full status message from the unit to the console.

		"""
		response = self.send_command( 'DAT')
		split_res = response.split('/')
		if 14 != len(split_res):
			logging.warning('Warning: length of the response is strange. Try interpreting anyway...')

		for i in range(len(split_res)):
			print( INTERP[i] + ' : ' + split_res[i] )
