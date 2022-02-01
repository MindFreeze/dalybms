#!/usr/bin/python3

# Protocol docs https://github.com/jblance/mpp-solar/blob/master/docs/protocols/DALY-Daly_RS485_UART_Protocol.pdf
# Protocol examples and more info https://diysolarforum.com/threads/decoding-the-daly-smartbms-protocol.21898/

import serial
import binascii
import time
import os
import paho.mqtt.client as mqtt

print('Starting BMS monitor...')

# ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # open serial port
ser = serial.Serial(os.environ['DEVICE'], 9600, timeout=1)  # open serial port

# connect to MQTT server
client = mqtt.Client(client_id=os.environ['MQTT_CLIENT_ID'])
client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASS'])
client.connect(os.environ['MQTT_SERVER'])

devId = os.environ['DEVICE_ID']
BASE_TOPIC = os.environ['MQTT_DISCOVERY_PREFIX'] + '/sensor/'
STATE_TOPIC = BASE_TOPIC + devId
STATUS_TOPIC = STATE_TOPIC + '_status'
deviceConf = '"device": {"manufacturer": "Dongfuan Daly Electronics", "name": "Smart BMS", "identifiers": ["' + devId + '"]}'
# publish MQTT Discovery configs to Home Assistant
socHaConf = '{"device_class": "battery", "name": "Battery SOC", "state_topic": "' + STATE_TOPIC +'/state", "unit_of_measurement": "%", "value_template": "{{ value_json.soc}}", "unique_id": "' + devId + '_soc", ' + deviceConf + ', "json_attributes_topic": "' + STATUS_TOPIC + '/state"}' 
client.publish(STATE_TOPIC +'_soc/config', socHaConf, 0, True)
voltageHaConf = '{"device_class": "voltage", "name": "Battery Voltage", "state_topic": "' + STATE_TOPIC +'/state", "unit_of_measurement": "V", "value_template": "{{ value_json.voltage}}", "unique_id": "' + devId + '_voltage", ' + deviceConf + '}'
client.publish(STATE_TOPIC + '_voltage/config', voltageHaConf, 0, True)
currentHaConf = '{"device_class": "current", "name": "Battery Current", "state_topic": "' + STATE_TOPIC +'/state", "unit_of_measurement": "A", "value_template": "{{ value_json.current}}", "unique_id": "' + devId + '_current", ' + deviceConf + '}' 
client.publish(STATE_TOPIC + '_current/config', currentHaConf, 0, True)

CELLS_TOPIC = STATE_TOPIC + '_balance'
cellsHaConf = '{"device_class": "voltage", "name": "Battery Cell Balance", "state_topic": "' + CELLS_TOPIC + '/state", "unit_of_measurement": "V", "value_template": "{{ value_json.diff}}", "json_attributes_topic": "' + CELLS_TOPIC + '/state", "unique_id": "' + devId + '_balance", ' + deviceConf + '}' 
client.publish(CELLS_TOPIC + '/config', cellsHaConf, 0, True)

TEMP_TOPIC = STATE_TOPIC + '_temp'
tempHaConf = '{"device_class": "temperature", "name": "Battery Temperature", "state_topic": "' + TEMP_TOPIC + '/state", "unit_of_measurement": "°C", "value_template": "{{ value_json.value}}", "unique_id": "' + devId + '_temp", ' + deviceConf + ', "json_attributes_topic": "' + TEMP_TOPIC + '/state"}'
client.publish(TEMP_TOPIC + '/config', tempHaConf, 0, True)

def cmd(command):
    res = []
    ser.write(command)
    while True:
        s = ser.read(13)
        if (s == b''):
            break
        # print(binascii.hexlify(s, ' '))
        res.append(s)
    return res

def publish(topic, data):
    try:
        client.publish(topic, data, 0, False)
    except Exception as e:
        print("Error sending to mqtt: " + str(e))

def extract_cells_v(buffer):
    return [
        int.from_bytes(buffer[5:7], byteorder='big', signed=False),
        int.from_bytes(buffer[7:9], byteorder='big', signed=False),
        int.from_bytes(buffer[9:11], byteorder='big', signed=False)
    ]

def get_cell_balance(cell_count):
    res = cmd(b'\xa5\x40\x95\x08\x00\x00\x00\x00\x00\x00\x00\x00\x82')
    if len(res) < 1:
        print('Empty response get_cell_balance')
        return
    cells = []
    for frame in res:
        cells += extract_cells_v(frame)
    cells = cells[:cell_count]
    json = '{'
    sum = 0
    for i in range(cell_count):
        cells[i] = cells[i]/1000
        sum += cells[i]
        json += '"cell_' + str(i+1) + '":' + str(cells[i]) + ','
    json += '"sum":' + str(round(sum, 1)) + ','
    json += '"avg":' + str(round(sum/16, 3)) + ','
    min_v = min(cells)
    max_v = max(cells)
    json += '"min":' + str(min_v) + ','
    json += '"minCell":' + str(cells.index(min_v) + 1) + ','
    json += '"max":' + str(max_v) + ','
    json += '"maxCell":' + str(cells.index(max_v) + 1) + ','
    json += '"diff":' + str(round(max_v - min_v, 3))
    json += '}'
    # print(json)
    publish(CELLS_TOPIC + '/state', json)

def get_battery_state():
    res = cmd(b'\xa5\x40\x90\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7d')
    if len(res) < 1:
        print('Empty response get_battery_state')
        return
    buffer = res[0]
    voltage = int.from_bytes(buffer[4:6], byteorder='big', signed=False) / 10
    aquisition = int.from_bytes(buffer[6:8], byteorder='big', signed=False) / 10
    current = int.from_bytes(buffer[8:10], byteorder='big', signed=False) / 10 - 3000
    soc = int.from_bytes(buffer[10:12], byteorder='big', signed=False) / 10

    json = '{'
    json += '"voltage":' + str(voltage) + ','
    json += '"aquisition":' + str(aquisition) + ','
    json += '"current":' + str(round(current, 1)) + ','
    json += '"soc":' + str(soc)
    json += '}'
    print(json)
    publish(STATE_TOPIC +'/state', json)

def get_battery_status():
    res = cmd(b'\xa5\x40\x94\x08\x00\x00\x00\x00\x00\x00\x00\x00\x81')
    if len(res) < 1:
        print('Empty response get_battery_status')
        return
    buffer = res[0]
    batt_string = int.from_bytes(buffer[4:5], byteorder='big', signed=False)
    # this temperature seems to always be 1
    temp = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    charger = 'true' if int.from_bytes(buffer[6:7], byteorder='big', signed=False) == 1 else 'false'
    load = 'true' if int.from_bytes(buffer[7:8], byteorder='big', signed=False) == 1 else 'false'
    # dido = buffer[8:9]
    cycles = int.from_bytes(buffer[9:11], byteorder='big', signed=False)

    json = '{'
    json += '"batt_string":' + str(batt_string) + ','
    json += '"temp":' + str(temp) + ','
    json += '"charger":' + charger + ','
    json += '"load":' + load + ','
    json += '"cycles":' + str(cycles)
    json += '}'
    # print(json)
    publish(STATUS_TOPIC +'/state', json)

def get_battery_temp():
    res = cmd(b'\xa5\x40\x92\x08\x00\x00\x00\x00\x00\x00\x00\x00\x7f')
    if len(res) < 1:
        print('Empty response get_battery_temp')
        return
    buffer = res[0]
    maxTemp = int.from_bytes(buffer[4:5], byteorder='big', signed=False) - 40
    maxTempCell = int.from_bytes(buffer[5:6], byteorder='big', signed=False)
    minTemp = int.from_bytes(buffer[6:7], byteorder='big', signed=False) - 40
    minTempCell = int.from_bytes(buffer[7:8], byteorder='big', signed=False)

    json = '{'
    json += '"value":' + str((maxTemp + minTemp) / 2) + ','
    json += '"maxTemp":' + str(maxTemp) + ','
    json += '"maxTempCell":' + str(maxTempCell) + ','
    json += '"minTemp":' + str(minTemp) + ','
    json += '"minTempCell":' + str(minTempCell)
    json += '}'
    # print(json)
    publish(TEMP_TOPIC +'/state', json)

while True:
    get_battery_state()
    get_cell_balance(int(os.environ['CELL_COUNT']))
    get_battery_status()
    get_battery_temp()
    time.sleep(1)
    
ser.close()
print('done')