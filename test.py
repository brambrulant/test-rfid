#!/usr/bin/env python
import serial
import RPi.GPIO as GPIO
import os
import sys
import time
import string
from subprocess import Popen
ser = serial.Serial(
       # port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0

        port='/dev/ttyUSB0',
#	port='/dev/ttyS0',
        baudrate = 38400,
        
        
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

while 1:
	y=ser.read(ser.inWaiting())
	time.sleep(0.01)
	x = y.replace("U", "")
	print(x)