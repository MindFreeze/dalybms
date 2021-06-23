# HA Addon for Daly Smart BMS
Home assistant addon that monitors a Daly Smart BMS through UART USB and publishes the data to MQTT. Has MQTT discovery build in, so no need to add the sensors manually to HA.

Based on the protocol docs found here https://github.com/jblance/mpp-solar/blob/master/docs/protocols/DALY-Daly_RS485_UART_Protocol.pdf and the discussion here https://diysolarforum.com/threads/decoding-the-daly-smartbms-protocol.21898/


The main code is in monitor.py, if you want to expand or change it.