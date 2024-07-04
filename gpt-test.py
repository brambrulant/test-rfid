import serial
import os
import sys
import time
import string
import datetime
import csv

# WARNING!!!! The RFID Module MUST be connected through the non-power USB port
serial_port = '/dev/ttyUSB0'  # Adjust if not correct, use $ python -m serial.tools.miniterm to find correct port
ser = serial.Serial(port=serial_port, baudrate=38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

Stall_Time = 10  # Time to consider that the tag has completely left the reader area
Last_Tag = "initialise value"  # Just need a value that isn't an RFID tag
Last_Time = time.time() - Stall_Time  # Set the time value to effectively 0 (for use in loop later)

date = datetime.today()

# Set up the reader
def set_up_the_reader():
    print("Setting up the reader...")
    power_level = 25  # Reader power level from -2 ~ 25dB
    ser.write(f'\nN1,{power_level}\r'.encode())
    time.sleep(0.1)

    # Set up the region - this is the frequency of operation - uncomment correct line
    # ser.write(b'\nN5,01\r')  # Region 01: US  902~928MHz
    # ser.write(b'\nN5,02\r')  # Region 02: TW  922~928MHz
    # ser.write(b'\nN5,03\r')  # Region 03: CN  920~925MHz
    # ser.write(b'\nN5,04\r')  # Region 04: CN2 840~845MHz
    ser.write(b'\nN5,05\r')  # Region 05: EU  865~868MHz
    # ser.write(b'\nN5,06\r')  # Region 06: JP  916~921MHz
    time.sleep(0.1)
    ser.write(b'\nB 0\r')
    print("Reader setup complete.")

# Write to CSV
def write_to_csv(RFID_Tag, RFID_Time):
    data = [RFID_Tag.decode('utf-8', 'ignore'), RFID_Time.strftime("%m/%d/%Y, %H:%M:%S"), date.strftime("%m/%d/%Y, %H:%M:%S")]
    with open('test.csv', 'a+', newline='') as read_file:
        reader = csv.reader(read_file)
        writer = csv.writer(read_file)
        for row in reader:
            if data[0] in row:
                row = [row[0], row[1], RFID_Time.strftime("%m/%d/%Y, %H:%M:%S")]
                writer.writerow()
                return
            else:
                writer.writerow(data)


# Send command
def send_command():
    reader_command = '\nU\r'  # Command to see only EPC
    # reader_command = '\nR2,0,6\r'  # Command to see TID, uncomment if needed
    ser.write(reader_command.encode())
    time.sleep(0.1)

# Read buffer
def read_buffer():
    RFID_Tag = ser.read(ser.inWaiting())  # Read the buffer (ser.read) for specific byte length (inWaiting)
    RFID_Time = datetime.datetime.now()  # Record the time the tag was read
    print('RFID_Tag:', RFID_Tag)
    return RFID_Tag, RFID_Time

# Main function
set_up_the_reader()

while True:
    send_command()
    RFID = read_buffer()
    RFID_Tag = RFID[0]
    RFID_Time = RFID[1]
    
    if len(RFID_Tag) > 15:  # This should be about 15 normally
        write_to_csv(RFID_Tag, RFID_Time)