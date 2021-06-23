#!/usr/bin/python3

import binascii
import os

def strip_overhead(buffer):
    return s[5:12]

def extract_cells_v(buffer):
    return [
        int.from_bytes(buffer[5:7], byteorder='big', signed=False),
        int.from_bytes(buffer[7:9], byteorder='big', signed=False),
        int.from_bytes(buffer[9:11], byteorder='big', signed=False)
    ]

# s = b'\xa5\x01\x95\x08\x01\x0e\xc0\x0e\xc2\x0e\xc7\x20\xd7'
# s = b'\xa5\x01\x95\x08\x01\r\x11\r\x12\r\x1cT\xfe'
# s1 = b'\xa5\x01\x95\x08\x02\r\x08\r\x1d\r\x14T\xf9'
# s2 = b'\xa5\x01\x95\x08\x03\r\x1c\r\x1e\r\x14T\x0f'
# s3 = b'\xa5\x01\x95\x08\x04\r\x12\r\x0f\r\x1cT\xff'
# s4 = b'\xa5\x01\x95\x08\x05\r\x0b\r\x14\r\x15T\xf7'
# s5 = b'\xa5\x01\x95\x08\x06\r\x17\r\x14\r\x15T\x04'
s = b'\xa5\x01\x95\x08\x01\x0c\xfc\x0c\xf6\x0d\x05\x54\xb4'
s1 = b'\xa5\x01\x95\x08\x02\x0c\xea\x0d\x04\x0c\xf7\x54\xa3'
s2 = b'\xa5\x01\x95\x08\x03\x0d\x06\x0d\x01\x0c\xff\x54\xc6'
s3 = b'\xa5\x01\x95\x08\x04\x0c\xf8\x0c\xe7\x0d\x00\x54\x9f'
s4 = b'\xa5\x01\x95\x08\x05\x0c\xf2\x0c\xee\x0d\x01\x54\xa2'
s5 = b'\xa5\x01\x95\x08\x06\x0c\xfd\x0c\xee\x0d\x01\x54\xae'

cells = extract_cells_v(s) + extract_cells_v(s1) + extract_cells_v(s2) + extract_cells_v(s3) + extract_cells_v(s4) + extract_cells_v(s5)
cells = cells[:16]
print(cells)
print(len(cells))

json = '{'
sum = 0
for i in range(len(cells)):
    cells[i] = cells[i]/1000
    sum += cells[i]
    json += '"cell_' + str(i+1) + '":' + str(cells[i]) + ','
json += '"sum":' + str(sum) + ','
json += '"avg":' + str(sum/16) + ','
json += '"diff":' + str(max(cells) - min(cells))
json += '}'
print(json)