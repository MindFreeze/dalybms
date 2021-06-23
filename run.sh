#!/bin/bash
CONFIG_PATH=/data/options.json

MQTT_SERVER="$(jq --raw-output '.mqtt_server' $CONFIG_PATH)" \
MQTT_USER="$(jq --raw-output '.mqtt_user' $CONFIG_PATH)" \
MQTT_PASS="$(jq --raw-output '.mqtt_pass' $CONFIG_PATH)" \
MQTT_CLIENT_ID="$(jq --raw-output '.mqtt_client_id' $CONFIG_PATH)" \
MQTT_TOPIC_DISCOVERY="$(jq --raw-output '.mqtt_topic_discovery' $CONFIG_PATH)" \
MQTT_TOPIC_CELLS="$(jq --raw-output '.mqtt_topic_cells' $CONFIG_PATH)" \
MQTT_TOPIC="$(jq --raw-output '.mqtt_topic' $CONFIG_PATH)" \
DEVICE="$(jq --raw-output '.device' $CONFIG_PATH)" \
DEVICE_ID="$(jq --raw-output '.device_id' $CONFIG_PATH)" \
python3 /monitor.py