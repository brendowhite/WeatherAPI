import math
import requests
from BAC0.core.devices.local.models import (
    analog_value
)
import BAC0
import time
import datetime

current_time = datetime.datetime.now()

# Global variables for weather data
current_temperature = 0
humidity = 0
current_dew_point = 0
current_enthalpy = 0
hourly_temperatures = []
hourly_humidity = []
max_temperature = 0
average_temperature = 0
max_humidity = 0
average_humidity = 0
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

lat = None
lon = None
api_token = None
# altitude = None
device_Id = None
port_Id = None


# '0d5d2cfed28b5145804a9901a16c2b40'
# latitude = -33.785791
# long = 151.121482

def setAltitude(inputAlt):
    global altitude
    altitude = float(inputAlt)
    return altitude

# Function to calculate dew point
def dewPointCalc(temp, humidity, altitude):
    a = 17.27
    b = 237.7
    deltaTemp = temp - (6.5 / 1000) * altitude # temperature typically decreases at a rate of 6.5 deg C for every 1000m (standard lapse rate)
    alpha = ((a * deltaTemp) / (b + deltaTemp)) + math.log(humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

# Function to calculate enthalpy
def enthalpyCalc(temp, humidity, altitude):
    dew_point = dewPointCalc(temp, humidity, altitude)
    deltaTemp = temp - (6.5 / 1000) * altitude # refer to comment above and (standard lapse rate)
    h = 1.006 * deltaTemp
    latent_heat = 2501
    specific_humidity = 0.622 * (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)) / (1013.25 - (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)))
    enthalpy = h + (latent_heat * specific_humidity)
    return enthalpy

def fetchWeatherData(lat, lon, api_token):
    # define global variables to be used in updating analog_values on BACnet device
    global current_temperature, humidity, current_dew_point, current_enthalpy, hourly_temperatures, hourly_humidity, max_temperature, average_temperature, average_humidity, max_humidity
    global dew_point3hr, dew_point6hr, dew_point9hr, dew_point12hr, dew_point15hr, dew_point18hr, dew_point21hr, dew_point24hr
    global enthalpy3hr, enthalpy6hr, enthalpy9hr, enthalpy12hr, enthalpy15hr, enthalpy18hr, enthalpy21hr, enthalpy24hr
 
    # Open Weather Map API with 3 arguments, latitude, longitude and weather api token. Metric by default
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_token}'
    response = requests.get(url)
    data = response.json()

    try:
        # key data pulled from the API 
        hourly_data = data['list'][0:9]
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        hourly_humidity = [hour['main']['humidity'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = data['list'][0]['main']['temp']
        humidity = data['list'][0]['main']['humidity']
        average_humidity = sum(hourly_humidity) / len(hourly_humidity)
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

        print(f"Current Temperature: {current_temperature} °C")
        print(f"Current Humidity: {humidity} %")
        print(f"Current Dew Point: {current_dew_point} °C")
        print(f"Current Enthalpy: {current_enthalpy} kJ/kg")

    except KeyError:
        print("Error fetching initial weather data")

def extractWeatherData():
    return{"temp3hr":hourly_temperatures[1],
           "temp6hr":hourly_temperatures[2],
           "temp9hr":hourly_temperatures[3],
           "temp12hr":hourly_temperatures[4],
           "temp15hr":hourly_temperatures[5],
           "temp18hr":hourly_temperatures[6],
           "temp21hr":hourly_temperatures[7],
           "temp24hr":hourly_temperatures[8],
           "current_temperature":current_temperature,
           "hum3hr":hourly_humidity[1],
           "hum6hr":hourly_humidity[2],
           "hum9hr":hourly_humidity[3],
           "hum12hr":hourly_humidity[4],
           "hum15hr":hourly_humidity[5],
           "hum18hr":hourly_humidity[6],
           "hum21hr":hourly_humidity[7],
           "hum24hr":hourly_humidity[8],
           "max_temperature":max_temperature,
           "max_humidity":max_humidity,
           "average_humidity":average_humidity,
           "average_temperature":average_temperature,
           "humidity":humidity,
           "current_dew_point":current_dew_point,
           "dew_point3hr":dew_point3hr,
           "dew_point6hr":dew_point6hr,
           "dew_point9hr":dew_point9hr,
           "dew_point12hr":dew_point12hr,
           "dew_point15hr":dew_point15hr,
           "dew_point18hr":dew_point18hr,
           "dew_point21hr":dew_point21hr,
           "dew_point24hr":dew_point24hr,
           "current_enthalpy":current_enthalpy,
           "enthalpy3hr":enthalpy3hr,
           "enthalpy6hr":enthalpy6hr,
           "enthalpy9hr":enthalpy9hr,
           "enthalpy12hr":enthalpy12hr,
           "enthalpy15hr":enthalpy15hr,
           "enthalpy18hr":enthalpy18hr,
           "enthalpy21hr":enthalpy21hr,
           "enthalpy24hr":enthalpy24hr}




# # Function to fetch weather data periodically
def fetchWeatherPeriodically(lat, lon, api_token):
    while True:
        print("Fetching weather data...")
        fetchWeatherData(lat, lon,api_token)
        print("Weather data fetched.")
        time.sleep(30*60)  # sleep for 30 minutes



# # Create the virtual BACnet device below, it will include a number of different analog_values for weather metrics
def start_device(device_Id, port_Id):
    virtualDevice = BAC0.lite(deviceId=device_Id, port=port_Id)
    time.sleep(1)

    # Analog Value creation for BACnet device. This will 
    _new_objects = analog_value(
        instance=1,
        name="Current Temperature",
        description="Current Temperature in degC", 
        presentValue=current_temperature,
        properties={"units": "degreesCelsius"},
    )
    _new_objects = analog_value(
        instance=2,
        name="Current Humidity",
        description="Current Humidity in percentage",
        presentValue=humidity,
        properties={"units": "percent"},
    )
    _new_objects = analog_value(
        instance=3,
        name="Dew Point",
        description="Dew Point Temperature",
        presentValue=current_dew_point,
        properties={"units": "degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=4,
        name="Enthalpy",
        description="Specific Enthalpy",
        presentValue=current_enthalpy,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=5,
        name="Predicted Temperature +3hr",
        description="Predicted Temperature in 3hrs",
        presentValue=hourly_temperatures[1],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=6,
        name="Predicted Temperature +6hr",
        description="Predicted Temperature in 6hrs",
        presentValue=hourly_temperatures[2],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=7,
        name="Predicted Temperature +9hr",
        description="Predicted Temperature in 9hrs",
        presentValue=hourly_temperatures[3],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=8,
        name="Predicted Temperature +12hr",
        description="Predicted Temperature in 12hrs",
        presentValue=hourly_temperatures[4],
        properties={"units":"degreesCelsius"}
    )   
    _new_objects = analog_value(
        instance=9,
        name="Predicted Temperature +15hr",
        description="Predicted Temperature in 15hrs",
        presentValue=hourly_temperatures[5],
        properties={"units":"degreesCelsius"}
    ) 
    _new_objects = analog_value(
        instance=10,
        name="Predicted Temperature +18hr",
        description="Predicted Temperature in 18hrs",
        presentValue=hourly_temperatures[6],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=11,
        name="Predicted Temperature +21hr",
        description="Predicted Temperature in 21hrs",
        presentValue=hourly_temperatures[7],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=12,
        name="Predicted Temperature +24hr",
        description="Predicted Temperature in 24hrs",
        presentValue=hourly_temperatures[8],
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=13,
        name="Predicted Humidity +3hr",
        description="Predicted Humidity in 3hrs",
        presentValue=hourly_humidity[1],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=14,
        name="Predicted Humidity +6hr",
        description="Predicted Humidity in 6hrs",
        presentValue=hourly_humidity[2],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=15,
        name="Predicted Humidity +9hr",
        description="Predicted Humidity in 9hrs",
        presentValue=hourly_humidity[3],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=16,
        name="Predicted Humidity +12hr",
        description="Predicted Humidity in 12hrs",
        presentValue=hourly_humidity[4],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=17,
        name="Predicted Humidity +15hr",
        description="Predicted Temperature in 15hrs",
        presentValue=hourly_humidity[5],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=18,
        name="Predicted Humidity +18hr",
        description="Predicted Humidity in 18hrs",
        presentValue=hourly_humidity[6],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=19,
        name="Predicted Humidity +21hr",
        description="Predicted Humidity in 21hrs",
        presentValue=hourly_humidity[7],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=20,
        name="Predicted Humidity +24hr",
        description="Predicted Humidity in 24hrs",
        presentValue=hourly_humidity[8],
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=21,
        name="Predicted Enthalpy +3hr",
        description="Predicted Enthalpy in 3hrs",
        presentValue=enthalpy3hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=22,
        name="Predicted Enthalpy +6hr",
        description="Predicted Enthalpy in 6hrs",
        presentValue=enthalpy6hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=23,
        name="Predicted Enthalpy +9hr",
        description="Predicted Enthalpy in 9hrs",
        presentValue=enthalpy9hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=24,
        name="Predicted Enthalpy +12hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=enthalpy12hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=25,
        name="Predicted Enthalpy +15hr",
        description="Predicted Enthalpy in 15hrs",
        presentValue=enthalpy15hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=26,
        name="Predicted Enthalpy +18hr",
        description="Predicted Enthalpy in 18hrs",
        presentValue=enthalpy18hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=27,
        name="Predicted Enthalpy +21hr",
        description="Predicted Enthalpy in 21hrs",
        presentValue=enthalpy21hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=28,
        name="Predicted Enthalpy +24hr",
        description="Predicted Enthalpy in 24hrs",
        presentValue=enthalpy24hr,
        properties={"units":"kilojoulesPerKilogram"}
    )
    _new_objects = analog_value(
        instance=29,
        name="Predicted Dew Point +3hr",
        description="Predicted Enthalpy in 3hrs",
        presentValue=dew_point3hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=30,
        name="Predicted Dew Point +6hr",
        description="Predicted Enthalpy in 6hrs",
        presentValue=dew_point6hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=31,
        name="Predicted Dew Point +9hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=dew_point12hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=32,
        name="Predicted Dew Point +12hr",
        description="Predicted Enthalpy in 12hrs",
        presentValue=dew_point12hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=33,
        name="Predicted Dew Point +15hr",
        description="Predicted Enthalpy in 15hrs",
        presentValue=dew_point15hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=34,
        name="Predicted Dew Point +18hr",
        description="Predicted Enthalpy in 18hrs",
        presentValue=dew_point18hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=35,
        name="Predicted Dew Point +21hr",
        description="Predicted Enthalpy in 21hrs",
        presentValue=dew_point21hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=36,
        name="Predicted Dew Point +24hr",
        description="Predicted Enthalpy in 24hrs",
        presentValue=dew_point24hr,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=37,
        name="Average Humidity 24H",
        description="Average Humidity in the next 24HR",
        presentValue=average_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=38,
        name="Average Temperature 24H",
        description="Average Temperature in the next 24HR",
        presentValue=average_temperature,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=39,
        name="Maximum Humidity 24H",
        description="Maximum Humidity in the next 24HR",
        presentValue=max_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=40,
        name="Maximum Temperature 24H",
        description="Max Temperature in the next 24HR",
        presentValue=max_temperature,
        properties={"units":"degreesCelsius"}
    )


# up to here

    _new_objects.add_objects_to_application(virtualDevice)
    return virtualDevice



def updateBACnetValues(device_Id, port_Id):
    try:
        bacnet_device = start_device(device_Id, port_Id)
    # run an infinite loop that updates current weather values
        while True:

        # Code below will update the weather data stored inside the BACnet device every 31 minutes
    # update the current weather values for temp, humidity, dew pt and enthalpy

            bacnet_device["Current Temperature"].presentValue = current_temperature
            bacnet_device["Current Humidity"].presentValue = humidity
            bacnet_device["Dew Point"].presentValue = current_dew_point
            bacnet_device["Enthalpy"].presentValue = current_enthalpy
    # update the predicted temperature readings 
            bacnet_device["Predicted Temperature +3hr"].presentValue=hourly_temperatures[1]
            bacnet_device["Predicted Temperature +6hr"].presentValue=hourly_temperatures[2]
            bacnet_device["Predicted Temperature +9hr"].presentValue=hourly_temperatures[3]
            bacnet_device["Predicted Temperature +12hr"].presentValue=hourly_temperatures[4]
            bacnet_device["Predicted Temperature +15hr"].presentValue=hourly_temperatures[5]
            bacnet_device["Predicted Temperature +18hr"].presentValue=hourly_temperatures[6]
            bacnet_device["Predicted Temperature +21hr"].presentValue=hourly_temperatures[7]
            bacnet_device["Predicted Temperature +24hr"].presentValue=hourly_temperatures[8]
    # update the predicted humidity readings
            bacnet_device["Predicted Humidity +3hr"].presentValue=hourly_humidity[1]
            bacnet_device["Predicted Humidity +6hr"].presentValue=hourly_humidity[2]
            bacnet_device["Predicted Humidity +9hr"].presentValue=hourly_humidity[3]
            bacnet_device["Predicted Humidity +12hr"].presentValue=hourly_humidity[4]
            bacnet_device["Predicted Humidity +15hr"].presentValue=hourly_humidity[5]
            bacnet_device["Predicted Humidity +18hr"].presentValue=hourly_humidity[6]
            bacnet_device["Predicted Humidity +21hr"].presentValue=hourly_humidity[7]
            bacnet_device["Predicted Humidity +24hr"].presentValue=hourly_humidity[8]
    # update the enthalty prediction readings
            bacnet_device["Predicted Enthalpy +3hr"].presentValue=enthalpy3hr
            bacnet_device["Predicted Enthalpy +6hr"].presentValue=enthalpy6hr
            bacnet_device["Predicted Enthalpy +9hr"].presentValue=enthalpy9hr
            bacnet_device["Predicted Enthalpy +12hr"].presentValue=enthalpy12hr
            bacnet_device["Predicted Enthalpy +15hr"].presentValue=enthalpy15hr
            bacnet_device["Predicted Enthalpy +18hr"].presentValue=enthalpy18hr
            bacnet_device["Predicted Enthalpy +21hr"].presentValue=enthalpy21hr
            bacnet_device["Predicted Enthalpy +24hr"].presentValue=enthalpy24hr
    # update the dew point readings
            bacnet_device["Predicted Dew Point +3hr"].presentValue=dew_point3hr
            bacnet_device["Predicted Dew Point +6hr"].presentValue=dew_point6hr
            bacnet_device["Predicted Dew Point +9hr"].presentValue=dew_point9hr
            bacnet_device["Predicted Dew Point +12hr"].presentValue=dew_point12hr
            bacnet_device["Predicted Dew Point +15hr"].presentValue=dew_point15hr
            bacnet_device["Predicted Dew Point +18hr"].presentValue=dew_point18hr
            bacnet_device["Predicted Dew Point +21hr"].presentValue=dew_point21hr
            bacnet_device["Predicted Dew Point +24hr"].presentValue=dew_point24hr
    # update the avg and max humidity and temp readings
            bacnet_device["Average Humidity 24H"].presentValue=average_humidity
            bacnet_device["Average Temperature 24H"].presentValue=average_temperature
            bacnet_device["Maximum Temperature 24H"].presentValue=max_temperature
            bacnet_device["Maximum Humidity 24H"].presentValue=max_humidity


            time.sleep(31*60)  # Wait for 31 mins before starting a new device instance
    except Exception as e:
        print(f"Error: {e}")

