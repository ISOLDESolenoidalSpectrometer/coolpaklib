#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Test script to read the status of the Coolpak 6000 compressor
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
command = 'SYS0' #switch OFF
#command = 'ERR'  #request error codes


# Find out which serial port the USB-to-Serial converter 
# of the compressor is connected to.
myport = ''
ports = list_ports.comports()
for port in ports:
	if 'Prolific' in port.manufacturer:
		print('Found USB-to-Serial converter in port ' + port.device)
		myport = port.device
		break

if '' == myport:
	print('USB-to-Serial converter not found')
	exit() # controller not found

#mg = serial.Serial(port=myport, baudrate=SPEED, timeout=5)
mg = serial.Serial( port=myport,
		  bytesize=serial.EIGHTBITS,
		  parity=serial.PARITY_NONE,
		  stopbits=serial.STOPBITS_ONE,
		  baudrate=SPEED,
		  xonxoff=False,
		  rtscts=False,
		  timeout=5 )

mg.flushInput()
mg.flushOutput()

com = ( START_CHR + command + LINETERM).encode('ascii') 
print(com)
print(len(com))
mg.write( com  )
#mg.write( bytes(START_CHR + command + LINETERM, 'ascii') ) 
#mg.write( b'(START_CHR + command + LINETERM)' ) 

res = mg.readline()
print(res)
res_dec = res.decode('ascii')
print(res_dec)

mg.close()

