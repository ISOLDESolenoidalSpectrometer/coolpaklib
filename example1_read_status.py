#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Example script to read and print the status of the COOLPAK 6000 unit
# 20190308 - Joonas Konki

import coolpaklib
from serial.tools import list_ports

# Identify the correct serial port to use
myport = ''
MANUFACTURER = 'Prolific'
ports = list_ports.comports()
for port in ports:
	if MANUFACTURER in port.manufacturer:
		myport = port.device
		print("Found unit in port: " + str(port.device) )
		break

# Unit not found
if myport == '':
	print("Unit is not connected or found, exiting...")
	exit()

myunit = coolpaklib.COOLPAK(myport)

val = myunit.get_status()
print("COOLPAK status is: " + val)

myunit.print_status()

myunit.close()
