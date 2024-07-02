#!/usr/bin/env python
import serial

listPorts = serial.tools.list_ports
print(listPorts.comports())
ser = serial.Serial('/dev/ttyUSB1')
print(ser.name)
x = ser.read(12)
print(x)
