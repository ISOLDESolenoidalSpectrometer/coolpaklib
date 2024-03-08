#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Watchdog script to check the status of the Coolpak 6000 compressor
# Run as a cronjob. Sends emails when the power is off or has just been restored.
# 
# 20190719 - Joonas Konki

import serial
from serial.tools import list_ports
import subprocess
import requests

HTTP_TIMEOUT = 10
MAX_TEMP = 34.5
MIN_TEMP = 16.0

#COMPRESSOR_SERIAL_NO = 'FTXOBKUT'
START_CHR = '\x02'
LINETERM = '\x0D'
SPEED=4800

command = 'DAT'
#command = 'SYS1' #switch ON
#command = 'SYS0' #switch OFF
#command = 'ERR'  #request error codes


# Find out which serial port the USB-to-Serial converter 
# of the compressor is connected to.
#myport = '/dev/ttyUSB2'
myport = ''
ports = list_ports.comports()
for port in ports:
	if 'Prolific' in port.manufacturer:
		myport = port.device
		break

if '' == myport:
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
actual_status = '0'

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
	res_dec = res.decode('ascii')
	clean_res = res_dec.replace(START_CHR+'DAT', '').replace('\r','')
	split_res = clean_res.split('/')
	if 14 != len(split_res):
		print('Warning: length of the response is strange. Try interpreting anyway...')
	else:
		actual_status = split_res[8]
		# Post to InfluxDB
		payload = 'powerstatus,device=compressor value=' + str(actual_status)
		try:
			r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False, timeout=HTTP_TIMEOUT )
		except Exception:
			pass

	#for i in range(len(split_res)):
	#	print(interpretation[i] + ' : ' + split_res[i])

else :
	print('No response received.')
	actual_status = 0
	# Post to InfluxDB
	payload = 'powerstatus,device=compressor value=' + str(actual_status)
	try:
		r = requests.post( 'https://dbod-iss.cern.ch:8080/write?db=he', data=payload, auth=("admin","issmonitor"), verify=False, timeout=HTTP_TIMEOUT )
	except Exception:
		pass


# Check from file if the compressor was already OFF previously to avoid sending multiple email alerts
last_status = '1'
filename = '/home/pi/scripts/last_status_compressor.txt'
try:
	with open(filename,'r') as f:
		last_status = f.read(1)
		f.close()
except FileNotFoundError:
	pass

f = open(filename,'w+')
f.write(actual_status)
f.close()

if last_status != actual_status: # Status has changed! Send email alert!
	status_str = 'OFF'
	if '1' == actual_status:
		status_str = 'ON'

	script_output = subprocess.call(['/home/pi/scripts/send_alert_email.sh','Coolpak helium compressor',status_str])


## Check the temperature of the coolant from the Julabo chiller
#tempfile = '/home/pi/scripts/current_chiller_temp.txt'
#cur_temp = 40.0
#try:
#	with open(tempfile,'r') as f:
#		cur_temp = float( f.readline() )
#		f.close()
#except FileNotFoundError:
#	print('Cannot open ' + str(tempfile) )
#	pass
#
## Turn off compressor if temperature too high
#if actual_status == '1' and cur_temp > MAX_TEMP:
#	print('Turning compressor off, temperature too high at ' + ('%.2f' % cur_temp) )
#	com = ( START_CHR + 'SYS0' + LINETERM).encode('ascii')
#	mg.write( com )
#	res = mg.readline()
#
## Turn on compressor if temperature is low enough
#if actual_status == '0' and cur_temp < MIN_TEMP:
#	print('Turning compressor back on, temperature now low enough at ' + ('%.2f' % cur_temp) )
#	com = ( START_CHR + 'SYS1' + LINETERM).encode('ascii')
#	mg.write( com )
#	res = mg.readline()

mg.close()

