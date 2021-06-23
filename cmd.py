#!/usr/bin/python3

import serial
import binascii
import sys

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # open serial port

def cmd(command):
    res = []
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        print(binascii.hexlify(s, ' '))
        res.append(s)
    return res

def get_cell_v(cell_count):
    command = sys.argv[1]
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        print(binascii.hexlify(s, ' '))
    
ser.close()
print('done')