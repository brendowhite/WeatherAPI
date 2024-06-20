## The intention of this file is to call weather API information

##  HERE ARE THE DESIRED SPECIFICATIONS FOR THE API

## Included aspects of weather that will be gathered is
## Temperature (current and predictive hourly for 24 hours ahead), humidity (current and predictive hourly for 24 hours ahead), dew point (calculated),
## Enthalpy, Max and average for the next 24 hours for each parameter...
 
# Import necessary modules
from flask import Flask, request, jsonify
import requests
import math
from datetime import datetime
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
def fetchWeatherData():
    global hourly_data, max_temperature, average_temperature, current_temperature, humidity, dew_point, enthalpy
    url = f'http://api.openweathermap.org/data/2.5/forecast?lat=49.2827&lon=-123.1207&units=metric&appid={WEATHER_API_KEY}'
    response = requests.get(url)
    data = response.json()

    try:
        hourly_data = data['list'][:8]
        hourly_temperatures = [hour['main']['temp'] for hour in hourly_data]
        max_temperature = max(hourly_temperatures)
        average_temperature = sum(hourly_temperatures) / len(hourly_temperatures)
        current_temperature = hourly_data[0]['main']['temp']
        humidity = hourly_data[0]['main']['humidity']
        dew_point = dewPointCalc(current_temperature, humidity)
        enthalpy = enthalpyCalc(current_temperature, humidity)
    except KeyError:
        print("Error fetching initial weather data")

# Create a scheduler to update weather data every 3 hours
scheduler = BackgroundScheduler()
scheduler.add_job(fetchWeatherData, 'interval', seconds=10)
scheduler.start()

# Define a route to get weather data
@app.route('/weather', methods=['GET'])
def get_weather():
    try:
        # Extract temperature and time for the next 24 hours
        hourly_temperature_time = [(hour['main']['temp'], datetime.strptime(hour['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')) for hour in hourly_data]

        # Get the current time
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        return jsonify({
            "Current Time": current_time,
            "Temperature (C)": current_temperature,
            "Humidity (%)": humidity,
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
    # Fetch initial weather data
    fetchWeatherData()
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








