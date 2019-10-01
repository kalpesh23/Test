# Google Sheets DHT Sensor readings data storage
# Purpose: The readings from the DHT22 Sensor are written to a Google Sheet
# Author: Pritesh Lalit

# Dependencies:
#   sudo pip install --upgrade google-api-python-client  
#   sudo pip install gspread oauth2client
#   sudo apt-get install python-openssl

# Install Spidev
# 1. In Terminal type: sudo raspi-config
# 2. Navigate to: 5. Interfacing options > P4. SPI
# 3. Enable SPI interface


import json
import sys
import time
import datetime

import Adafruit_DHT

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import spidev # To communicate with SPI devices
from numpy import interp # To scale values

# Sensor Details
DHT_SENSOR_TYPE = Adafruit_DHT.DHT22
DHT_SENSOR_PIN  = 4

# Moisture sensor Channel from CH0 of the MCP3008 chip
MOISTURE_SENSOR_PIN = 0

# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0) 

# Steps to obtain Google Docs OAuth credential JSON file.  
#   http://gspread.readthedocs.org/en/latest/oauth2.html
GOOGLE_OAUTH2_JSON_FILE  = 'DHT 22 Sensor-f3e9aeee2f74.json'

# Google Docs spreadsheet name.
GOOGLE_SHEET_NAME = 'dht22sensor'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS = 10

# Retrieve the specified google sheet from Google Drive, and open the first sheet.
def open_google_sheet(oauth_key_file, spreadsheet):
    print('Attempting to load Google Sheet {0}'.format(GOOGLE_SHEET_NAME))
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        # worksheet = gc.open(spreadsheet).get_worksheet(0)  
        return worksheet
    except Exception as ex:
        # Troubleshooting items: Google Sheet name (GOOGLE_SHEET_NAME), ensure the Google Sheet is shared to the client_email address in the OAuth .json file
        print('Unable to login and get Google Sheet.  Check OAuth credentials, and or google sheet name')
        print('Opening Google Sheet failed with error:', ex)
        sys.exit(1)

def get_analog_reading(channel):
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

# Retrieve moisture reading as a percentage. 
def get_moisture_reading(pin):
    output = get_analog_reading(pin) 
    output = interp(output, [0, 1023], [0, 100])
    output = int(output)
    return output

print('Logging sensor measurements every {0} seconds to {1}.'.format(FREQUENCY_SECONDS, GOOGLE_SHEET_NAME,))
print('To quit - Press Ctrl-C')

worksheet = None

try:
    while True:
        # Login and open google sheet if necessary.
        if worksheet is None:
            worksheet = open_google_sheet(GOOGLE_OAUTH2_JSON_FILE, GOOGLE_SHEET_NAME)

        # Get Sensor reading.
        humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)
        moisture = get_moisture_reading(MOISTURE_SENSOR_PIN)
    
        # If no reading retrieved, retry after 3 seconds.
        if temp is None or humidity is None or moisture is None:
            time.sleep(3)
            continue

        # Append the data in the spreadsheet, including a timestamp
        try:
            CURRENT_DT = datetime.datetime.now()
            CURRENT_DT_Format = CURRENT_DT.strftime("%d/%m/%Y %H:%M:%S")
            print('{0} - Temperature: {1:0.1f} C; Humidity:    {2:0.1f} %; Moisture: {3:0.1f}%'.format(CURRENT_DT, temp, humidity, moisture))
            worksheet.append_row((CURRENT_DT, temp, humidity, moisture))
        except:
            print('Error occurred when logging measurements to Google Sheet')
            worksheet = None
            time.sleep(FREQUENCY_SECONDS)
            continue

        print('Measurement logged to {0}'.format(GOOGLE_SHEET_NAME))
        time.sleep(FREQUENCY_SECONDS)
except KeyboardInterrupt:
    print ('Program has quit')
