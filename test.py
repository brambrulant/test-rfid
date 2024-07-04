import serial
import time
import datetime
import sqlite3
import re

# Serial port setup
serial_port = '/dev/ttyUSB0'
ser = serial.Serial(port=serial_port, baudrate=38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

Stall_Time = 10
Last_Tag = "initialise value"
Last_Time = time.time() - Stall_Time

# SQLite database setup
db_name = 'rfid_tags.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        tag TEXT PRIMARY KEY,
        time_of_first_scan TEXT,
        time_of_last_scan TEXT
    )
''')
conn.commit()

def set_up_the_reader():
    ser.write(b'\nN0,00\r')
    ser.write(b'\nN1,1B\r')
    ser.write(b'\nN0,00\r')
    ser.write(b'\nN5,06\r')

def insert_or_update_tag(tag, first_scan, last_scan):
    cursor.execute('SELECT * FROM tags WHERE tag = ?', (tag,))
    data = cursor.fetchone()
    if data is None:
        cursor.execute('INSERT INTO tags (tag, time_of_first_scan, time_of_last_scan) VALUES (?, ?, ?)',
                       (tag, first_scan, last_scan))
    else:
        cursor.execute('UPDATE tags SET time_of_last_scan = ? WHERE tag = ?', (last_scan, tag))
    conn.commit()

def send_command():
    reader_command = '\nU\r'
    ser.write(reader_command.encode())
    time.sleep(0.1)

def read_buffer():
    RFID_Tag = ser.read(ser.inWaiting())
    RFID_Time = datetime.datetime.now()
    print('RFID_Tag:', RFID_Tag)
    return RFID_Tag, RFID_Time

set_up_the_reader()

while True:
    print(ser.read())
    send_command()
    RFID = read_buffer()
    RFID_Tag = RFID[0]
    RFID_Time = RFID[1]
    
    if len(RFID_Tag) > 15:
        tag_str = RFID_Tag.decode('utf-8', 'ignore')
        tags = re.findall(r'U3000E[0-9A-F]+', tag_str)
        first_scan = RFID_Time.strftime('%Y-%m-%d %H:%M:%S.%f')
        last_scan = RFID_Time.strftime('%Y-%m-%d %H:%M:%S.%f')

        for tag in tags:
            insert_or_update_tag(tag, first_scan, last_scan)

        print(tags)
        print(RFID_Time)
