import serial
import os
import sys
import time
import string
import datetime
import csv
import sqlite3
####WARNING!!!! The RFID Module MUST be connected through the non power USB port####
serial_port = '/dev/ttyUSB0' #this should be correct, but if not working use $ python -m serial.tools.miniterm
ser = serial.Serial(port=serial_port,baudrate = 38400,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

Stall_Time = 10               #Time to consider that the tag has completely left the reader area
Last_Tag = "initialise value" #just need a value that isn't an RFID tag
Last_Time = time.time() - Stall_Time  #set the time value to effectively 0 (for use in loop later)

# SQLite database setup
db_name = 'rfid_tags.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

def reset_serial():
    # flush existing serial data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
	print(ser)

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        tag TEXT PRIMARY KEY,
        time_of_first_scan TEXT,
        time_of_last_scan TEXT
    )
''')
conn.commit()

#start set_up_the_reader()
def set_up_the_reader():
	#set the power level and report back the value
	print()
	ser.write(b'\nN0,00\r') # read power
	ser.write(b'\nN1,1B\r') # write power
	ser.write(b'\nN0,00\r') # read again

	#set up the region - this is the frequency of operation - uncomment correct line
	#ser.write(b'\nN5,03\r')                 #Region 01: US  902~928MHz
	#ser.write(b'\nN5,03\r')                 #Region 02: TW  922~928MHz
	#ser.write(b'\nN5,03\r')                  #Region 03: CN  920~925MHz
	#ser.write(b'\nN5,03\r')                 #Region 04: CN2 840~845MHz
	ser.write(b'\nN5,05\r')                 #Region 05: EU  865~868MHz
	#ser.write(b'\nN5,03\r')                 #Region 06: JP  916~921MH
#end set_up_the_reader()

# Insert or update tag in the database
def insert_or_update_tag(tag, first_scan, last_scan):
    cursor.execute('SELECT * FROM tags WHERE tag = ?', (tag,))
    data = cursor.fetchone()
    if data is None:
        cursor.execute('INSERT INTO tags (tag, time_of_first_scan, time_of_last_scan) VALUES (?, ?, ?)',
                       (tag, first_scan, last_scan))
    else:
        cursor.execute('UPDATE tags SET time_of_last_scan = ? WHERE tag = ?', (last_scan, tag))
    conn.commit()

#start send_command()
def send_command():
	reader_command = '\nU\r'                 #uncomment if you want to only see EPC
	# reader_command = '\nR2,0,6\r'		 #uncomment to see TID copy/paste to www.gs1.org/services/tid-decoder '806' is NXP
	print('reader_command:', reader_command)
	ser.write(reader_command.encode())
	time.sleep(0.1)
#end send_command()

#start read_buffer()
def read_buffer():
	RFID_Tag = ser.read(ser.inWaiting())   #read the buffer (ser.read) for specific byte length (inWaiting)
	RFID_Time = datetime.datetime.now()    #record the time the tag was read
	print('RFID_Tag:', RFID_Tag)

	return RFID_Tag, RFID_Time
#end read_buffer()

#main()
set_up_the_reader()

while True:
	print(ser.read())
	send_command()
	RFID = read_buffer()
	RFID_Tag = RFID[0]
	RFID_Time = RFID[1]
	  
	if len(RFID_Tag) > 15:  # This should be about 15 normally
		tag_str = RFID_Tag.decode('utf-8', 'ignore')
		first_scan = RFID_Time.strftime('%Y-%m-%d %H:%M:%S.%f')
		last_scan = RFID_Time.strftime('%Y-%m-%d %H:%M:%S.%f')

		insert_or_update_tag(tag_str, first_scan, last_scan)

		print(RFID_Tag)  # Only display the tag id part of the value
		print(RFID_Time)