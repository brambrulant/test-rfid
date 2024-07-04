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
    print("Reader setup complete.")

# Write to CSV
def write_to_csv(RFID_Tag, RFID_Time):
    data = [RFID_Tag.decode('utf-8', 'ignore'), RFID_Time.strftime('%Y-%m-%d'), RFID_Time.strftime('%H:%M:%S.%f')]
    with open('test.csv', 'a+', newline='') as read_file:
        writer = csv.writer(read_file)
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
        if RFID_Tag != Last_Tag:  # Compare last read to this read to see if it is the same
            print(RFID_Tag)  # Only display the tag id part of the value
            print(RFID_Time)  # Display the time the tag was read at (yes, it's delayed but close enough)
            write_to_csv(RFID_Tag, RFID_Time)
            Last_Tag = RFID_Tag  # Gives something to compare for next run through loop
            Last_Time = time.time()  # Gives seconds since /whatever/ so can check if 60 seconds have passed for the next part of the loop
        elif time.time() - Last_Time > Stall_Time:  # This part of the loop checks if a /time/ has passed before recording the RFID again, this could be several minutes really
            print(RFID_Tag)  # Do the same stuff as the first loop
            print(RFID_Time)
            write_to_csv(RFID_Tag, RFID_Time)
            Last_Tag = RFID_Tag
            Last_Time = time.time()