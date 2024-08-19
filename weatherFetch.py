# The purpose of this module is the backend logic that creates weather API requests,
# creates the virtual BACnet device, whilst also populating the analog values of the BACnet device.
# This software package was developed by Brendan White whilst interning at Johnson Controls Australia (North Ryde)
# Source code may only be altered by an authorised employee of Johnson Controls
# External entities must not attempt to obtain or reproduce this source code.
# Version 1.0, date modified: 12.08.2024

# python library declaration
import math
import requests
from BAC0.core.devices.local.models import (
    analog_value
)
import BAC0
import time
import datetime

current_time = datetime.datetime.now()
import xml.etree.ElementTree as ET
from xml.dom import minidom
import threading
from datetime import datetime
import pytz
import sys
import uuid

# Global variables for weather data
current_temperature = 0
humidity = 0
current_dew_point = 0
current_enthalpy = 0
hourly_temperatures = []
hourly_humidity = []
max_temperature = 0
min_temperature = 0
max_humidity = 0
min_humidity = 0
dew_point3hr = 0
dew_point6hr = 0
dew_point9hr = 0
dew_point12hr = 0
dew_point15hr = 0
dew_point18hr = 0
dew_point21hr = 0
dew_point24hr = 0
enthalpy3hr = 0
enthalpy6hr = 0
enthalpy9hr = 0
enthalpy12hr = 0
enthalpy15hr = 0
enthalpy18hr = 0
enthalpy21hr = 0
enthalpy24hr = 0
BOMtemp0h = 0
BOMtemp3h = 0
BOMtemp6h = 0
BOMtemp9h = 0
BOMtemp12h = 0
BOMtemp15h = 0 
BOMtemp18h = 0
BOMtemp21h = 0
BOMtemp24h = 0
BOMhumidity0h = BOMhumidity3h = BOMhumidity6h = BOMhumidity9h = BOMhumidity12h = BOMhumidity15h = BOMhumidity18h = BOMhumidity21h = BOMhumidity24h = 0
BOMdewpoint0h = BOMdewpoint3h = BOMdewpoint6h = BOMdewpoint9h = BOMdewpoint12h = BOMdewpoint15h = BOMdewpoint18h = BOMdewpoint21h = BOMdewpoint24h = 0
BOMenthalpy0h = BOMenthalpy3h = BOMenthalpy6h = BOMenthalpy9h = BOMenthalpy12h = BOMenthalpy15h = BOMenthalpy18h = BOMenthalpy21h = BOMenthalpy24h = 0
BOMmax_dewpoint = BOMmax_enthalpy = BOMmax_humidity = BOMmax_temp = 0
BOMminimum_dewpoint = BOMminimum_enthalpy = BOMminimum_humidity = BOMminimum_temp = 0

lat = None
lon = None
api_token = None
device_Id = None
port_Id = None
IP_address = None

    # fetches the device MAC address
def getDeviceMacAddress():
    mac = uuid.getnode()
    return mac

    # takes the device MAC address and compares it to the verification method of * 263
def verifyKey():
    multiplier = 263
    current_mac = getDeviceMacAddress()
    expected_value = current_mac * multiplier
    
    # Read the value from the text file
    with open("./nssm-2.24/license_key.txt", "r") as f:
        real_value = int(f.read().strip())  # Convert the read value to an integer
    
    if expected_value == real_value:
        return True
    else:
        return False
    
    # reads the configured device settings, populates variables and feeds them to the requesting logic to create a specific query
def readXMLSettings():
    global lat
    global lon
    global altitude
    global api_token
    global device_Id
    global IP_address
    global port_Id
    global num_requests

    xmlfile = 'C:\\BACnetWeatherFetchData\settings.xml'
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    # Extract values from the XML
    lat = float(root.find('latitude').text)
    lon = float(root.find('longitude').text)
    altitude = float(root.find('altitude').text)
    api_token = root.find('api_token').text
    device_Id = int(root.find('device_Id').text)
    # Check if the IP address is '0' and set it to None if it is
    ip_address_element = root.find('ip_address')
    if ip_address_element.text == '0':
        IP_address = None
    else:
        IP_address = str(ip_address_element.text)
    
    port_Id = int(root.find('port_Id').text)
    num_requests = int(root.find('num_requests').text)
   
    # Number of requests per day calculation, this will just be thread calculation time
def setDailyRequests(num_requests):
    daily_to_hourly = 24 / num_requests
    hourly_to_mins = 60 * daily_to_hourly
    sleeptime = hourly_to_mins * 60
    return sleeptime

    

# Function to calculate the dew point
def dewPointCalc(temp, humidity, altitude):
    a = 17.27
    b = 237.7
    deltaTemp = temp - ((6.5 / 1000) * altitude) # temperature typically decreases at a rate of 6.5 deg C for every 1000m (standard lapse rate)
    alpha = ((a * deltaTemp) / (b + deltaTemp)) + math.log(humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

# Function to calculate the enthalpy
def enthalpyCalc(temp, humidity, altitude):
    dew_point = dewPointCalc(temp, humidity, altitude)
    deltaTemp = temp - ((6.5 / 1000) * altitude) # refer to comment above and (standard lapse rate)
    h = 1.006 * deltaTemp
    latent_heat = 2501
    specific_humidity = 0.622 * (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)) / (1013.25 - (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)))
    enthalpy = h + (latent_heat * specific_humidity)

    return enthalpy

# fetch logic for Open Weather API 
def fetchWeatherData(lat, lon, api_token):
    # Read settings from XML
    tree = ET.parse('C:\\BACnetWeatherFetchData\\settings.xml')
    root = tree.getroot()

    lat = float(root.find('latitude').text)
    lon = float(root.find('longitude').text)
    api_token = root.find('api_token').text
    api_source = int(root.find('OpenWeather_api_source').text)
    altitude = float(root.find('altitude').text)

    # Define global variables to be used in updating analog_values on BACnet device
    global current_temperature, humidity, current_dew_point, current_enthalpy, hourly_temperatures, hourly_humidity, max_temperature, min_temperature, min_humidity, max_humidity
    global dew_point3hr, dew_point6hr, dew_point9hr, dew_point12hr, dew_point15hr, dew_point18hr, dew_point21hr, dew_point24hr, minEnthalpy, minDewpt
    global enthalpy3hr, enthalpy6hr, enthalpy9hr, enthalpy12hr, enthalpy15hr, enthalpy18hr, enthalpy21hr, enthalpy24hr, maximumDewPt, maximumEnthalpy

    # Check if the API source is enabled
    if api_source == 0:
        # Set all global variables to 0
        current_temperature = 0
        humidity = 0
        current_dew_point = 0
        current_enthalpy = 0
        hourly_temperatures = [0] * 9
        hourly_humidity = [0] * 9
        max_temperature = 0
        min_temperature = 0
        min_humidity = 0
        max_humidity = 0
        dew_point3hr = 0
        dew_point6hr = 0
        dew_point9hr = 0
        dew_point12hr = 0
        dew_point15hr = 0
        dew_point18hr = 0
        dew_point21hr = 0
        dew_point24hr = 0
        minEnthalpy = 0
        minDewpt = 0
        enthalpy3hr = 0
        enthalpy6hr = 0
        enthalpy9hr = 0
        enthalpy12hr = 0
        enthalpy15hr = 0
        enthalpy18hr = 0
        enthalpy21hr = 0
        enthalpy24hr = 0
        maximumDewPt = 0
        maximumEnthalpy = 0
        return

    # Open Weather Map API with 3 arguments, latitude, longitude and weather api token. Metric by default
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_token}'
    response = requests.get(url)
    data = response.json()

    try:
        # Key data pulled from the API 
        hourly_data = data['list'][0:9]
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        hourly_humidity = [hour['main']['humidity'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        min_temperature = min(hourly_temperatures)
        current_temperature = data['list'][0]['main']['temp']
        humidity = data['list'][0]['main']['humidity']
        min_humidity = min(hourly_humidity)
        max_humidity = max(hourly_humidity)

        # Data for dew point and enthalpy calculated via custom functions
        current_dew_point = dewPointCalc(current_temperature, humidity, altitude)
        dew_point3hr = dewPointCalc(hourly_temperatures[1], hourly_humidity[1], altitude)
        dew_point6hr = dewPointCalc(hourly_temperatures[2], hourly_humidity[2], altitude)
        dew_point9hr = dewPointCalc(hourly_temperatures[3], hourly_humidity[3], altitude)
        dew_point12hr = dewPointCalc(hourly_temperatures[4], hourly_humidity[4], altitude)
        dew_point15hr = dewPointCalc(hourly_temperatures[5], hourly_humidity[5], altitude)
        dew_point18hr = dewPointCalc(hourly_temperatures[6], hourly_humidity[6], altitude)
        dew_point21hr = dewPointCalc(hourly_temperatures[7], hourly_humidity[7], altitude)
        dew_point24hr = dewPointCalc(hourly_temperatures[8], hourly_humidity[8], altitude)
        current_enthalpy = enthalpyCalc(current_temperature, humidity, altitude)
        enthalpy3hr = enthalpyCalc(hourly_temperatures[1], hourly_humidity[1], altitude)
        enthalpy6hr = enthalpyCalc(hourly_temperatures[2], hourly_humidity[2], altitude)
        enthalpy9hr = enthalpyCalc(hourly_temperatures[3], hourly_humidity[3], altitude)
        enthalpy12hr = enthalpyCalc(hourly_temperatures[4], hourly_humidity[4], altitude)
        enthalpy15hr = enthalpyCalc(hourly_temperatures[5], hourly_humidity[5], altitude)
        enthalpy18hr = enthalpyCalc(hourly_temperatures[6], hourly_humidity[6], altitude)
        enthalpy21hr = enthalpyCalc(hourly_temperatures[7], hourly_humidity[7], altitude)
        enthalpy24hr = enthalpyCalc(hourly_temperatures[8], hourly_humidity[8], altitude)

        hourlydewpoint = [current_dew_point, dew_point3hr, dew_point6hr, dew_point9hr, dew_point12hr, dew_point15hr, dew_point18hr, dew_point21hr, dew_point24hr]
        maximumDewPt = max(hourlydewpoint)
        hourlyEnthalpy = [current_enthalpy, enthalpy3hr, enthalpy6hr, enthalpy9hr, enthalpy12hr, enthalpy15hr, enthalpy18hr, enthalpy21hr, enthalpy24hr]
        minEnthalpy = min(hourlyEnthalpy)
        minDewpt = min(hourlydewpoint)
        maximumEnthalpy = max(hourlyEnthalpy)

    except KeyError:
        print("Error fetching initial weather data")

# store the collected data into a dictionary and format/ write to xml format
def writeXMLWeatherData():
        # Define the data
    data = {
        "temp3hr": hourly_temperatures[1],
        "temp6hr": hourly_temperatures[2],
        "temp9hr": hourly_temperatures[3],
        "temp12hr": hourly_temperatures[4],
        "temp15hr": hourly_temperatures[5],
        "temp18hr": hourly_temperatures[6],
        "temp21hr": hourly_temperatures[7],
        "temp24hr": hourly_temperatures[8],
        "current_temperature": current_temperature,
        "hum3hr": hourly_humidity[1],
        "hum6hr": hourly_humidity[2],
        "hum9hr": hourly_humidity[3],
        "hum12hr": hourly_humidity[4],
        "hum15hr": hourly_humidity[5],
        "hum18hr": hourly_humidity[6],
        "hum21hr": hourly_humidity[7],
        "hum24hr": hourly_humidity[8],
        "max_temperature": max_temperature,
        "max_humidity": max_humidity,
        "minimum_humidity": min_humidity,
        "minimum_temperature": min_temperature,
        "humidity": humidity,
        "current_dew_point": current_dew_point,
        "dew_point3hr": dew_point3hr,
        "dew_point6hr": dew_point6hr,
        "dew_point9hr": dew_point9hr,
        "dew_point12hr": dew_point12hr,
        "dew_point15hr": dew_point15hr,
        "dew_point18hr": dew_point18hr,
        "dew_point21hr": dew_point21hr,
        "dew_point24hr": dew_point24hr,
        "current_enthalpy": current_enthalpy,
        "enthalpy3hr": enthalpy3hr,
        "enthalpy6hr": enthalpy6hr,
        "enthalpy9hr": enthalpy9hr,
        "enthalpy12hr": enthalpy12hr,
        "enthalpy15hr": enthalpy15hr,
        "enthalpy18hr": enthalpy18hr,
        "enthalpy21hr": enthalpy21hr,
        "enthalpy24hr": enthalpy24hr,
        "max_dewpt": maximumDewPt,
        "max_enthalpy": maximumEnthalpy,
        "minimum_dewpt": minDewpt,
        "minimum_enthalpy": minEnthalpy
    }
    # Create an XML structure
    root = ET.Element("weather_data")

    # Add child elements for each key-value pair in the data dictionary
    for key, value in data.items():
        elem = ET.SubElement(root, key)
        elem.text = str(value)

    # Save the XML to a file
    tree_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(tree_str).toprettyxml(indent="  ")

    with open("C:\\BACnetWeatherFetchData\weather_data.xml", "w") as xml_file:
        xml_file.write(pretty_xml)



# calculate the altitude effect on dew point (Open meteo portion)
def deltaDewPoint(initialDewPt, altitude):
    dew_point_change_rate = 0.2 / 100  # °C per meter
    # Calculate the dew point change
    dew_point_change = dew_point_change_rate * altitude

    # Calculate the adjusted dew point
    adjusted_dew_point = initialDewPt - dew_point_change

    return adjusted_dew_point


# calculate the altitude effect on enthalpy (open meteo portion)
def deltaEnthalpy(initialEnthalpy, altitude):
    # Enthalpy change rate (approximation)
    enthalpy_change_rate = 0.0065  # kJ/kg per meter
    # Calculate the enthalpy change
    enthalpy_change = enthalpy_change_rate * altitude

    # Calculate the adjusted enthalpy
    adjusted_enthalpy = initialEnthalpy - enthalpy_change

    return adjusted_enthalpy


def calculate_specific_humidity(temperature, relative_humidity):
    # Calculate the saturation vapor pressure (in hPa)
    es = 6.112 * 10**((7.5 * temperature) / (237.7 + temperature))
    # Calculate the actual vapor pressure (in hPa)
    e = es * (relative_humidity / 100)
    # Calculate the specific humidity (in kg/kg)
    specific_humidity = 0.622 * e / (1013.25 - e)
    return specific_humidity

def calculate_enthalpy(temperature, specific_humidity):
    # Constants
    cp = 1.006  # Specific heat capacity of dry air (kJ/kg·°C)
    cpv = 1.86  # Specific heat capacity of water vapor (kJ/kg·°C)
    Lv = 2501  # Latent heat of vaporization (kJ/kg)
    
    # Calculate enthalpy (kJ/kg)
    enthalpy = cp * temperature + specific_humidity * (cpv * temperature + Lv)
    return enthalpy


    # logic associated with Open Meteo API source
def fetchOpenMeteoWeather(lat, lon):
    # Make weather information global to access it inside other functions
    global BOMtemp0h, BOMtemp3h, BOMtemp6h, BOMtemp9h, BOMtemp12h, BOMtemp15h, BOMtemp18h, BOMtemp21h, BOMtemp24h
    global BOMhumidity0h, BOMhumidity3h, BOMhumidity6h, BOMhumidity9h, BOMhumidity12h, BOMhumidity15h, BOMhumidity18h, BOMhumidity21h, BOMhumidity24h
    global BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h, BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h
    global BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h, BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h
    global BOMmax_dewpoint, BOMmax_enthalpy, BOMmax_humidity, BOMmax_temp
    global BOMminimum_dewpoint, BOMminimum_enthalpy, BOMminimum_humidity, BOMminimum_temp

    # Read settings from XML
    tree = ET.parse('C:\\BACnetWeatherFetchData\\settings.xml')
    root = tree.getroot()
    api_source = int(root.find('OpenMeteo_api_source').text)

    # Check if the API source is enabled
    if api_source == 0:
        # Set all global variables to 0
        BOMtemp0h = 0
        BOMtemp3h = 0
        BOMtemp6h = 0
        BOMtemp9h = 0
        BOMtemp12h = 0
        BOMtemp15h = 0
        BOMtemp18h = 0
        BOMtemp21h = 0
        BOMtemp24h = 0
        BOMhumidity0h = 0
        BOMhumidity3h = 0
        BOMhumidity6h = 0
        BOMhumidity9h = 0
        BOMhumidity12h = 0
        BOMhumidity15h = 0
        BOMhumidity18h = 0
        BOMhumidity21h = 0
        BOMhumidity24h = 0
        BOMdewpoint0h = 0
        BOMdewpoint3h = 0
        BOMdewpoint6h = 0
        BOMdewpoint9h = 0
        BOMdewpoint12h = 0
        BOMdewpoint15h = 0
        BOMdewpoint18h = 0
        BOMdewpoint21h = 0
        BOMdewpoint24h = 0
        BOMenthalpy0h = 0
        BOMenthalpy3h = 0
        BOMenthalpy6h = 0
        BOMenthalpy9h = 0
        BOMenthalpy12h = 0
        BOMenthalpy15h = 0
        BOMenthalpy18h = 0
        BOMenthalpy21h = 0
        BOMenthalpy24h = 0
        BOMmax_dewpoint = 0
        BOMmax_enthalpy = 0
        BOMmax_humidity = 0
        BOMmax_temp = 0
        BOMminimum_dewpoint = 0
        BOMminimum_enthalpy = 0
        BOMminimum_humidity = 0
        BOMminimum_temp = 0

        # runs this function to create an XML of the data
        writeWeatherDataToXML(BOMtemp0h, BOMtemp3h, BOMtemp6h, BOMtemp9h, BOMtemp12h, BOMtemp15h, BOMtemp18h, BOMtemp21h, BOMtemp24h,
        BOMhumidity0h, BOMhumidity3h, BOMhumidity6h, BOMhumidity9h, BOMhumidity12h, BOMhumidity15h, BOMhumidity18h, BOMhumidity21h, BOMhumidity24h,
        BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h, BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h,
        BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h, BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h,
        BOMmax_temp, BOMmax_humidity, BOMmax_dewpoint, BOMmax_enthalpy,
        BOMminimum_temp, BOMminimum_humidity, BOMminimum_dewpoint, BOMminimum_enthalpy)

        return

    # Define the URL for the Open-Meteo API
    url = "https://api.open-meteo.com/v1/forecast"

    # Define the parameters for the API request
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m"],
        "timezone": "Australia/Sydney",
        "forecast_days": 2,
        "models": "bom_access_global"
    }

    # Make the API request
    responses = requests.get(url, params=params, verify=False)
    data = responses.json()

    # Extract data every 3 hours starting from the 10th or 11th value based on DST
    hourly_data = data['hourly']
    filtered_data = {
        'time': [],
        'temperature_2m': [],
        'relative_humidity_2m': [],
        'dew_point_2m': [],
        'enthalpy': []
    }   

    # Define the Sydney timezone
    sydney_tz = pytz.timezone('Australia/Sydney')

    # Get the current hour in military time
    now = datetime.now(sydney_tz)
    current_hour = now.hour

    # Start from the current hour and take every 3rd element up to +24 hours
    # this logic uses system time to calculate the element that it uses
    for i in range(current_hour, current_hour + 25, 3):
        index = i % 25  # Ensure the index wraps around if it exceeds 24
        if index >= len(hourly_data['time']):
            break
        # Extract and assign each element to a corresponding variable
        time = hourly_data['time'][index]
        temperature_2m = hourly_data['temperature_2m'][index]
        relative_humidity_2m = hourly_data['relative_humidity_2m'][index]
        dew_point_2m = hourly_data['dew_point_2m'][index]
        
        # Calculate specific humidity
        specific_humidity = calculate_specific_humidity(temperature_2m, relative_humidity_2m)
        
        # Calculate enthalpy
        enthalpy = calculate_enthalpy(temperature_2m, specific_humidity)
        
        # Append to filtered_data
        filtered_data['time'].append(time)
        filtered_data['temperature_2m'].append(temperature_2m)
        filtered_data['relative_humidity_2m'].append(relative_humidity_2m)
        filtered_data['dew_point_2m'].append(dew_point_2m)
        filtered_data['enthalpy'].append(enthalpy)

    # Assign the data to individual variables
    BOMtemp0h = filtered_data['temperature_2m'][0]
    BOMtemp3h = filtered_data['temperature_2m'][1]
    BOMtemp6h = filtered_data['temperature_2m'][2]
    BOMtemp9h = filtered_data['temperature_2m'][3]
    BOMtemp12h = filtered_data['temperature_2m'][4]
    BOMtemp15h = filtered_data['temperature_2m'][5]
    BOMtemp18h = filtered_data['temperature_2m'][6]
    BOMtemp21h = filtered_data['temperature_2m'][7]
    BOMtemp24h = filtered_data['temperature_2m'][8]

    BOMhumidity0h = filtered_data['relative_humidity_2m'][0]
    BOMhumidity3h = filtered_data['relative_humidity_2m'][1]
    BOMhumidity6h = filtered_data['relative_humidity_2m'][2]
    BOMhumidity9h = filtered_data['relative_humidity_2m'][3]
    BOMhumidity12h = filtered_data['relative_humidity_2m'][4]
    BOMhumidity15h = filtered_data['relative_humidity_2m'][5]
    BOMhumidity18h = filtered_data['relative_humidity_2m'][6]
    BOMhumidity21h = filtered_data['relative_humidity_2m'][7]
    BOMhumidity24h = filtered_data['relative_humidity_2m'][8]

    # Adjust the dew point values based on the altitude change
    BOMdewpoint0h = deltaDewPoint(filtered_data['dew_point_2m'][0], altitude)
    BOMdewpoint3h = deltaDewPoint(filtered_data['dew_point_2m'][1], altitude)
    BOMdewpoint6h = deltaDewPoint(filtered_data['dew_point_2m'][2], altitude)
    BOMdewpoint9h = deltaDewPoint(filtered_data['dew_point_2m'][3], altitude)
    BOMdewpoint12h = deltaDewPoint(filtered_data['dew_point_2m'][4], altitude)
    BOMdewpoint15h = deltaDewPoint(filtered_data['dew_point_2m'][5], altitude)
    BOMdewpoint18h = deltaDewPoint(filtered_data['dew_point_2m'][6], altitude)
    BOMdewpoint21h = deltaDewPoint(filtered_data['dew_point_2m'][7], altitude)
    BOMdewpoint24h = deltaDewPoint(filtered_data['dew_point_2m'][8], altitude)

    # Adjust the enthalpy values based on the altitude change
    BOMenthalpy0h = deltaEnthalpy(filtered_data['enthalpy'][0], altitude)
    BOMenthalpy3h = deltaEnthalpy(filtered_data['enthalpy'][1], altitude)
    BOMenthalpy6h = deltaEnthalpy(filtered_data['enthalpy'][2], altitude)
    BOMenthalpy9h = deltaEnthalpy(filtered_data['enthalpy'][3], altitude)
    BOMenthalpy12h = deltaEnthalpy(filtered_data['enthalpy'][4], altitude)
    BOMenthalpy15h = deltaEnthalpy(filtered_data['enthalpy'][5], altitude)
    BOMenthalpy18h = deltaEnthalpy(filtered_data['enthalpy'][6], altitude)
    BOMenthalpy21h = deltaEnthalpy(filtered_data['enthalpy'][7], altitude)
    BOMenthalpy24h = deltaEnthalpy(filtered_data['enthalpy'][8], altitude)

    # Find the maximum values
    BOMmax_temp = max(filtered_data['temperature_2m'])
    BOMmax_humidity = max(filtered_data['relative_humidity_2m'])
    BOMmax_dewpoint = max([
    BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h,
    BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h
    ])
    BOMmax_enthalpy = max([BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h, 
    BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h])

    # Calculate the average of each metric
    BOMminimum_temp = min(filtered_data['temperature_2m'])
    BOMminimum_humidity = min(filtered_data['relative_humidity_2m'])
    BOMminimum_dewpoint = min([
        BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h,
        BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h
    ])
    BOMminimum_enthalpy = min([
        BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h,
        BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h
    ])
        # runs this function to create an XML of the data
    writeWeatherDataToXML(BOMtemp0h, BOMtemp3h, BOMtemp6h, BOMtemp9h, BOMtemp12h, BOMtemp15h, BOMtemp18h, BOMtemp21h, BOMtemp24h,
    BOMhumidity0h, BOMhumidity3h, BOMhumidity6h, BOMhumidity9h, BOMhumidity12h, BOMhumidity15h, BOMhumidity18h, BOMhumidity21h, BOMhumidity24h,
    BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h, BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h,
    BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h, BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h,
    BOMmax_temp, BOMmax_humidity, BOMmax_dewpoint, BOMmax_enthalpy,
    BOMminimum_temp, BOMminimum_humidity, BOMminimum_dewpoint, BOMminimum_enthalpy)

# take data from weather fetch and write it to an xml structure
def writeWeatherDataToXML(BOMtemp0h, BOMtemp3h, BOMtemp6h, BOMtemp9h, BOMtemp12h, BOMtemp15h, BOMtemp18h, BOMtemp21h, BOMtemp24h,
    BOMhumidity0h, BOMhumidity3h, BOMhumidity6h, BOMhumidity9h, BOMhumidity12h, BOMhumidity15h, BOMhumidity18h, BOMhumidity21h, BOMhumidity24h,
    BOMdewpoint0h, BOMdewpoint3h, BOMdewpoint6h, BOMdewpoint9h, BOMdewpoint12h, BOMdewpoint15h, BOMdewpoint18h, BOMdewpoint21h, BOMdewpoint24h,
    BOMenthalpy0h, BOMenthalpy3h, BOMenthalpy6h, BOMenthalpy9h, BOMenthalpy12h, BOMenthalpy15h, BOMenthalpy18h, BOMenthalpy21h, BOMenthalpy24h,
    BOMmax_temp, BOMmax_humidity, BOMmax_dewpoint, BOMmax_enthalpy,
    BOMminimum_temp, BOMminimum_humidity, BOMminimum_dewpoint, BOMminimum_enthalpy):

    root = ET.Element("WeatherData")

    # Create temperature elements
    temperatures = ET.SubElement(root, "Temperatures")
    ET.SubElement(temperatures, "BOMtemp0h").text = str(BOMtemp0h)
    ET.SubElement(temperatures, "BOMtemp3h").text = str(BOMtemp3h)
    ET.SubElement(temperatures, "BOMtemp6h").text = str(BOMtemp6h)
    ET.SubElement(temperatures, "BOMtemp9h").text = str(BOMtemp9h)
    ET.SubElement(temperatures, "BOMtemp12h").text = str(BOMtemp12h)
    ET.SubElement(temperatures, "BOMtemp15h").text = str(BOMtemp15h)
    ET.SubElement(temperatures, "BOMtemp18h").text = str(BOMtemp18h)
    ET.SubElement(temperatures, "BOMtemp21h").text = str(BOMtemp21h)
    ET.SubElement(temperatures, "BOMtemp24h").text = str(BOMtemp24h)
    ET.SubElement(temperatures, "BOMmax_temp").text = str(BOMmax_temp)
    ET.SubElement(temperatures, "BOMminimum_temp").text = str(BOMminimum_temp)

    # Create humidity elements
    humidities = ET.SubElement(root, "Humidities")
    ET.SubElement(humidities, "BOMhumidity0h").text = str(BOMhumidity0h)
    ET.SubElement(humidities, "BOMhumidity3h").text = str(BOMhumidity3h)
    ET.SubElement(humidities, "BOMhumidity6h").text = str(BOMhumidity6h)
    ET.SubElement(humidities, "BOMhumidity9h").text = str(BOMhumidity9h)
    ET.SubElement(humidities, "BOMhumidity12h").text = str(BOMhumidity12h)
    ET.SubElement(humidities, "BOMhumidity15h").text = str(BOMhumidity15h)
    ET.SubElement(humidities, "BOMhumidity18h").text = str(BOMhumidity18h)
    ET.SubElement(humidities, "BOMhumidity21h").text = str(BOMhumidity21h)
    ET.SubElement(humidities, "BOMhumidity24h").text = str(BOMhumidity24h)
    ET.SubElement(humidities, "BOMmax_humidity").text = str(BOMmax_humidity)
    ET.SubElement(humidities, "BOMminimum_humidity").text = str(BOMminimum_humidity)

    # Create dew point elements
    dewpoints = ET.SubElement(root, "DewPoints")
    ET.SubElement(dewpoints, "BOMdewpoint0h").text = str(BOMdewpoint0h)
    ET.SubElement(dewpoints, "BOMdewpoint3h").text = str(BOMdewpoint3h)
    ET.SubElement(dewpoints, "BOMdewpoint6h").text = str(BOMdewpoint6h)
    ET.SubElement(dewpoints, "BOMdewpoint9h").text = str(BOMdewpoint9h)
    ET.SubElement(dewpoints, "BOMdewpoint12h").text = str(BOMdewpoint12h)
    ET.SubElement(dewpoints, "BOMdewpoint15h").text = str(BOMdewpoint15h)
    ET.SubElement(dewpoints, "BOMdewpoint18h").text = str(BOMdewpoint18h)
    ET.SubElement(dewpoints, "BOMdewpoint21h").text = str(BOMdewpoint21h)
    ET.SubElement(dewpoints, "BOMdewpoint24h").text = str(BOMdewpoint24h)
    ET.SubElement(dewpoints, "BOMmax_dewpoint").text = str(BOMmax_dewpoint)
    ET.SubElement(dewpoints, "BOMminimum_dewpoint").text = str(BOMminimum_dewpoint)

    # Create enthalpy elements
    enthalpies = ET.SubElement(root, "Enthalpies")
    ET.SubElement(enthalpies, "BOMenthalpy0h").text = str(BOMenthalpy0h)
    ET.SubElement(enthalpies, "BOMenthalpy3h").text = str(BOMenthalpy3h)
    ET.SubElement(enthalpies, "BOMenthalpy6h").text = str(BOMenthalpy6h)
    ET.SubElement(enthalpies, "BOMenthalpy9h").text = str(BOMenthalpy9h)
    ET.SubElement(enthalpies, "BOMenthalpy12h").text = str(BOMenthalpy12h)
    ET.SubElement(enthalpies, "BOMenthalpy15h").text = str(BOMenthalpy15h)
    ET.SubElement(enthalpies, "BOMenthalpy18h").text = str(BOMenthalpy18h)
    ET.SubElement(enthalpies, "BOMenthalpy21h").text = str(BOMenthalpy21h)
    ET.SubElement(enthalpies, "BOMenthalpy24h").text = str(BOMenthalpy24h)
    ET.SubElement(enthalpies, "BOMmax_enthalpy").text = str(BOMmax_enthalpy)
    ET.SubElement(enthalpies, "BOMminimum_enthalpy").text = str(BOMminimum_enthalpy)

    # Write to XML file with pretty print
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open("C:\\BACnetWeatherFetchData\OpenMeteo_weather_data.xml", "w") as f:
        f.write(xml_str)

    # runs open meteo requests functionality from input configuration
def runOpenMeteo():
    # Read the XML settings to get latitude and longitude
    readXMLSettings()
    # Fetch the weather data using the extracted latitude and longitude
    fetchOpenMeteoWeather(lat, lon)


# loop to constantly fetch and update weather information in the background
def fetchWeatherPeriodically():
    readXMLSettings()
    dailyCallWait = setDailyRequests(num_requests)
    while True:
        readXMLSettings()
        fetchWeatherData(lat, lon, api_token)
        runOpenMeteo()
        writeXMLWeatherData()
        time.sleep(dailyCallWait)


# Create a thread for periodic weather fetching
weather_thread = threading.Thread(target=fetchWeatherPeriodically, daemon=True)
weather_thread.start()


# # Create the virtual BACnet device below, it will include a number of different analog_values for weather metrics
def start_device(device_Id, port_Id): #IP_address
    # will run license verification before window initialisation
    if not verifyKey():
        sys.exit()
        
    virtualDevice = BAC0.lite(deviceId=device_Id, port=port_Id, ip=IP_address)
    time.sleep(1)

    # Analog Value creation for BACnet device
    # Instance numbers 1-99 are allocated to OpenWeatherMap API
    # Instance numbers 100-199 are allocated to Open Meteo API 
    # Continue this naming convention for sources added later ... 200-299 and so on.

    # Open weather analog points 1-99
    _new_objects = analog_value(
        instance=1,
        name="Open Weather Map Current Temperature",
        description="Current Temperature in degC", 
        presentValue=current_temperature,
        properties={"units": "degreesCelsius"},
    )
    _new_objects = analog_value(
        instance=2,
        name="Open Weather Map Current Humidity",
        description="Current Humidity in percentage",
        presentValue=humidity,
        properties={"units": "percent"},
    )
    _new_objects = analog_value(
        instance=3,
        name="Open Weather Map Current Dew Point",
        description="Current Dew Point Temperature",
        presentValue=current_dew_point,
        properties={"units": "degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=4,
        name="Open Weather Map Current Enthalpy",
        description="CUrrent Specific Enthalpy",
        presentValue=current_enthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=5,
        name="Open Weather Map Forecast Temperature +3hr",
        description="Predicted Temperature in 3hrs",
        presentValue=hourly_temperatures[1],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=6,
        name="Open Weather Map Forecast Temperature +6hr",
        description="Predicted Temperature in 6hrs",
        presentValue=hourly_temperatures[2],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=7,
        name="Open Weather Map Forecast Temperature +9hr",
        description="Predicted Temperature in 9hrs",
        presentValue=hourly_temperatures[3],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=8,
        name="Open Weather Map Forecast Temperature +12hr",
        description="Predicted Temperature in 12hrs",
        presentValue=hourly_temperatures[4],
        properties={"units":"degreesCelsius"}
    )   
    _new_objects = analog_value(
        instance=9,
        name="Open Weather Map Forecast Temperature +15hr",
        description="Predicted Temperature in 15hrs",
        presentValue=hourly_temperatures[5],
        properties={"units":"degreesCelsius"}
    ) 
    _new_objects = analog_value(
        instance=10,
        name="Open Weather Map Forecast Temperature +18hr",
        description="Predicted Temperature in 18hrs",
        presentValue=hourly_temperatures[6],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=11,
        name="Open Weather Map Forecast Temperature +21hr",
        description="Predicted Temperature in 21hrs",
        presentValue=hourly_temperatures[7],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=12,
        name="Open Weather Map Forecast Temperature +24hr",
        description="Predicted Temperature in 24hrs",
        presentValue=hourly_temperatures[8],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=13,
        name="Open Weather Map Forecast Humidity +3hr",
        description="Predicted Humidity in 3hrs",
        presentValue=hourly_humidity[1],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=14,
        name="Open Weather Map Forecast Humidity +6hr",
        description="Predicted Humidity in 6hrs",
        presentValue=hourly_humidity[2],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=15,
        name="Open Weather Map Forecast Humidity +9hr",
        description="Predicted Humidity in 9hrs",
        presentValue=hourly_humidity[3],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=16,
        name="Open Weather Map Forecast Humidity +12hr",
        description="Predicted Humidity in 12hrs",
        presentValue=hourly_humidity[4],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=17,
        name="Open Weather Map Forecast Humidity +15hr",
        description="Predicted Temperature in 15hrs",
        presentValue=hourly_humidity[5],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=18,
        name="Open Weather Map Forecast Humidity +18hr",
        description="Predicted Humidity in 18hrs",
        presentValue=hourly_humidity[6],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=19,
        name="Open Weather Map Forecast Humidity +21hr",
        description="Predicted Humidity in 21hrs",
        presentValue=hourly_humidity[7],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=20,
        name="Open Weather Map Forecast Humidity +24hr",
        description="Predicted Humidity in 24hrs",
        presentValue=hourly_humidity[8],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=21,
        name="Open Weather Map Forecast Enthalpy +3hr",
        description="Predicted Enthalpy in 3hrs",
        presentValue=enthalpy3hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=22,
        name="Open Weather Map Forecast Enthalpy +6hr",
        description="Predicted Enthalpy in 6hrs",
        presentValue=enthalpy6hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=23,
        name="Open Weather Map Forecast Enthalpy +9hr",
        description="Predicted Enthalpy in 9hrs",
        presentValue=enthalpy9hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=24,
        name="Open Weather Map Forecast Enthalpy +12hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=enthalpy12hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=25,
        name="Open Weather Map Forecast Enthalpy +15hr",
        description="Predicted Enthalpy in 15hrs",
        presentValue=enthalpy15hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=26,
        name="Open Weather Map Forecast Enthalpy +18hr",
        description="Predicted Enthalpy in 18hrs",
        presentValue=enthalpy18hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=27,
        name="Open Weather Map Forecast Enthalpy +21hr",
        description="Predicted Enthalpy in 21hrs",
        presentValue=enthalpy21hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=28,
        name="Open Weather Map Forecast Enthalpy +24hr",
        description="Predicted Enthalpy in 24hrs",
        presentValue=enthalpy24hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=29,
        name="Open Weather Map Forecast Dew Point +3hr",
        description="Predicted Enthalpy in 3hrs",
        presentValue=dew_point3hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=30,
        name="Open Weather Map Forecast Dew Point +6hr",
        description="Predicted Enthalpy in 6hrs",
        presentValue=dew_point6hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=31,
        name="Open Weather Map Forecast Dew Point +9hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=dew_point12hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=32,
        name="Open Weather Map Forecast Dew Point +12hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=dew_point12hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=33,
        name="Open Weather Map Forecast Dew Point +15hr",
        description="Predicted Enthalpy in 15hrs",
        presentValue=dew_point15hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=34,
        name="Open Weather Map Forecast Dew Point +18hr",
        description="Predicted Enthalpy in 18hrs",
        presentValue=dew_point18hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=35,
        name="Open Weather Map Forecast Dew Point +21hr",
        description="Predicted Enthalpy in 21hrs",
        presentValue=dew_point21hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=36,
        name="Open Weather Map Forecast Dew Point +24hr",
        description="Predicted Enthalpy in 24hrs",
        presentValue=dew_point24hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=37,
        name="Open Weather Map Minimum Humidity 24H",
        description="Minimum Humidity in the next 24HR",
        presentValue=min_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=38,
        name="Open Weather Map Minimum Temperature 24H",
        description="Minimum Temperature in the next 24HR",
        presentValue=min_temperature,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=39,
        name="Open Weather Map Maximum Humidity 24H",
        description="Maximum Humidity in the next 24HR",
        presentValue=max_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=40,
        name="Open Weather Map Maximum Temperature 24H",
        description="Max Temperature in the next 24HR",
        presentValue=max_temperature,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=41,
        name="Open Weather Map Minimum Enthalpy 24H",
        description="Minimum Enthalpy in the next 24HR",
        presentValue=minEnthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=42,
        name="Open Weather Map Maximum Enthalpy 24H",
        description="Max Enthalpy in the next 24HR",
        presentValue=maximumEnthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=43,
        name="Open Weather Map Maximum Dew Point 24H",
        description="Max Dew Point in the next 24HR",
        presentValue=maximumDewPt,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=44,
        name="Open Weather Map Minimum Dew Point 24H",
        description="Min Dew Point in the next 24HR",
        presentValue=minDewpt,
        properties={"units":"degreesCelsius"}
    )

    # Open Meteo Analog Objects instances from 100-199

    _new_objects = analog_value(
        instance=100,
        name="Open Meteo Current Temperature",
        description="Current Temperature in degC",
        presentValue=BOMtemp0h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=101,
        name="Open Meteo Current Humidity",
        description="Current Humidity in %",
        presentValue=BOMhumidity0h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=102,
        name="Open Meteo Current Dew Point",
        description="Current Dew Point in degC",
        presentValue=BOMdewpoint0h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=103,
        name="Open Meteo Current Enthalpy",
        description="Current Enthalpy Kj/Kg",
        presentValue=BOMenthalpy0h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=104,
        name="Open Meteo Temperature Forecast +3h",
        description="Predicted Temperature in 3hrs",
        presentValue=BOMtemp3h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=105,
        name="Open Meteo Temperature Forecast +6h",
        description="Predicted Temperature in 6hrs",
        presentValue=BOMtemp6h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=106,
        name="Open Meteo Temperature Forecast +9h",
        description="Predicted Temperature in 9hrs",
        presentValue=BOMtemp9h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=107,
        name="Open Meteo Temperature Forecast +12h",
        description="Predicted Temperature in 12hrs",
        presentValue=BOMtemp12h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=108,
        name="Open Meteo Temperature Forecast +15h",
        description="Predicted Temperature in 15hrs",
        presentValue=BOMtemp15h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=109,
        name="Open Meteo Temperature Forecast +18h",
        description="Predicted Temperature in 18hrs",
        presentValue=BOMtemp18h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=110,
        name="Open Meteo Temperature Forecast +21h",
        description="Predicted Temperature in 21hrs",
        presentValue=BOMtemp21h,
        properties={"units":"degreesCelsius"} # 10.0.0.150
    )
    _new_objects = analog_value(
        instance=111,
        name="Open Meteo Temperature Forecast +24h",
        description="Predicted Temperature in 24hrs",
        presentValue=BOMtemp24h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=112,
        name="Open Meteo Humidity Forecast +3h",
        description="Predicted Humidity in 3hrs",
        presentValue=BOMhumidity3h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=113,
        name="Open Meteo Humidity Forecast +6h",
        description="Predicted Humidity in 6hrs",
        presentValue=BOMhumidity6h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=114,
        name="Open Meteo Humidity Forecast +9h",
        description="Predicted Humidity in 9hrs",
        presentValue=BOMhumidity9h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=115,
        name="Open Meteo Humidity Forecast +12h",
        description="Predicted Humidity in 12hrs",
        presentValue=BOMhumidity12h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=116,
        name="Open Meteo Humidity Forecast +15h",
        description="Predicted Humidity in 15hrs",
        presentValue=BOMhumidity15h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=117,
        name="Open Meteo Humidity Forecast +18h",
        description="Predicted Humidity in 18hrs",
        presentValue=BOMhumidity18h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=118,
        name="Open Meteo Humidity Forecast +21h",
        description="Predicted Humidity in 21hrs",
        presentValue=BOMhumidity21h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=119,
        name="Open Meteo Humidity Forecast +24h",
        description="Predicted Humidity in 24hrs",
        presentValue=BOMhumidity24h,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=120,
        name="Open Meteo Dew Point Forecast +3h",
        description="Predicted Dew Point in 3hrs",
        presentValue=BOMdewpoint3h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=121,
        name="Open Meteo Dew Point Forecast +6h",
        description="Predicted Dew Point in 6hrs",
        presentValue=BOMdewpoint6h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=122,
        name="Open Meteo Dew Point Forecast +9h",
        description="Predicted Dew Point in 9hrs",
        presentValue=BOMdewpoint9h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=123,
        name="Open Meteo Dew Point Forecast +12h",
        description="Predicted Dew Point in 12hrs",
        presentValue=BOMdewpoint12h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=124,
        name="Open Meteo Dew Point Forecast +15h",
        description="Predicted Dew Point in 15hrs",
        presentValue=BOMdewpoint15h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=125,
        name="Open Meteo Dew Point Forecast +18h",
        description="Predicted Dew Point in 18hrs",
        presentValue=BOMdewpoint18h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=126,
        name="Open Meteo Dew Point Forecast +21h",
        description="Predicted Dew Point in 21hrs",
        presentValue=BOMdewpoint21h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=127,
        name="Open Meteo Dew Point Forecast +24h",
        description="Predicted Dew Point in 24hrs",
        presentValue=BOMdewpoint24h,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=128,
        name="Open Meteo Enthalpy Forecast +3h",
        description="Predicted Enthalpy in 3hrs",
        presentValue=BOMenthalpy3h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=129,
        name="Open Meteo Enthalpy Forecast +6h",
        description="Predicted Enthalpy in 6hrs",
        presentValue=BOMenthalpy6h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=130,
        name="Open Meteo Enthalpy Forecast +9h",
        description="Predicted Enthalpy in 9hrs",
        presentValue=BOMenthalpy9h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=131,
        name="Open Meteo Enthalpy Forecast +12h",
        description="Predicted Enthalpy in 12hrs",
        presentValue=BOMenthalpy12h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=132,
        name="Open Meteo Enthalpy Forecast +15h",
        description="Predicted Enthalpy in 15hrs",
        presentValue=BOMenthalpy15h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=133,
        name="Open Meteo Enthalpy Forecast +18h",
        description="Predicted Enthalpy in 18hrs",
        presentValue=BOMenthalpy18h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=134,
        name="Open Meteo Enthalpy Forecast +21h",
        description="Predicted Enthalpy in 21hrs",
        presentValue=BOMenthalpy21h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=135,
        name="Open Meteo Enthalpy Forecast +24h",
        description="Predicted Enthalpy in 24hrs",
        presentValue=BOMenthalpy24h,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=136,
        name="Open Meteo Maximum Temperature 24H",
        description="Maximum Temperature for 24hrs",
        presentValue=BOMmax_temp,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=137,
        name="Open Meteo Maximum Humidity 24H",
        description="Maximum Humidity for 24hrs",
        presentValue=BOMmax_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=138,
        name="Open Meteo Maximum Dew Point 24H",
        description="Maximum Dew Point for 24hrs",
        presentValue=BOMmax_dewpoint,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=139,
        name="Open Meteo Maximum Enthalpy 24H",
        description="Maximum Enthalpy for 24hrs",
        presentValue=BOMmax_enthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=140,
        name="Open Meteo Minimum Temperature 24H",
        description="Minimum Enthalpy for 24hrs",
        presentValue=BOMminimum_temp,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=141,
        name="Open Meteo Minimum Humidity 24H",
        description="Minimum Humidity for 24hrs",
        presentValue=BOMminimum_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=142,
        name="Open Meteo Minimum Dew Point 24H",
        description="Minimum Dew Point for 24hrs",
        presentValue=BOMminimum_dewpoint,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=143,
        name="Open Meteo Minimum Enthalpy 24H",
        description="Minimum Enthalpy for 24hrs",
        presentValue=BOMminimum_enthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )

    _new_objects.add_objects_to_application(virtualDevice)
    return virtualDevice

try:
    # reading the xml weather data and updating the internal variables of the BACnet device
    readXMLSettings()
    bacnet_device = start_device(device_Id, port_Id) #IP_address
    # run an infinite loop that updates current weather values
    while True:
    # Code below will update the weather data stored inside the BACnet device every 31 minutes
    # update the current weather values for temp, humidity, dew pt and enthalpy
        bacnet_device["Open Weather Map Current Temperature"].presentValue = current_temperature
        bacnet_device["Open Weather Map Current Humidity"].presentValue = humidity
        bacnet_device["Open Weather Map Current Dew Point"].presentValue = current_dew_point
        bacnet_device["Open Weather Map Current Enthalpy"].presentValue = current_enthalpy
    # update the predicted temperature readings 
        bacnet_device["Open Weather Map Forecast Temperature +3hr"].presentValue=hourly_temperatures[1]
        bacnet_device["Open Weather Map Forecast Temperature +6hr"].presentValue=hourly_temperatures[2]
        bacnet_device["Open Weather Map Forecast Temperature +9hr"].presentValue=hourly_temperatures[3]
        bacnet_device["Open Weather Map Forecast Temperature +12hr"].presentValue=hourly_temperatures[4]
        bacnet_device["Open Weather Map Forecast Temperature +15hr"].presentValue=hourly_temperatures[5]
        bacnet_device["Open Weather Map Forecast Temperature +18hr"].presentValue=hourly_temperatures[6]
        bacnet_device["Open Weather Map Forecast Temperature +21hr"].presentValue=hourly_temperatures[7]
        bacnet_device["Open Weather Map Forecast Temperature +24hr"].presentValue=hourly_temperatures[8]
    # update the predicted humidity readings
        bacnet_device["Open Weather Map Forecast Humidity +3hr"].presentValue=hourly_humidity[1]
        bacnet_device["Open Weather Map Forecast Humidity +6hr"].presentValue=hourly_humidity[2]
        bacnet_device["Open Weather Map Forecast Humidity +9hr"].presentValue=hourly_humidity[3]
        bacnet_device["Open Weather Map Forecast Humidity +12hr"].presentValue=hourly_humidity[4]
        bacnet_device["Open Weather Map Forecast Humidity +15hr"].presentValue=hourly_humidity[5]
        bacnet_device["Open Weather Map Forecast Humidity +18hr"].presentValue=hourly_humidity[6]
        bacnet_device["Open Weather Map Forecast Humidity +21hr"].presentValue=hourly_humidity[7]
        bacnet_device["Open Weather Map Forecast Humidity +24hr"].presentValue=hourly_humidity[8]
    # update the enthalty prediction readings
        bacnet_device["Open Weather Map Forecast Enthalpy +3hr"].presentValue=enthalpy3hr
        bacnet_device["Open Weather Map Forecast Enthalpy +6hr"].presentValue=enthalpy6hr
        bacnet_device["Open Weather Map Forecast Enthalpy +9hr"].presentValue=enthalpy9hr
        bacnet_device["Open Weather Map Forecast Enthalpy +12hr"].presentValue=enthalpy12hr
        bacnet_device["Open Weather Map Forecast Enthalpy +15hr"].presentValue=enthalpy15hr
        bacnet_device["Open Weather Map Forecast Enthalpy +18hr"].presentValue=enthalpy18hr
        bacnet_device["Open Weather Map Forecast Enthalpy +21hr"].presentValue=enthalpy21hr
        bacnet_device["Open Weather Map Forecast Enthalpy +24hr"].presentValue=enthalpy24hr
    # update the dew point readings
        bacnet_device["Open Weather Map Forecast Dew Point +3hr"].presentValue=dew_point3hr
        bacnet_device["Open Weather Map Forecast Dew Point +6hr"].presentValue=dew_point6hr
        bacnet_device["Open Weather Map Forecast Dew Point +9hr"].presentValue=dew_point9hr
        bacnet_device["Open Weather Map Forecast Dew Point +12hr"].presentValue=dew_point12hr
        bacnet_device["Open Weather Map Forecast Dew Point +15hr"].presentValue=dew_point15hr
        bacnet_device["Open Weather Map Forecast Dew Point +18hr"].presentValue=dew_point18hr
        bacnet_device["Open Weather Map Forecast Dew Point +21hr"].presentValue=dew_point21hr
        bacnet_device["Open Weather Map Forecast Dew Point +24hr"].presentValue=dew_point24hr
    # update the avg and max humidity and temp readings
        bacnet_device["Open Weather Map Minimum Humidity 24H"].presentValue=min_humidity
        bacnet_device["Open Weather Map Minimum Temperature 24H"].presentValue=min_temperature
        bacnet_device["Open Weather Map Minimum Enthalpy 24H"].presentValue=minEnthalpy
        bacnet_device["Open Weather Map Minimum Dew Point 24H"].presentValue=minDewpt
        bacnet_device["Open Weather Map Maximum Temperature 24H"].presentValue=max_temperature
        bacnet_device["Open Weather Map Maximum Humidity 24H"].presentValue=max_humidity
        bacnet_device["Open Weather Map Maximum Enthalpy 24H"].presentValue=maximumEnthalpy
        bacnet_device["Open Weather Map Maximum Dew Point 24H"].presentValue=maximumDewPt

        ################################################
        # start of Open Meteo (BOM) data updating points
        ################################################

        bacnet_device["Open Meteo Current Temperature"].presentValue = BOMtemp0h
        bacnet_device["Open Meteo Current Humidity"].presentValue = BOMhumidity0h
        bacnet_device["Open Meteo Current Dew Point"].presentValue = BOMdewpoint0h
        bacnet_device["Open Meteo Current Enthalpy"].presentValue = BOMenthalpy0h
    # update the predicted temperature readings 
        bacnet_device["Open Meteo Temperature Forecast +3h"].presentValue=BOMtemp3h
        bacnet_device["Open Meteo Temperature Forecast +6h"].presentValue=BOMtemp6h
        bacnet_device["Open Meteo Temperature Forecast +9h"].presentValue=BOMtemp9h
        bacnet_device["Open Meteo Temperature Forecast +12h"].presentValue=BOMtemp12h
        bacnet_device["Open Meteo Temperature Forecast +15h"].presentValue=BOMtemp15h
        bacnet_device["Open Meteo Temperature Forecast +18h"].presentValue=BOMtemp18h
        bacnet_device["Open Meteo Temperature Forecast +21h"].presentValue=BOMtemp21h
        bacnet_device["Open Meteo Temperature Forecast +24h"].presentValue=BOMtemp24h
    # update the predicted humidity readings
        bacnet_device["Open Meteo Humidity Forecast +3h"].presentValue=BOMhumidity3h
        bacnet_device["Open Meteo Humidity Forecast +6h"].presentValue=BOMhumidity6h
        bacnet_device["Open Meteo Humidity Forecast +9h"].presentValue=BOMhumidity9h
        bacnet_device["Open Meteo Humidity Forecast +12h"].presentValue=BOMhumidity12h
        bacnet_device["Open Meteo Humidity Forecast +15h"].presentValue=BOMhumidity15h
        bacnet_device["Open Meteo Humidity Forecast +18h"].presentValue=BOMhumidity18h
        bacnet_device["Open Meteo Humidity Forecast +21h"].presentValue=BOMhumidity21h
        bacnet_device["Open Meteo Humidity Forecast +24h"].presentValue=BOMhumidity24h
    # update the enthalty prediction readings
        bacnet_device["Open Meteo Enthalpy Forecast +3h"].presentValue=BOMenthalpy3h
        bacnet_device["Open Meteo Enthalpy Forecast +6h"].presentValue=BOMenthalpy6h
        bacnet_device["Open Meteo Enthalpy Forecast +9h"].presentValue=BOMenthalpy9h
        bacnet_device["Open Meteo Enthalpy Forecast +12h"].presentValue=BOMenthalpy12h
        bacnet_device["Open Meteo Enthalpy Forecast +15h"].presentValue=BOMenthalpy15h
        bacnet_device["Open Meteo Enthalpy Forecast +18h"].presentValue=BOMenthalpy18h
        bacnet_device["Open Meteo Enthalpy Forecast +21h"].presentValue=BOMenthalpy21h
        bacnet_device["Open Meteo Enthalpy Forecast +24h"].presentValue=BOMenthalpy24h
    # update the dew point readings
        bacnet_device["Open Meteo Dew Point Forecast +3h"].presentValue=BOMdewpoint3h
        bacnet_device["Open Meteo Dew Point Forecast +6h"].presentValue=BOMdewpoint6h
        bacnet_device["Open Meteo Dew Point Forecast +9h"].presentValue=BOMdewpoint9h
        bacnet_device["Open Meteo Dew Point Forecast +12h"].presentValue=BOMdewpoint12h
        bacnet_device["Open Meteo Dew Point Forecast +15h"].presentValue=BOMdewpoint15h
        bacnet_device["Open Meteo Dew Point Forecast +18h"].presentValue=BOMdewpoint18h
        bacnet_device["Open Meteo Dew Point Forecast +21h"].presentValue=BOMdewpoint21h
        bacnet_device["Open Meteo Dew Point Forecast +24h"].presentValue=BOMdewpoint24h
    # update the avg and max humidity and temp readings
        bacnet_device["Open Meteo Maximum Temperature 24H"].presentValue=BOMmax_temp
        bacnet_device["Open Meteo Maximum Humidity 24H"].presentValue=BOMmax_humidity
        bacnet_device["Open Meteo Maximum Enthalpy 24H"].presentValue=BOMmax_enthalpy
        bacnet_device["Open Meteo Maximum Dew Point 24H"].presentValue=BOMmax_dewpoint
        bacnet_device["Open Meteo Minimum Temperature 24H"].presentValue=BOMminimum_temp
        bacnet_device["Open Meteo Minimum Humidity 24H"].presentValue=BOMminimum_humidity
        bacnet_device["Open Meteo Minimum Enthalpy 24H"].presentValue=BOMminimum_enthalpy
        bacnet_device["Open Meteo Minimum Dew Point 24H"].presentValue=BOMminimum_dewpoint

        time.sleep(10) # loop_sleep
except Exception as e:
        print(f"Error: {e}")
