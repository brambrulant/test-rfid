#!/usr/bin/env python
import serial

ser = serial.Serial('/dev/ttyUSB1')
print(ser.name)
x = ser.read(12)
print(x)
