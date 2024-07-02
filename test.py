import serial

ser = serial.Serial("/dev/ttyUSB0", 38400)

while(ser.is_open == True):
    rfidtag = ''
    incomingByte = ser.read(21)
    print(incomingByte)
    for i in incomingByte:
        rfidtag = rfidtag + hex(i)