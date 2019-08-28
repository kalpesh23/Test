# Google Sheets DHT Sensor readings data storage
# Purpose: The readings from the DHT22 Sensor are written to a Google Sheet
# Author: Pritesh Lalit

# Dependencies:
#   sudo pip install --upgrade google-api-python-client  
#   sudo pip install gspread oauth2client
#   sudo apt-get install python-openssl

import json
import sys
import time
import datetime

import Adafruit_DHT

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Sensor Details
DHT_SENSOR_TYPE = Adafruit_DHT.DHT22
DHT_SENSOR_PIN  = 4


# Steps to obtain Google Docs OAuth credential JSON file.  
#   http://gspread.readthedocs.org/en/latest/oauth2.html
GOOGLE_OAUTH2_JSON_FILE       = 'DHT 22 Sensor-f3e9aeee2f74.json'

# Google Docs spreadsheet name.
GOOGLE_SHEET_NAME = 'dht22sensor'

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 30


# Retrieve the specified google sheet from Google Drive, and open the first sheet.
def open_google_sheet(oauth_key_file, spreadsheet):
    print('Attempting to load Google Sheet {0}'.format(GOOGLE_SHEET_NAME))
    try:
        scope =  ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open(spreadsheet).sheet1
        return worksheet
    except Exception as ex:
        # Troubleshooting items: Google Sheet name (GOOGLE_SHEET_NAME), ensure the Google Sheet is shared to the client_email address in the OAuth .json file
        print('Unable to login and get Google Sheet.  Check OAuth credentials, and or google sheet name')
        print('Opening Google Sheet failed with error:', ex)
        sys.exit(1)

print('Logging sensor measurements every {0} seconds to {1}.'.format(FREQUENCY_SECONDS, GOOGLE_SHEET_NAME,))
print('To quit - Press Ctrl-C')

worksheet = None

while True:
    # Login and open google sheet if necessary.
    if worksheet is None:
        worksheet = open_google_sheet(GOOGLE_OAUTH2_JSON_FILE, GOOGLE_SHEET_NAME)

    # Get Sensor reading.
    humidity, temp = Adafruit_DHT.read_retry(DHT_SENSOR_TYPE, DHT_SENSOR_PIN)

    # If no reading retrieved, retry after 3 seconds.
    if temp is None or humidity is None:
        time.sleep(3)
        continue

    # Append the data in the spreadsheet, including a timestamp
    try:
        CURRENT_DT = datetime.datetime.now().isoformat()
        print('{0} - Temperature: {1:0.1f} C; Humidity:    {2:0.1f} %'.format(CURRENT_DT, temp, humidity))
        worksheet.append_row((CURRENT_DT, temp, humidity))
    except:
        print('Error occurred when logging measurements to Google Sheet')
        worksheet = None
        time.sleep(FREQUENCY_SECONDS)
        continue

    print('Measurement logged to {0}'.format(GOOGLE_SHEET_NAME))
    time.sleep(FREQUENCY_SECONDS)

