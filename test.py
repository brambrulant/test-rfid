import serial

rfid_serial_port = serial.Serial("/dev/ttyUSB1", 9600)

id_num = []
i = 0
while True:
    serial_data = rfid_serial_port.read()
    data = serial_data.decode('utf-8')
    i = i + 1
    if i == 12:
        i = 0
        ID = "".join(map(str, id_num))
        print(ID)
        id_num = []
    else:
        id_num.append(data)
    i = i + 1
    if i == 12:
        i = 0
        ID = "".join(map(str, id_num))
        print(ID)
    else:
        id_num.append(data)