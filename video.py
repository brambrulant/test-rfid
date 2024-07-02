#!/usr/bin/python2
import serial
import re
import sys
import signal
import os
import time
import datetime
from subprocess import Popen

BITRATE = 38400
# for videos
movie1 = "/home/pi/Videos/movie1.mp4"
movie2 = "/home/pi/Videos/movie2.mp4"
movie3 = "/home/pi/Videos/movie3.mp4"
movie4 = "/home/pi/Videos/movie4.mp4"
movie5 = "/home/pi/Videos/movie5.mp4"

# declare RF cards
rfcard1 = '3000E2000019060C00770650D633EB30'
rfcard2 = '3000E2000019060C01360510E09F488D'
rfcard3 = '3000E2000019060C00960530E04B2A76'
rfcard4 = '3000E2000019060C00520560DFEC1EA0'
rfcard5 = '3000E2000019060C02220530E14A251E'
rfcard6 = '3000E2000019060C00531080AEC17D85'

# Add RF cards Number Here as well
CARDS = [
    '3000E2000019060C00770650D633EB30',
    '3000E2000019060C01360510E09F488D',
    '3000E2000019060C00960530E04B2A76',
    '3000E2000019060C00520560DFEC1EA0',
    '3000E2000019060C02220530E14A251E',
    '3000E2000019060C00531080AEC17D85'
]

if __name__ == '__main__':
    buffer = ''
    ser = serial.Serial('/dev/ttyUSB0', BITRATE, timeout=0)
    rfidPattern = re.compile(b'[\W_]+')

    while True:
        # Read data from RFID reader
        read = buffer + ser.read(ser.inWaiting())
        buffer = read.replace("U", "")

        if '\n' in buffer:
            lines = buffer.split('\n')
            last_received = lines[-2]
            match = rfidPattern.sub('', last_received)

            if match:
                print(match)
                if match == rfcard1:
                    print('1st card')
                    os.system('killall omxplayer.bin')
                    omxc = Popen(['omxplayer', '-b', movie1])

                elif match == rfcard2:
                    print('2nd card')
                    os.system('killall omxplayer.bin')
                    omxc = Popen(['omxplayer', '-b', movie2])

                elif match == rfcard3:
                    print('3rd card')
                    os.system('killall omxplayer.bin')
                    omxc = Popen(['omxplayer', '-b', movie3])

                elif match == rfcard4:
                    print('4th card')
                    os.system('killall omxplayer.bin')
                    omxc = Popen(['omxplayer', '-b', movie4])

                elif match == rfcard5:
                    print('5th card')
                    os.system('killall omxplayer.bin')
                    omxc = Popen(['omxplayer', '-b', movie5])

                elif match == rfcard6:  # For Killing the Video
                    print('6th card')
                    os.system('killall omxplayer.bin')
                    player = False

            buffer = ''
            lines = ''
        time.sleep(0.1)
