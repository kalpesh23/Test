#!/usr/bin/python

# DHT Sensor Data-Loading
# Author: Pritesh Lalit

import sys
import datetime
import time
import json

import Adafruit_DHT

# Sensor Type
DHT_TYPE = Adafruit_DHT.DHT22

# Pin the sensor is connected to the Raspberry Pi on
DHT_PIN = 23

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 30

print('Logging sensor measurements every {0} seconds.'.format(FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')

while True:
    # Attempt to get sensor reading.
    humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)

    # Skip to the next reading if a valid measurement couldn't be taken.
    # This might happen if the CPU is under a lot of load and the sensor
    # can't be reliably read (timing is critical to read the sensor).
    if humidity is None or temp is None:
        time.sleep(2)
        continue

    print('Temperature: {0:0.1f} C - Humidity: {1:0.1f} %'.format(temp, humidity))
    time.sleep(FREQUENCY_SECONDS)