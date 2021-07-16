#!/bin/bash
CONFIG_PATH=/data/options.json

MQTT_SERVER="$(jq --raw-output '.mqtt_server' $CONFIG_PATH)" \
MQTT_USER="$(jq --raw-output '.mqtt_user' $CONFIG_PATH)" \
MQTT_PASS="$(jq --raw-output '.mqtt_pass' $CONFIG_PATH)" \
MQTT_CLIENT_ID="$(jq --raw-output '.mqtt_client_id' $CONFIG_PATH)" \
MQTT_DISCOVERY_PREFIX="$(jq --raw-output '.mqtt_discovery_prefix' $CONFIG_PATH)" \
DEVICE="$(jq --raw-output '.device' $CONFIG_PATH)" \
DEVICE_ID="$(jq --raw-output '.device_id' $CONFIG_PATH)" \
CELL_COUNT="$(jq --raw-output '.cells_in_series' $CONFIG_PATH)" \
python3 /monitor.py