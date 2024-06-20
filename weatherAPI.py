## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...

# Import necessary libraries
from flask import Flask, request, jsonify
import requests
import os
import math
from datetime import datetime

app = Flask(__name__)

WEATHER_API_KEY = '0d5d2cfed28b5145804a9901a16c2b40'

# Function to calculate dew point
def dew_point_calc(temp, humidity):
    a = 17.27
    b = 237.7
    alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100)
    dew_point = (b * alpha) / (a - alpha)
    return dew_point

# Function to calculate enthalpy
def enthalpy_calc(temp, humidity):
    dew_point = dew_point_calc(temp, humidity)
    h = 1.006 * temp
    latent_heat = 2501
    specific_humidity = 0.622 * (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)) / (1013.25 - (humidity / 100) * 6.112 * math.exp((17.67 * dew_point) / (243.5 + dew_point)))
    enthalpy = h + (latent_heat * specific_humidity)
    return enthalpy

@app.route('/weather', methods=['GET'])
def get_weather():
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')

    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    try:
        hourly_data = data['list']
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = hourly_data[0]['main']['temp']
        humidity = hourly_data[0]['main']['humidity']
        dew_point = dew_point_calc(current_temperature, humidity)
        enthalpy = enthalpy_calc(current_temperature, humidity)

        # Extract temperature and time for the next 24 hours
        hourly_temperature_time = [(hour['main']['temp'], datetime.strptime(hour['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')) for hour in hourly_data]

        return jsonify({
            "Temperature (C)": current_temperature,
            "Humidity (%)": humidity,
            "Average Temperature (C) (24-hour period)": average_temperature,
            "Maximum Temperature (C) (24-hour period)": max_temperature,
            "Maximum Humidity (24-hour period) (C)": max(h['main']['humidity'] for h in hourly_data),
            "Dew Point": dew_point,
            "Enthalpy": enthalpy,
            "Hourly Temperature Timestamped": hourly_temperature_time
        })
    except KeyError:
        return jsonify({"error": "Weather data not available"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

 



























# CODE GRAVEYARD #

#app = Flask(__name__)
# API_KEY = 'insert weather api key'

# def getWeatherData(latitude, longitude):
#     base_url = "insert API site here http:// ..."
#     params = {
#         'latitude' : latitude,
#         'longitude' : longitude,
#         'applicaton_ID' : API_KEY,
#         'units' : 'metric'  # uses metric measurements. Substitute 'metric' with 'imperial' for Fahrenheit
#     }

#     response = requests.get(base_url, params=params)

#     data = response.json()

#     if response.status_code == 200:
#         # Extract temperature and humidity
#         weather_information = {
#             'temperature': data['main']
#             ['temperature'],
#             'humidity': data['main']
#             ['humidity']
#         }
#         return weather_information
#     else: 
#             return {'error': data.get('message', 'Error fetching weather data')
#         }


# def weather():
#     latitude = request.args.get('latitude')
#     longitude = request.args.get('longitude')

#     if not latitude or not longitude :
#          return jsonify({'error':'Latitude and Longitude parameters are required'}), 400
    
#     try:
#          latitude = float(latitude)
#          longitude = float(longitude)
#     except ValueError:
#          return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    
    
#     weather_data = getWeatherData(latitude, longitude, API_KEY)

#     return jsonify(weather_data)








