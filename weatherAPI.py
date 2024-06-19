## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...

from flask import Flask, request, jsonify
import requests

## This function requests the weather data from the weather API
## It requests 3 paramters - latitude, longitude and the API key




def getWeatherData(latitude, longitude, api_key):
    base_url = "insert API site here http:// ..."
    params = {
        'latitude' : latitude,
        'longitude' : longitude,
        'applicaton_ID' : api_key,
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

            return weather_information
        }


    return response.json


API_KEY = 'weather api key goes here'
app = Flask(__name__)


def weather():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
