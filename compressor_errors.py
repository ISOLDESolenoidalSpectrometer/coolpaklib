#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Test script to read the logged errors of the Coolpak 6000 compressor
# using the RS-232/485 interface.
#
# Protocol format is: 4800 baud 8N1, no handshake needed
#
# 20190123 - Joonas Konki

import serial
from serial.tools import list_ports

#COMPRESSOR_SERIAL_NO = 'FTXOBKUT'
START_CHR = '\x02'
LINETERM = '\x0D'
SPEED=4800

#command = 'DAT'
#command = 'SYS1' #switch ON
#command = 'SYS0' #switch OFF
command = 'ERR'  #request error codes


# Find out which serial port the USB-to-Serial converter 
# of the compressor is connected to.
#myport = '/dev/ttyUSB2'
myport = ''
ports = list_ports.comports()
for port in ports:
	if 'Prolific' in port.manufacturer:
		print('Found USB-to-Serial converter in port ' + port.device)
		myport = port.device
		break

if '' == myport:
	print('USB-to-Serial converter not found\n')
	exit() # controller not found

#mg = serial.Serial(port=myport, baudrate=SPEED, timeout=5)
mg = serial.Serial( port=myport,
		  bytesize=serial.EIGHTBITS,
		  parity=serial.PARITY_NONE,
		  stopbits=serial.STOPBITS_ONE,
		  baudrate=SPEED,
		  xonxoff=False,
		  rtscts=False,
		  timeout=2 )

mg.flushInput()
mg.flushOutput()

com = ( START_CHR + command + LINETERM).encode('ascii') 
#print(com)
mg.write( com  )
#mg.write( bytes(START_CHR + command + LINETERM, 'ascii') ) 
#mg.write( b'(START_CHR + command + LINETERM)' ) 

res = mg.readline()

interpretation = {
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

if len(res) > 0:
	#print(res)
	res_dec = res.decode('ascii')
	clean_res = res_dec.replace(START_CHR+'DAT', '').replace('\r','')
	#print(clean_res)
	split_res = clean_res.split('/')
	msg = 'Number of errors = ' + str(len(split_res))
	print(msg)
	for i in range(len(split_res)):
		print('error ' + str(i) + ' : ' + split_res[i])

mg.close()


