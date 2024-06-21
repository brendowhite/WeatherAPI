## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...
 
## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...
 
# Import necessary modules
from flask import Flask, request, jsonify
import requests
import math
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler # have attempted scheduling, need to revisit this
#from bacpypes.object import AnalogInputObject, AnalogValueObject

app = Flask(__name__)

# OpenWeatherMap API key (needs to not be hard coded so that the user can input it themselves)
WEATHER_API_KEY = '0d5d2cfed28b5145804a9901a16c2b40'

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

# Function to fetch initial weather data
def fetchWeatherData(lat, lon):
    global hourly_data, max_temperature, average_temperature, current_temperature, humidity, dew_point, enthalpy
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    try:
        hourly_data = data['list'][0:9]
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = data['list'][0]['main']['temp']
        humidity = data['list'][0]['main']['humidity']
        dew_point = dewPointCalc(current_temperature, humidity)
        enthalpy = enthalpyCalc(current_temperature, humidity)
    except KeyError:
        print("Error fetching initial weather data")

# Create a route to get weather data
@app.route('/weather', methods=['GET'])
def get_weather():
    try:
        # Get latitude and longitude from query parameters
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # Fetch weather data using the provided latitude and longitude
        fetchWeatherData(lat, lon)

        # Calculate hourly temperature and humidity timestamps
        hourly_temperature_time = []
        hourly_humidity_time = []
        current_time = datetime.now()

        for i, hour in enumerate(hourly_data):
            # Calculate the timestamp for each hour (starting from the current time)
            # timestamp = current_time + timedelta(hours=i * 3)
            # formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            time_label = f"Current time + {i * 3} hours"
            hourly_temperature_time.append((hour['main']['temp'], time_label))
            hourly_humidity_time.append((hour['main']['humidity'], time_label))

        return jsonify({
            "Current Time": current_time.strftime('%d/%m/%Y %H:%M:%S'),
            "Temperature (C)": current_temperature,
            "Humidity (%)": humidity,
            "Average Temperature (C) (24-hour period)": average_temperature,
            "Maximum Temperature (C) (24-hour period)": max_temperature,
            "Maximum Humidity (24-hour period) (%)": max(h['main']['humidity'] for h in hourly_data) if hourly_data else None,
            "Dew Point": dew_point,
            "Enthalpy": enthalpy,
            "3 Hourly Temperatures (C) Timestamped": hourly_temperature_time,
            "3 Hourly Humidity (%) Timestamped": hourly_humidity_time
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching weather data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


# Need to still find and use BOM XML data to compare and interpolate the data


# Begin BACnet integration attempt

# create some BACnet objects 

# Define BACnet object IDs
# TEMPERATURE_OBJECT_ID = (1, 0)
# HUMIDITY_OBJECT_ID = (2, 0)

# # Create BACnet objects
# temperature_object = AnalogValueObject(objectIdentifier=TEMPERATURE_OBJECT_ID, presentValue=current_temperature)
# humidity_object = AnalogValueObject(objectIdentifier=HUMIDITY_OBJECT_ID, presentValue=humidity)

# # Update the BACnet objects with the calculated values
# temperature_object.update()
# humidity_object.update()



# Techbeast.org youtube

# latitude and longitude for 123 epping rd -33.784183, 151.118332
