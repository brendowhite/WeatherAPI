## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...

from flask import Flask, request, jsonify
import requests
import math
import os

app = Flask(__name__)

WEATHER_API_KEY = '0d5d2cfed28b5145804a9901a16c2b40'


# Function to get the weather based on latitude and longitude

def getWeatherData(latitude, longitude): #api_key):
    
    # This will construct the query URL that relates to the API selected
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon{longitude}&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    weather_data = []
    for entry in data['list'][:8]: # can only collect next 24 hours in 3 hour intervals with this api, haven't been able to find a better option that is free...
        weather_data.append({
            'time': entry['dt_txt'],
            'temperature': entry['main']['temp'],
            'humidity': entry['main']['humidity']                 
        })

        return weather_data


# function that calculates the dew point

def dewPointCalc(temp, humidity):
    a = 17.27 # magnus coefficients a and b
    b = 237.7
    alpha = ((a * temp) / (b + temp)) + math.log(humidity / 100)
    dewPoint = (b * alpha) / (a - alpha)
    return dewPoint

# function that calculates the enthalpy
# NEEDS TO BE VERIFIED ONLINE #
def enthalpyCalc(temp, humidity):
    dew_Point = dewPointCalc(temp, humidity)
    h = 1.006 * temp
    latent_heat = 2501
    specific_humidity = 0.622 * (humidity/100) * 6.112 * math.exp((17.67 * dew_Point) / (243.5 + dew_Point)) / (1013.25 - (humidity / 100) * 6.112 * math.exp((17.67 * dew_Point) / (243.5 + dew_Point)))
    
    enthalpy = h + (latent_heat * specific_humidity)

    return enthalpy

# Function that calculates the average and maximum temperature

def avgAndMaxTempCalc(weather_data):
    temperatures = [entry['temperature']
                    for entry in weather_data]
    avg_temp = sum(temperatures) / len(temperatures)
    max_temp = max(temperatures)
    return avg_temp, max_temp


@app.route('/weather', methods=['get'])
def extractWeatherMetrics():
    api_key = os.getenv(WEATHER_API_KEY)
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')

    if not api_key:
        return jsonify({"error" : "Weather API Key is not found"}), 500
    
    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    weather_data = getWeatherData(latitude, longitude)
    
    for entry in weather_data:
        entry['dew point'] = dewPointCalc(entry['temperature'], entry['humidity'])
        entry['enthalpy'] = enthalpyCalc(entry['temperature'], entry['humidity'])

        avg_temp, max_temp = avgAndMaxTempCalc(weather_data)

        response = {'weather data' : weather_data,
                   'average temperature' : avg_temp,
                   'maximum temperature' : max_temp
                   }
        
        return jsonify(response)
    
if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')

 



























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








