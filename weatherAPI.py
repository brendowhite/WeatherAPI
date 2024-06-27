import math
import requests
import BAC0
import time
from BAC0.core.devices.local.models import (
    analog_value
)
import datetime
import threading

WEATHER_API_KEY = '0d5d2cfed28b5145804a9901a16c2b40'
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
lat = None
lon = None


# Function to set latitude and longitude via user input
def set_location():
    global lat, lon
    try:
        lat = float(input("Enter latitude: "))
        lon = float(input("Enter longitude: "))
    except ValueError:
        print("Invalid input! Please enter valid numeric values for latitude and longitude.")

# Function to calculate dew point
def dewPointCalc(temp, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

# Function to calculate enthalpy
def enthalpyCalc(temp, humidity):
    dew_point = dewPointCalc(temp, humidity)
    h = 1.006 * temp
    latent_heat = 2501
    specific_humidity = 0.622 * (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)) / (1013.25 - (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)))
    enthalpy = h + (latent_heat * specific_humidity)
    return enthalpy

def fetchWeatherData(lat, lon):
    # define global variables to be used in updating analog_values on BACnet device
    global current_temperature, humidity, current_dew_point, current_enthalpy, hourly_temperatures, hourly_humidity, max_temperature, average_temperature, average_humidity, max_humidity
    global dew_point3hr, dew_point6hr, dew_point9hr, dew_point12hr, dew_point15hr, dew_point18hr, dew_point21hr, dew_point24hr, min_temperature, min_humidity
    global enthalpy3hr, enthalpy6hr, enthalpy9hr, enthalpy12hr, enthalpy15hr, enthalpy18hr, enthalpy21hr, enthalpy24hr
    if lat is None or lon is None:
        print("Latitude and/or longitude not set. Please set location first.")
        return
    

    # Open Weather Map API with 3 arguments, latitude, longitude and weather api token
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    try:
        # Data pulled from the API
        hourly_data = data['list'][0:9]
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        hourly_humidity = [hour['main']['humidity'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        min_temperature = min(hourly_temperatures)
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = data['list'][0]['main']['temp']
        humidity = data['list'][0]['main']['humidity']
        average_humidity = sum(hourly_humidity) / len(hourly_humidity)
        max_humidity = max(hourly_humidity)
        min_humidity = min(hourly_humidity)

        # Data calculated via custom functions
        current_dew_point = dewPointCalc(current_temperature, humidity)
        dew_point3hr = dewPointCalc(hourly_temperatures[1], hourly_humidity[1])
        dew_point6hr = dewPointCalc(hourly_temperatures[2], hourly_humidity[2])
        dew_point9hr = dewPointCalc(hourly_temperatures[3], hourly_humidity[3])
        dew_point12hr = dewPointCalc(hourly_temperatures[4], hourly_humidity[4])
        dew_point15hr = dewPointCalc(hourly_temperatures[5], hourly_humidity[5])
        dew_point18hr = dewPointCalc(hourly_temperatures[6], hourly_humidity[6])
        dew_point21hr = dewPointCalc(hourly_temperatures[7], hourly_humidity[7])
        dew_point24hr = dewPointCalc(hourly_temperatures[8], hourly_humidity[8])
        current_enthalpy = enthalpyCalc(current_temperature, humidity)
        enthalpy3hr = enthalpyCalc(hourly_temperatures[1], hourly_humidity[1])
        enthalpy6hr = enthalpyCalc(hourly_temperatures[2], hourly_humidity[2])
        enthalpy9hr = enthalpyCalc(hourly_temperatures[3], hourly_humidity[3])
        enthalpy12hr = enthalpyCalc(hourly_temperatures[4], hourly_humidity[4])
        enthalpy15hr = enthalpyCalc(hourly_temperatures[5], hourly_humidity[5])
        enthalpy18hr = enthalpyCalc(hourly_temperatures[6], hourly_humidity[6])
        enthalpy21hr = enthalpyCalc(hourly_temperatures[7], hourly_humidity[7])
        enthalpy24hr = enthalpyCalc(hourly_temperatures[8], hourly_humidity[8])

        print(f"Current Temperature: {current_temperature} °C")
        print(f"Current Humidity: {humidity} %")
        print(f"Current Dew Point: {current_dew_point} °C")
        print(f"Current Enthalpy: {current_enthalpy} kJ/kg")

    except KeyError:
        print("Error fetching initial weather data")


# # Function to fetch weather data periodically
def fetchWeatherPeriodically():
    while True:
        print("Fetching weather data...")
        fetchWeatherData(lat, lon)
        print("Weather data fetched.")
        time.sleep(30*60)  # For testing, sleep for 10 seconds instead of 3 hours

# Use latitude and longitude from user input to fetch the updated weather on the thread
set_location()
# Create a thread for periodic weather fetching
weather_thread = threading.Thread(target=fetchWeatherPeriodically)
weather_thread.start()

# # Create the virtual BACnet device below, it will include a number of different analog_values for weather metrics
def start_device():
    new_device = BAC0.lite(deviceId=11110)
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
        name="Minimum Humidity 24H",
        description="Min Humidity in the next 24HR",
        presentValue=min_humidity,
        properties={"units":"percent"}
    )
    _new_objects = analog_value(
        instance=41,
        name="Maximum Temperature 24H",
        description="Max Temperature in the next 24HR",
        presentValue=max_temperature,
        properties={"units":"degreesCelsius"}
    )
    _new_objects = analog_value(
        instance=42,
        name="Minimum Temperature 24H",
        description="Min Temperature in the next 24HR",
        presentValue=min_temperature,
        properties={"units":"degreesCelsius"}
    )

# up to here

    _new_objects.add_objects_to_application(new_device)
    return new_device

try:
    bacnet_device = start_device()
    while True:

        # Code below will update the weather data stored inside the BACnet device every 31 minutes
        
        print("we are here")
        bacnet_device["Current Temperature"].presentValue = current_temperature
        bacnet_device["Current Humidity"].presentValue = humidity
        bacnet_device["Dew Point"].presentValue = current_dew_point
        bacnet_device["Enthalpy"].presentValue = current_enthalpy

        bacnet_device["Predicted Temperature +3hr"].presentValue=hourly_temperatures[1]
        bacnet_device["Predicted Temperature +6hr"].presentValue=hourly_temperatures[2]
        bacnet_device["Predicted Temperature +9hr"].presentValue=hourly_temperatures[3]
        bacnet_device["Predicted Temperature +12hr"].presentValue=hourly_temperatures[4]
        bacnet_device["Predicted Temperature +15hr"].presentValue=hourly_temperatures[5]
        bacnet_device["Predicted Temperature +18hr"].presentValue=hourly_temperatures[6]
        bacnet_device["Predicted Temperature +21hr"].presentValue=hourly_temperatures[7]
        bacnet_device["Predicted Temperature +24hr"].presentValue=hourly_temperatures[8]

        bacnet_device["Predicted Humidity +3hr"].presentValue=hourly_humidity[1]
        bacnet_device["Predicted Humidity +6hr"].presentValue=hourly_humidity[2]
        bacnet_device["Predicted Humidity +9hr"].presentValue=hourly_humidity[3]
        bacnet_device["Predicted Humidity +12hr"].presentValue=hourly_humidity[4]
        bacnet_device["Predicted Humidity +15hr"].presentValue=hourly_humidity[5]
        bacnet_device["Predicted Humidity +18hr"].presentValue=hourly_humidity[6]
        bacnet_device["Predicted Humidity +21hr"].presentValue=hourly_humidity[7]
        bacnet_device["Predicted Humidity +24hr"].presentValue=hourly_humidity[8]

        bacnet_device["Predicted Enthalpy +3hr"].presentValue=enthalpy3hr
        bacnet_device["Predicted Enthalpy +6hr"].presentValue=enthalpy6hr
        bacnet_device["Predicted Enthalpy +9hr"].presentValue=enthalpy9hr
        bacnet_device["Predicted Enthalpy +12hr"].presentValue=enthalpy12hr
        bacnet_device["Predicted Enthalpy +15hr"].presentValue=enthalpy15hr
        bacnet_device["Predicted Enthalpy +18hr"].presentValue=enthalpy18hr
        bacnet_device["Predicted Enthalpy +21hr"].presentValue=enthalpy21hr
        bacnet_device["Predicted Enthalpy +24hr"].presentValue=enthalpy24hr

        bacnet_device["Predicted Dew Point +3hr"].presentValue=dew_point3hr
        bacnet_device["Predicted Dew Point +6hr"].presentValue=dew_point6hr
        bacnet_device["Predicted Dew Point +9hr"].presentValue=dew_point9hr
        bacnet_device["Predicted Dew Point +12hr"].presentValue=dew_point12hr
        bacnet_device["Predicted Dew Point +15hr"].presentValue=dew_point15hr
        bacnet_device["Predicted Dew Point +18hr"].presentValue=dew_point18hr
        bacnet_device["Predicted Dew Point +21hr"].presentValue=dew_point21hr
        bacnet_device["Predicted Dew Point +24hr"].presentValue=dew_point24hr

        bacnet_device["Average Humidity 24H"].presentValue=average_humidity
        bacnet_device["Average Temperature 24H"].presentValue=average_temperature
        bacnet_device["Maximum Temperature 24H"].presentValue=max_temperature
        bacnet_device["Minimum Temperature 24H"].presentValue=min_temperature
        bacnet_device["Maximum Humidity 24H"].presentValue=max_humidity
        bacnet_device["Minimum Humidity 24H"].presnetValue=min_humidity

        print("devices updated")
        time.sleep(31*60)  # Wait for 31 mins before starting a new device instance
except Exception as e:
    print(f"Error: {e}")
