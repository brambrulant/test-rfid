#!/usr/bin/python3
import serial
import re
import time
import datetime

BITRATE = 38400

if __name__ == '__main__':
    buffer = ''
    ser = serial.Serial('/dev/ttyUSB0', BITRATE, timeout=0)  # Update the serial port path
    rfidPattern = re.compile(r'[\W_]+')

    log_file = open("rfid_log.txt", "a")  # Open a log file in append mode

    try:
        while True:
            # Read data from RFID reader
            read_bytes = ser.read(ser.inWaiting())
            read = buffer + read_bytes.decode('utf-8', errors='ignore')
            buffer = read.replace("U", "")
            
            if '\n' in buffer:
                lines = buffer.split('\n')
                last_received = lines[-2]
                match = rfidPattern.sub('', last_received)
                
                if match:
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp} - RFID Tag: {match}\n"
                    print(log_entry.strip())
                    log_file.write(log_entry)
                    log_file.flush()

                buffer = ''
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program...")
    finally:
        log_file.close()
        ser.close()
