import serial
import time
import datetime
import sqlite3

# WARNING!!!! The RFID Module MUST be connected through the non-power USB port
serial_port = '/dev/ttyUSB0'  # Adjust if not correct, use $ python -m serial.tools.miniterm to find correct port
ser = serial.Serial(port=serial_port, baudrate=38400, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

Stall_Time = 10  # Time to consider that the tag has completely left the reader area
Last_Tag = "initialise value"  # Just need a value that isn't an RFID tag
Last_Time = time.time() - Stall_Time  # Set the time value to effectively 0 (for use in loop later)

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

# Set up the reader
def set_up_the_reader():
    print("Setting up the reader...")
    ser.write(b'\nN0,00\r')  # Read power
    time.sleep(0.1)
    ser.write(b'\nN1,1B\r')  # Write power
    time.sleep(0.1)
    ser.write(b'\nN0,00\r')  # Read again
    time.sleep(0.1)

    # Set up the region - this is the frequency of operation - uncomment correct line
    # ser.write(b'\nN5,01\r')  # Region 01: US  902~928MHz
    # ser.write(b'\nN5,02\r')  # Region 02: TW  922~928MHz
    # ser.write(b'\nN5,03\r')  # Region 03: CN  920~925MHz
    # ser.write(b'\nN5,04\r')  # Region 04: CN2 840~845MHz
    ser.write(b'\nN5,05\r')  # Region 05: EU  865~868MHz
    # ser.write(b'\nN5,06\r')  # Region 06: JP  916~921MHz
    time.sleep(0.1)

    # Turn off the buzzer - assuming 'B 0' is the correct command to disable the buzzer
    ser.write(b'B0\r')
    time.sleep(0.1)
    print("Reader setup complete.")

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

# Send command
def send_command():
    # reader_command = '\nU\r'  # Uncomment if you want to only see EPC
    reader_command = '\nR2,0,6\r'  # Uncomment to see TID copy/paste to www.gs1.org/services/tid-decoder '806' is NXP
    print('Sending command:', reader_command)
    ser.write(reader_command.encode())
    time.sleep(0.1)

# Read buffer
def read_buffer():
    data_waiting = ser.inWaiting()
    print(f"Bytes waiting in buffer: {data_waiting}")
    RFID_Tag = ser.read(data_waiting)  # Read the buffer (ser.read) for specific byte length (inWaiting)
    RFID_Time = datetime.datetime.now()  # Record the time the tag was read
    print('RFID_Tag:', RFID_Tag)
    return RFID_Tag, RFID_Time

# Main function
set_up_the_reader()
time.sleep(1)  # Allow some time for the reader to set up properly

try:
    while True:
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

except KeyboardInterrupt:
    # Close the database connection when the script is interrupted
    conn.close()
    ser.close()
    print("Data written to database. Exiting.")