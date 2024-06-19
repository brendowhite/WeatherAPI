## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...

from flask import Flask, request, jsonify
import requests

## This function requests the weather data from the weather API
## It requests 3 paramters - latitude, longitude and the API key

#app = Flask(__name__)
API_KEY = 'insert weather api key'

def getWeatherData(latitude, longitude):
    base_url = "insert API site here http:// ..."
    params = {
        'latitude' : latitude,
        'longitude' : longitude,
        'applicaton_ID' : API_KEY,
        'units' : 'metric'  # uses metric measurements. Substitute 'metric' with 'imperial' for Fahrenheit
    }

    response = requests.get(base_url, params=params)

    data = response.json()

    if response.status_code == 200:
        # Extract temperature and humidity
        weather_information = {
            'temperature': data['main']
            ['temperature'],
            'humidity': data['main']
            ['humidity']
        }
        return weather_information
    else: 
            return {'error': data.get('message', 'Error fetching weather data')
        }


def weather():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    if not latitude or not longitude :
         return jsonify({'error':'Latitude and Longitude parameters are required'}), 400
    
    try:
         latitude = float(latitude)
         longitude = float(longitude)
    except ValueError:
         return jsonify({'error': 'Invalid latitude or longitude values'}), 400
    
    
    weather_data = getWeatherData(latitude, longitude, API_KEY)

    return jsonify(weather_data)








