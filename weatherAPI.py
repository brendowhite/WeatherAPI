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
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Replace with your OpenWeatherMap API key
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
        hourly_data = data['list'][0:8]
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

        # Calculate hourly temperature timestamps
        hourly_temperature_time = []
        current_time = datetime.now()

        for i, hour in enumerate(hourly_data):
            # Calculate the timestamp for each hour (starting from 3 hours from now - this will print as HH:MM:SS)
            timestamp = current_time + timedelta(hours=(i + 1) * 3)
            formatted_timestamp = timestamp.strftime('%d/%m/%Y %H:%M:%S')
            hourly_temperature_time.append((hour['main']['temp'], formatted_timestamp))

        return jsonify({
            "Current Time": current_time.strftime('%d/%m/%Y %H:%M:%S'),
            "Current Temperature (C)": current_temperature,
            "Current Humidity (%)": humidity,
            "Average Temperature (C) (24-hour period)": average_temperature,
            "Maximum Temperature (C) (24-hour period)": max_temperature,
            "Maximum Humidity (24-hour period) (%)": max(h['main']['humidity'] for h in hourly_data) if hourly_data else None,
            "Dew Point": dew_point,
            "Enthalpy": enthalpy,
            "Hourly Temperature Timestamped": hourly_temperature_time
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching weather data: {str(e)}"}), 500


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








