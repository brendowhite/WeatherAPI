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

def fetchWeatherData():
    # define global variables to be used in updating analog_values on BACnet device
    global current_temperature, humidity, current_dew_point, current_enthalpy, hourly_temperatures, hourly_humidity, max_temperature, average_temperature
    global dew_point3hr, dew_point6hr, dew_point9hr, dew_point12hr, dew_point15hr, dew_point18hr, dew_point21hr, dew_point24hr
    global enthalpy3hr, enthalpy6hr, enthalpy9hr, enthalpy12hr, enthalpy15hr, enthalpy18hr, enthalpy21hr, enthalpy24hr
    try:
        lat = float(input("Enter latitude: "))
        lon = float(input("Enter longitude: "))
        # api_key = float(input("Enter your OpenWeatherMap API key: "))
    except ValueError:
        print("Invalid input! Please enter valid numeric values for latitude and longitude.")
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
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = data['list'][0]['main']['temp']
        humidity = data['list'][0]['main']['humidity']

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

        # Logic to refresh the weather data every 3 hours
        while True:
            # time.sleep(10)  # Wait for 3 hours
            response = requests.get(url)
            data = response.json()

            hourly_data = data['list'][0:9]
            hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
            hourly_humidity = [hour['main']['humidity'] for hour in hourly_data]
            current_temperature = data['list'][0]['main']['temp']
            humidity = data['list'][0]['main']['humidity']
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

    except KeyError:
        print("Error fetching initial weather data")
        

# fetching weather data based on user input arguments 
fetchWeatherData()


# # Create the virtual BACnet device below, it will include a number of different analog_values for weather metrics
def start_device():
    new_device = BAC0.lite(deviceId=10032)
    time.sleep(1)

    # Analog Values
    _new_objects = analog_value(
        instance=1,
        name="Current_Temp",
        description="Current Temperature in degC", 
        presentValue=current_temperature,
        properties={"units": "degreesCelsius"},
    )
    _new_objects = analog_value(
        instance=2,
        name="Humidity",
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
# up to here

    _new_objects.add_objects_to_application(new_device)
    return new_device

try:
    bacnet_device = start_device()
    while True:
        time.sleep(60)  # Wait for 60 seconds before starting a new device instance
except Exception as e:
    print(f"Error: {e}")


thread = threading.Thread(target=start_device)

