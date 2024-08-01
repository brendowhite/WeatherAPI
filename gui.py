import tkinter as tk
import time
from tkinter import messagebox
import requests
import threading
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from licenseVerification import verifyKey


########################### GUI FUNCTIONALITY ################################

# function to collect user inputs from the form once "confirm configuration" is pressed
def submit_form():
    try:
        # gather the inputs from the input boxes
        lat = float(latitude_entry.get())
        lon = float(longitude_entry.get())
        inputAlt = float(altitude_entry.get())
        api_token = api_key_entry.get()
        device_Id = int(device_entry.get())
        port_Id = port_entry.get()
        num_requests = int(requests_entry.get())

    # validation checks for values and empty boxes
        if not validate_lat(lat):
            messagebox.showerror("Error", "Invalid latitude, please enter a value between -90 and 90 degrees.")
            return
        
        if not validate_lon(lon):
            messagebox.showerror("Error", "Invalid longitude, please enter a value between -180 and 180 degrees.")
            return
        # Check if all fields are filled
        if not (lat and lon and inputAlt and api_token and device_Id and port_Id):
            messagebox.showerror("Error", "Please fill in all fields before submitting.")
            return

        # Check if the API key is valid (you can replace this with your own validation logic)
        if not validateAPIToken(api_token):
            messagebox.showerror("Error", "Invalid API key. Please check your token.")
            return
        
        if not validDeviceId(device_Id):
            messagebox.showerror("Error", "Please enter a device ID between 0 and 4194302")
            return
        
        if not validateNumRequests(num_requests):
            messagebox.showerror("Error", "Please enter less than 1000 daily requests")
            return
        
        # Create the folder to store configuration data if it doesn't exist already
        folder_path = "C:\\BACnetWeatherFetchData"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        # write the entered parameters to the xml
        writeParamtersToXML(lat, lon, inputAlt, api_token, device_Id, port_Id, num_requests)

    except ValueError:
        messagebox.showerror("Error", "Invalid input! Please enter valid numeric values for latitude, longitude, and altitude.")
        # Reset lat and lon to None
        lat = None
        lon = None

    # tests to check if input is valid
def validateNumRequests(num_requests):
    return 1 <= num_requests <= 1000

    # function to validate longitude input
def validate_lon(lon):
    return -180 <= lon <= 180

    # function to validate latitude input
def validate_lat(lat):
    return -90 <= lat <= 90

    # function to validate weather API token input
def validateAPIToken(WEATHER_API_TOKEN):
    try:
        # dummy request to confirm token validity
        url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={WEATHER_API_TOKEN}"
        response = requests.get(url)
        # checks code that confirms validity of the key
        if response.status_code == 200:
            print("API key is valid.")
            return True
        else: # returns that the key is invalid
            print("API key is invalid.")
            return False
    except requests.RequestException:
        print("Error occurred while checking the API key.")
        return False    

# check that ensures that device id does not exceed bacnet protocol limit
def validDeviceId(device_Id):
    return 0 <= device_Id <= 4194302

# creates clock with live time widget
def update_time():
    current_time = time.strftime('%d-%m-%Y\n%H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000,update_time)
    
    # enables stop button functionality to kill all GUI execution 
def stopProgram():
    sys.exit()


def runReadAndSet():
    while True:
        readWeatherXML()
        setTextBoxes()
        updateOpenMeteoBoxes()
        time.sleep(15)

def runReadThread():
    thread = threading.Thread(daemon=True, target=runReadAndSet)
    thread.start()

def clearOpenWeatherBoxes():
    entries = [
        currenttemp_entry, maxtemp_entry, minimumtemp_entry, temp3hr_entry, temp6hr_entry, temp9hr_entry, temp12hr_entry, temp15hr_entry, temp18hr_entry, temp21hr_entry, temp24hr_entry,
        currenthumidity_entry, maxhumidity_entry, minimumhumidity_entry, humid3hr_entry, humid6hr_entry, humid9hr_entry, humid12hr_entry, humid15hr_entry, humid18hr_entry, humid21hr_entry, humid24hr_entry,
        currentdewpt_entry, maxdewpt_entry, minimumdewpt_entry, dewpt3hr_entry, dewpt6hr_entry, dewpt9hr_entry, dewpt12hr_entry, dewpt15hr_entry, dewpt18hr_entry, dewpt21hr_entry, dewpt24hr_entry,
        currententhalpy_entry, maxenthalpy_entry, minimumenthalpy_entry, enthalpy3hr_entry, enthalpy6hr_entry, enthalpy9hr_entry, enthalpy12hr_entry, enthalpy15hr_entry, enthalpy18hr_entry, enthalpy21hr_entry, enthalpy24hr_entry
    ]
    
    for entry in entries:
        entry.delete(0, tk.END)
        entry.config(bg='white')

def clearOpenMeteoBoxes():
        # List of all temperature, humidity, and dew point entry boxes
    entries = [
        BOMcurrenttemp_entry, BOMmaxtemp_entry, BOMminimumtemp_entry,
        BOMtemp3hr_entry, BOMtemp6hr_entry, BOMtemp9hr_entry,
        BOMtemp12hr_entry, BOMtemp15hr_entry, BOMtemp18hr_entry,
        BOMtemp21hr_entry, BOMtemp24hr_entry, BOMcurrenthumidity_entry,
        BOMmaxhumidity_entry, BOMminimumhumidity_entry, BOMhumid3hr_entry,
        BOMhumid6hr_entry, BOMhumid9hr_entry, BOMhumid12hr_entry,
        BOMhumid15hr_entry, BOMhumid18hr_entry, BOMhumid21hr_entry,
        BOMhumid24hr_entry, BOMcurrentdewpt_entry, BOMmaxdewpt_entry,
        BOMminimumdewpt_entry, BOMdewpt3hr_entry, BOMdewpt6hr_entry,
        BOMdewpt9hr_entry, BOMdewpt12hr_entry, BOMdewpt15hr_entry,
        BOMdewpt18hr_entry, BOMdewpt21hr_entry, BOMdewpt24hr_entry, 
        BOMcurrententhalpy_entry, BOMmaxenthalpy_entry, BOMenthalpy3hr_entry,
        BOMenthalpy6hr_entry, BOMenthalpy9hr_entry, BOMenthalpy12hr_entry,
        BOMenthalpy15hr_entry, BOMenthalpy18hr_entry, BOMenthalpy21hr_entry, BOMenthalpy24hr_entry, BOMminimumenthalpy_entry
    ]
    
    # Clear the contents and set the background color to white
    for entry in entries:
        entry.delete(0, tk.END)
        entry.config(bg='white')

def writeParamtersToXML(lat, lon, inputAlt, api_token, device_Id, port_Id, num_requests):
    # Create an XML structure
    root = ET.Element("settings")

    # Add child elements for each parameter
    lat_elem = ET.SubElement(root, "latitude")
    lat_elem.text = str(lat)

    lon_elem = ET.SubElement(root, "longitude")
    lon_elem.text = str(lon)

    inputAlt_elem = ET.SubElement(root, "altitude")
    inputAlt_elem.text = str(inputAlt)

    api_token_elem = ET.SubElement(root, "api_token")
    api_token_elem.text = api_token

    device_Id_elem = ET.SubElement(root, "device_Id")
    device_Id_elem.text = str(device_Id)

    port_Id_elem = ET.SubElement(root, "port_Id")
    port_Id_elem.text = port_Id

    num_requests_elem = ET.SubElement(root, "num_requests")
    num_requests_elem.text = str(num_requests)

    # Save the XML to a file
    tree_str = ET.tostring(root, encoding="utf-8")
    pretty_xml = minidom.parseString(tree_str).toprettyxml(indent="  ")

    with open("C:\\BACnetWeatherFetchData\settings.xml", "w") as xml_file:
        xml_file.write(pretty_xml)

def loadSettingsXML():
    settingsXML = 'C:\\BACnetWeatherFetchData\\settings.xml'
    
    # Check if the file exists before parsing
    if os.path.exists(settingsXML):
        tree = ET.parse(settingsXML)
        root = tree.getroot()
        
        latitude = float(root.find('latitude').text)
        latitude_entry.delete(0, tk.END)
        latitude_entry.insert(0, latitude)
        longitude = float(root.find('longitude').text)
        longitude_entry.delete(0, tk.END)
        longitude_entry.insert(0, longitude)
        altitude = float(root.find('altitude').text)
        altitude_entry.delete(0, tk.END)
        altitude_entry.insert(0, altitude)
        device_Id = int(root.find('device_Id').text)
        device_entry.delete(0, tk.END)
        device_entry.insert(0, device_Id)
        port_Id = int(root.find('port_Id').text)
        port_entry.delete(0, tk.END)
        port_entry.insert(0, port_Id)
        num_requests = int(root.find('num_requests').text)
        requests_entry.delete(0, tk.END)
        requests_entry.insert(0, num_requests)

    else:
        # If the file doesn't exist, you can set the default state of your entries here
        latitude_entry.delete(0, tk.END)         # No need to insert anything since we want it to be empty
        longitude_entry.delete(0, tk.END)
        altitude_entry.delete(0, tk.END)
        device_entry.delete(0, tk.END)
        port_entry.delete(0, tk.END)
        requests_entry.delete(0, tk.END)


def readWeatherXML():
    global current_temperature, max_temperature, minimum_temperature, temp_3, temp_6, temp_9, temp_12, temp_15, temp_18, temp_18, temp_21, temp_24
    global current_humidity, max_humidity, minimum_humidity, humid_3, humid_6, humid_9, humid_12, humid_15, humid_18, humid_21, humid_24
    global current_enthalpy, max_enthalpy, minimum_enthalpy, enth_3, enth_6, enth_9, enth_12, enth_15, enth_18, enth_21, enth_24
    global current_dewpt, max_dewpt, minimum_dewpt, dew_3, dew_6, dew_9, dew_12, dew_15, dew_18, dew_21, dew_24

# path for xml file reading
    xmlfile = 'C:\\BACnetWeatherFetchData\weather_data.xml'
    tree = ET.parse(xmlfile)
    # extract weather values from the xml
    root = tree.getroot()
    # extract temperature data 
    current_temperature = float(root.find('current_temperature').text)
    max_temperature = float(root.find('max_temperature').text)
    minimum_temperature = float(root.find('minimum_temperature').text)
    temp_3 = float(root.find('temp3hr').text)
    temp_6 = float(root.find('temp6hr').text)
    temp_9 = float(root.find('temp9hr').text)
    temp_12 = float(root.find('temp12hr').text)
    temp_15 = float(root.find('temp15hr').text)
    temp_18 = float(root.find('temp18hr').text)
    temp_21 = float(root.find('temp21hr').text)
    temp_24 = float(root.find('temp24hr').text)
    # extract humidity data 
    current_humidity = float(root.find('humidity').text)
    max_humidity = float(root.find('max_humidity').text)
    minimum_humidity = float(root.find('minimum_humidity').text)
    humid_3 = float(root.find('hum3hr').text)
    humid_6 = float(root.find('hum6hr').text)
    humid_9 = float(root.find('hum9hr').text)
    humid_12 = float(root.find('hum12hr').text)
    humid_15 = float(root.find('hum15hr').text)
    humid_18 = float(root.find('hum18hr').text)
    humid_21 = float(root.find('hum21hr').text)
    humid_24 = float(root.find('hum24hr').text)
    # extract dew point data
    current_dewpt = float(root.find('current_dew_point').text)
    max_dewpt = float(root.find('max_dewpt').text)
    minimum_dewpt = float(root.find('minimum_dewpt').text)
    dew_3 = float(root.find('dew_point3hr').text)
    dew_6 = float(root.find('dew_point6hr').text)
    dew_9 = float(root.find('dew_point9hr').text)
    dew_12 = float(root.find('dew_point12hr').text)
    dew_15 = float(root.find('dew_point15hr').text)
    dew_18 = float(root.find('dew_point18hr').text)
    dew_21 = float(root.find('dew_point21hr').text)
    dew_24 = float(root.find('dew_point24hr').text)
    #extract enthalpy data
    current_enthalpy = float(root.find('current_enthalpy').text)
    max_enthalpy = float(root.find('max_enthalpy').text)
    minimum_enthalpy = float(root.find('minimum_enthalpy').text)
    enth_3 = float(root.find('enthalpy3hr').text)
    enth_6 = float(root.find('enthalpy6hr').text)
    enth_9 = float(root.find('enthalpy9hr').text)
    enth_12 = float(root.find('enthalpy12hr').text)
    enth_15 = float(root.find('enthalpy15hr').text)
    enth_18 = float(root.find('enthalpy18hr').text)
    enth_21 = float(root.find('enthalpy21hr').text)
    enth_24 = float(root.find('enthalpy24hr').text)

def readOpenMeteoWeather():
    # reading path for weather xml
    xmlfile = 'C:\\BACnetWeatherFetchData\\OpenMeteo_weather_data.xml'
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    # creating dictionary for BOM data
    data = {
        "BOMtemp0h": float(root.findtext("Temperatures/BOMtemp0h")),
        "BOMtemp3h": float(root.findtext("Temperatures/BOMtemp3h")),
        "BOMtemp6h": float(root.findtext("Temperatures/BOMtemp6h")),
        "BOMtemp9h": float(root.findtext("Temperatures/BOMtemp9h")),
        "BOMtemp12h": float(root.findtext("Temperatures/BOMtemp12h")),
        "BOMtemp15h": float(root.findtext("Temperatures/BOMtemp15h")),
        "BOMtemp18h": float(root.findtext("Temperatures/BOMtemp18h")),
        "BOMtemp21h": float(root.findtext("Temperatures/BOMtemp21h")),
        "BOMtemp24h": float(root.findtext("Temperatures/BOMtemp24h")),
        "BOMmax_temp": float(root.findtext("Temperatures/BOMmax_temp")),
        "BOMminimum_temp": float(root.findtext("Temperatures/BOMminimum_temp")),
        "BOMhumidity0h": float(root.findtext("Humidities/BOMhumidity0h")),
        "BOMhumidity3h": float(root.findtext("Humidities/BOMhumidity3h")),
        "BOMhumidity6h": float(root.findtext("Humidities/BOMhumidity6h")),
        "BOMhumidity9h": float(root.findtext("Humidities/BOMhumidity9h")),
        "BOMhumidity12h": float(root.findtext("Humidities/BOMhumidity12h")),
        "BOMhumidity15h": float(root.findtext("Humidities/BOMhumidity15h")),
        "BOMhumidity18h": float(root.findtext("Humidities/BOMhumidity18h")),
        "BOMhumidity21h": float(root.findtext("Humidities/BOMhumidity21h")),
        "BOMhumidity24h": float(root.findtext("Humidities/BOMhumidity24h")),
        "BOMmax_humidity": float(root.findtext("Humidities/BOMmax_humidity")),
        "BOMminimum_humidity": float(root.findtext("Humidities/BOMminimum_humidity")),
        "BOMdewpoint0h": float(root.findtext("DewPoints/BOMdewpoint0h")),
        "BOMdewpoint3h": float(root.findtext("DewPoints/BOMdewpoint3h")),
        "BOMdewpoint6h": float(root.findtext("DewPoints/BOMdewpoint6h")),
        "BOMdewpoint9h": float(root.findtext("DewPoints/BOMdewpoint9h")),
        "BOMdewpoint12h": float(root.findtext("DewPoints/BOMdewpoint12h")),
        "BOMdewpoint15h": float(root.findtext("DewPoints/BOMdewpoint15h")),
        "BOMdewpoint18h": float(root.findtext("DewPoints/BOMdewpoint18h")),
        "BOMdewpoint21h": float(root.findtext("DewPoints/BOMdewpoint21h")),
        "BOMdewpoint24h": float(root.findtext("DewPoints/BOMdewpoint24h")),
        "BOMmax_dewpoint": float(root.findtext("DewPoints/BOMmax_dewpoint")),
        "BOMminimum_dewpoint": float(root.findtext("DewPoints/BOMminimum_dewpoint")),
        "BOMenthalpy0h": float(root.findtext("Enthalpies/BOMenthalpy0h")),
        "BOMenthalpy3h": float(root.findtext("Enthalpies/BOMenthalpy3h")),
        "BOMenthalpy6h": float(root.findtext("Enthalpies/BOMenthalpy6h")),
        "BOMenthalpy9h": float(root.findtext("Enthalpies/BOMenthalpy9h")),
        "BOMenthalpy12h": float(root.findtext("Enthalpies/BOMenthalpy12h")),
        "BOMenthalpy15h": float(root.findtext("Enthalpies/BOMenthalpy15h")),
        "BOMenthalpy18h": float(root.findtext("Enthalpies/BOMenthalpy18h")),
        "BOMenthalpy21h": float(root.findtext("Enthalpies/BOMenthalpy21h")),
        "BOMenthalpy24h": float(root.findtext("Enthalpies/BOMenthalpy24h")),
        "BOMmax_enthalpy": float(root.findtext("Enthalpies/BOMmax_enthalpy")),
        "BOMminimum_enthalpy": float(root.findtext("Enthalpies/BOMminimum_enthalpy")),
    }
    return data

def updateOpenMeteoBoxes():
    # create instance of weather information to access current data
    weather_data= readOpenMeteoWeather()
    # Update temperature entry boxes
    BOMcurrenttemp_entry.delete(0, tk.END)
    BOMcurrenttemp_entry.insert(0, weather_data["BOMtemp0h"])
    BOMmaxtemp_entry.delete(0, tk.END)
    BOMmaxtemp_entry.insert(0, weather_data["BOMmax_temp"])
    BOMminimumtemp_entry.delete(0, tk.END)
    BOMminimumtemp_entry.insert(0, weather_data["BOMminimum_temp"])
    BOMtemp3hr_entry.delete(0, tk.END)
    BOMtemp3hr_entry.insert(0, weather_data["BOMtemp3h"])
    BOMtemp6hr_entry.delete(0, tk.END)
    BOMtemp6hr_entry.insert(0, weather_data["BOMtemp6h"])
    BOMtemp9hr_entry.delete(0, tk.END)
    BOMtemp9hr_entry.insert(0, weather_data["BOMtemp9h"])
    BOMtemp12hr_entry.delete(0, tk.END)
    BOMtemp12hr_entry.insert(0, weather_data["BOMtemp12h"])
    BOMtemp15hr_entry.delete(0, tk.END)
    BOMtemp15hr_entry.insert(0, weather_data["BOMtemp15h"])
    BOMtemp18hr_entry.delete(0, tk.END)
    BOMtemp18hr_entry.insert(0, weather_data["BOMtemp18h"])
    BOMtemp21hr_entry.delete(0, tk.END)
    BOMtemp21hr_entry.insert(0, weather_data["BOMtemp21h"])
    BOMtemp24hr_entry.delete(0, tk.END)
    BOMtemp24hr_entry.insert(0, weather_data["BOMtemp24h"])

    # Find the maximum temperature
    temperatures = {
        'BOMtemp0h': weather_data["BOMtemp0h"],
        'BOMtemp3h': weather_data["BOMtemp3h"],
        'BOMtemp6h': weather_data["BOMtemp6h"],
        'BOMtemp9h': weather_data["BOMtemp9h"],
        'BOMtemp12h': weather_data["BOMtemp12h"],
        'BOMtemp15h': weather_data["BOMtemp15h"],
        'BOMtemp18h': weather_data["BOMtemp18h"],
        'BOMtemp21h': weather_data["BOMtemp21h"],
        'BOMtemp24h': weather_data["BOMtemp24h"],
        'BOMmax_temp': weather_data["BOMmax_temp"],
        'BOMminimum_temp': weather_data["BOMminimum_temp"]
    }
    max_temp_value = max(temperatures.values())
    min_temp_value = min(temperatures.values())
    
    # Set the corresponding entries to red if they match the maximum temperature
    temperature_entries = {
        'BOMtemp0h': BOMcurrenttemp_entry,
        'BOMtemp3h': BOMtemp3hr_entry,
        'BOMtemp6h': BOMtemp6hr_entry,
        'BOMtemp9h': BOMtemp9hr_entry,
        'BOMtemp12h': BOMtemp12hr_entry,
        'BOMtemp15h': BOMtemp15hr_entry,
        'BOMtemp18h': BOMtemp18hr_entry,
        'BOMtemp21h': BOMtemp21hr_entry,
        'BOMtemp24h': BOMtemp24hr_entry,
        'BOMmax_temp': BOMmaxtemp_entry,
        'BOMminimum_temp': BOMminimumtemp_entry
    }
    
# Assuming you have your temperatures dictionary and temperature_entries defined
    max_temp_value = max(temperatures.values())
    min_temp_value = min(temperatures.values())

    for key, value in temperatures.items():
        if value == max_temp_value:
            temperature_entries[key].config(bg='yellow')
        elif value == min_temp_value:
            temperature_entries[key].config(bg='lightblue')
        else:
            temperature_entries[key].config(bg='white')

    # Update humidity entry boxes
    BOMcurrenthumidity_entry.delete(0, tk.END)
    BOMcurrenthumidity_entry.insert(0, weather_data["BOMhumidity0h"])
    BOMmaxhumidity_entry.delete(0, tk.END)
    BOMmaxhumidity_entry.insert(0, weather_data["BOMmax_humidity"])
    BOMminimumhumidity_entry.delete(0, tk.END)
    BOMminimumhumidity_entry.insert(0, weather_data["BOMminimum_humidity"])
    BOMhumid3hr_entry.delete(0, tk.END)
    BOMhumid3hr_entry.insert(0, weather_data["BOMhumidity3h"])
    BOMhumid6hr_entry.delete(0, tk.END)
    BOMhumid6hr_entry.insert(0, weather_data["BOMhumidity6h"])
    BOMhumid9hr_entry.delete(0, tk.END)
    BOMhumid9hr_entry.insert(0, weather_data["BOMhumidity9h"])
    BOMhumid12hr_entry.delete(0, tk.END)
    BOMhumid12hr_entry.insert(0, weather_data["BOMhumidity12h"])
    BOMhumid15hr_entry.delete(0, tk.END)
    BOMhumid15hr_entry.insert(0, weather_data["BOMhumidity15h"])
    BOMhumid18hr_entry.delete(0, tk.END)
    BOMhumid18hr_entry.insert(0, weather_data["BOMhumidity18h"])
    BOMhumid21hr_entry.delete(0, tk.END)
    BOMhumid21hr_entry.insert(0, weather_data["BOMhumidity21h"])
    BOMhumid24hr_entry.delete(0, tk.END)
    BOMhumid24hr_entry.insert(0, weather_data["BOMhumidity24h"])

        # Find the maximum humidity
    humidities = {
        'BOMhumidity0h': weather_data["BOMhumidity0h"],
        'BOMhumidity3h': weather_data["BOMhumidity3h"],
        'BOMhumidity6h': weather_data["BOMhumidity6h"],
        'BOMhumidity9h': weather_data["BOMhumidity9h"],
        'BOMhumidity12h': weather_data["BOMhumidity12h"],
        'BOMhumidity15h': weather_data["BOMhumidity15h"],
        'BOMhumidity18h': weather_data["BOMhumidity18h"],
        'BOMhumidity21h': weather_data["BOMhumidity21h"],
        'BOMhumidity24h': weather_data["BOMhumidity24h"],
        'BOMmax_humidity': weather_data["BOMmax_humidity"],
        'BOMminimum_humidity': weather_data["BOMminimum_humidity"]
    }

    
    # Set the corresponding entries to red if they match the maximum humidity
    humidity_entries = {
        'BOMhumidity0h': BOMcurrenthumidity_entry,
        'BOMhumidity3h': BOMhumid3hr_entry,
        'BOMhumidity6h': BOMhumid6hr_entry,
        'BOMhumidity9h': BOMhumid9hr_entry,
        'BOMhumidity12h': BOMhumid12hr_entry,
        'BOMhumidity15h': BOMhumid15hr_entry,
        'BOMhumidity18h': BOMhumid18hr_entry,
        'BOMhumidity21h': BOMhumid21hr_entry,
        'BOMhumidity24h': BOMhumid24hr_entry,
        'BOMmax_humidity': BOMmaxhumidity_entry,
        'BOMminimum_humidity': BOMminimumhumidity_entry
    }

    max_humidity_value = max(humidities.values())
    min_humidity_value = min(humidities.values())
    
    for key, value in humidities.items():
        if value == max_humidity_value:
            humidity_entries[key].config(bg='yellow')
        elif value == min_humidity_value:
            humidity_entries[key].config(bg='lightblue')
        else:
            humidity_entries[key].config(bg='white')

    # Update dew point entry boxes
    BOMcurrentdewpt_entry.delete(0, tk.END)
    BOMcurrentdewpt_entry.insert(0, weather_data["BOMdewpoint0h"])
    BOMmaxdewpt_entry.delete(0, tk.END)
    BOMmaxdewpt_entry.insert(0, weather_data["BOMmax_dewpoint"])
    BOMminimumdewpt_entry.delete(0, tk.END)
    BOMminimumdewpt_entry.insert(0, weather_data["BOMminimum_dewpoint"])
    BOMdewpt3hr_entry.delete(0, tk.END)
    BOMdewpt3hr_entry.insert(0, weather_data["BOMdewpoint3h"])
    BOMdewpt6hr_entry.delete(0, tk.END)
    BOMdewpt6hr_entry.insert(0, weather_data["BOMdewpoint6h"])
    BOMdewpt9hr_entry.delete(0, tk.END)
    BOMdewpt9hr_entry.insert(0, weather_data["BOMdewpoint9h"])
    BOMdewpt12hr_entry.delete(0, tk.END)
    BOMdewpt12hr_entry.insert(0, weather_data["BOMdewpoint12h"])
    BOMdewpt15hr_entry.delete(0, tk.END)
    BOMdewpt15hr_entry.insert(0, weather_data["BOMdewpoint15h"])
    BOMdewpt18hr_entry.delete(0, tk.END)
    BOMdewpt18hr_entry.insert(0, weather_data["BOMdewpoint18h"])
    BOMdewpt21hr_entry.delete(0, tk.END)
    BOMdewpt21hr_entry.insert(0, weather_data["BOMdewpoint21h"])
    BOMdewpt24hr_entry.delete(0, tk.END)
    BOMdewpt24hr_entry.insert(0, weather_data["BOMdewpoint24h"])

        # Find the maximum dew point
    dew_points = {
        'BOMdewpoint0h': weather_data["BOMdewpoint0h"],
        'BOMdewpoint3h': weather_data["BOMdewpoint3h"],
        'BOMdewpoint6h': weather_data["BOMdewpoint6h"],
        'BOMdewpoint9h': weather_data["BOMdewpoint9h"],
        'BOMdewpoint12h': weather_data["BOMdewpoint12h"],
        'BOMdewpoint15h': weather_data["BOMdewpoint15h"],
        'BOMdewpoint18h': weather_data["BOMdewpoint18h"],
        'BOMdewpoint21h': weather_data["BOMdewpoint21h"],
        'BOMdewpoint24h': weather_data["BOMdewpoint24h"],
        'BOMmax_dewpoint': weather_data["BOMmax_dewpoint"],
        'BOMminimum_dewpoint': weather_data["BOMminimum_dewpoint"]
    }
    
    
    # Set the corresponding entries to red if they match the maximum dew point
    dew_point_entries = {
        'BOMdewpoint0h': BOMcurrentdewpt_entry,
        'BOMdewpoint3h': BOMdewpt3hr_entry,
        'BOMdewpoint6h': BOMdewpt6hr_entry,
        'BOMdewpoint9h': BOMdewpt9hr_entry,
        'BOMdewpoint12h': BOMdewpt12hr_entry,
        'BOMdewpoint15h': BOMdewpt15hr_entry,
        'BOMdewpoint18h': BOMdewpt18hr_entry,
        'BOMdewpoint21h': BOMdewpt21hr_entry,
        'BOMdewpoint24h': BOMdewpt24hr_entry,
        'BOMmax_dewpoint': BOMmaxdewpt_entry,
        'BOMminimum_dewpoint': BOMminimumdewpt_entry
    }
    max_dew_point = max(dew_points.values())
    min_dew_point = min(dew_points.values())
    
    for key, value in dew_points.items():
        if value == max_dew_point:
            dew_point_entries[key].config(bg='yellow')
        elif value == min_dew_point:
            dew_point_entries[key].config(bg='lightblue')
        else:
            dew_point_entries[key].config(bg='white')


    # Update enthalpy entry boxes
    BOMcurrententhalpy_entry.delete(0, tk.END)
    BOMcurrententhalpy_entry.insert(0, weather_data["BOMenthalpy0h"])
    BOMmaxenthalpy_entry.delete(0, tk.END)
    BOMmaxenthalpy_entry.insert(0, weather_data["BOMmax_enthalpy"])
    BOMminimumenthalpy_entry.delete(0, tk.END)
    BOMminimumenthalpy_entry.insert(0, weather_data["BOMminimum_enthalpy"])
    BOMenthalpy3hr_entry.delete(0, tk.END)
    BOMenthalpy3hr_entry.insert(0, weather_data["BOMenthalpy3h"])
    BOMenthalpy6hr_entry.delete(0, tk.END)
    BOMenthalpy6hr_entry.insert(0, weather_data["BOMenthalpy6h"])
    BOMenthalpy9hr_entry.delete(0, tk.END)
    BOMenthalpy9hr_entry.insert(0, weather_data["BOMenthalpy9h"])
    BOMenthalpy12hr_entry.delete(0, tk.END)
    BOMenthalpy12hr_entry.insert(0, weather_data["BOMenthalpy12h"])
    BOMenthalpy15hr_entry.delete(0, tk.END)
    BOMenthalpy15hr_entry.insert(0, weather_data["BOMenthalpy15h"])
    BOMenthalpy18hr_entry.delete(0, tk.END)
    BOMenthalpy18hr_entry.insert(0, weather_data["BOMenthalpy18h"])
    BOMenthalpy21hr_entry.delete(0, tk.END)
    BOMenthalpy21hr_entry.insert(0, weather_data["BOMenthalpy21h"])
    BOMenthalpy24hr_entry.delete(0, tk.END)
    BOMenthalpy24hr_entry.insert(0, weather_data["BOMenthalpy24h"])

    # Find the maximum enthalpy
    enthalpies = {
        'BOMenthalpy0h': weather_data["BOMenthalpy0h"],
        'BOMenthalpy3h': weather_data["BOMenthalpy3h"],
        'BOMenthalpy6h': weather_data["BOMenthalpy6h"],
        'BOMenthalpy9h': weather_data["BOMenthalpy9h"],
        'BOMenthalpy12h': weather_data["BOMenthalpy12h"],
        'BOMenthalpy15h': weather_data["BOMenthalpy15h"],
        'BOMenthalpy18h': weather_data["BOMenthalpy18h"],
        'BOMenthalpy21h': weather_data["BOMenthalpy21h"],
        'BOMenthalpy24h': weather_data["BOMenthalpy24h"],
        'BOMmax_enthalpy': weather_data["BOMmax_enthalpy"],
        'BOMminimum_enthalpy': weather_data["BOMminimum_enthalpy"]
    }
    
    
    # Set the corresponding entries to yellow if they match the maximum enthalpy
    enthalpy_entries = {
        'BOMenthalpy0h': BOMcurrententhalpy_entry,
        'BOMenthalpy3h': BOMenthalpy3hr_entry,
        'BOMenthalpy6h': BOMenthalpy6hr_entry,
        'BOMenthalpy9h': BOMenthalpy9hr_entry,
        'BOMenthalpy12h': BOMenthalpy12hr_entry,
        'BOMenthalpy15h': BOMenthalpy15hr_entry,
        'BOMenthalpy18h': BOMenthalpy18hr_entry,
        'BOMenthalpy21h': BOMenthalpy21hr_entry,
        'BOMenthalpy24h': BOMenthalpy24hr_entry,
        'BOMmax_enthalpy': BOMmaxenthalpy_entry,
        'BOMminimum_enthalpy': BOMminimumenthalpy_entry
    }

    max_enthalpy_value = max(enthalpies.values())
    min_enthalpy_value = min(enthalpies.values())
    
    for key, value in enthalpies.items():
        if value == max_enthalpy_value:
            enthalpy_entries[key].config(bg='yellow')
        elif value == min_enthalpy_value:
            enthalpy_entries[key].config(bg='lightblue')
        else:
            enthalpy_entries[key].config(bg='white')
    
    # Function that sets the xml data to the corresponding text boxes
def setTextBoxes():
    # Temperature data box updates
    currenttemp_entry.delete(0, tk.END)  # Clear existing value
    currenttemp_entry.insert(0, current_temperature)
    maxtemp_entry.delete(0, tk.END)
    maxtemp_entry.insert(0, max_temperature)
    minimumtemp_entry.delete(0, tk.END)
    minimumtemp_entry.insert(0, minimum_temperature)
    temp3hr_entry.delete(0,tk.END)
    temp3hr_entry.insert(0, temp_3)
    temp6hr_entry.delete(0,tk.END)
    temp6hr_entry.insert(0, temp_6)
    temp9hr_entry.delete(0,tk.END)
    temp9hr_entry.insert(0, temp_9)
    temp12hr_entry.delete(0,tk.END)
    temp12hr_entry.insert(0, temp_12)
    temp15hr_entry.delete(0,tk.END)
    temp15hr_entry.insert(0, temp_15)
    temp18hr_entry.delete(0,tk.END)
    temp18hr_entry.insert(0, temp_18)
    temp21hr_entry.delete(0,tk.END)
    temp21hr_entry.insert(0, temp_21)
    temp24hr_entry.delete(0,tk.END)
    temp24hr_entry.insert(0, temp_24)

    # Find the maximum temperature
    temperatures = {
        'current': current_temperature,
        'max': max_temperature,
        'minimum': minimum_temperature,
        'temp_3': temp_3,
        'temp_6': temp_6,
        'temp_9': temp_9,
        'temp_12': temp_12,
        'temp_15': temp_15,
        'temp_18': temp_18,
        'temp_21': temp_21,
        'temp_24': temp_24
    }
    
    
    # Set the corresponding entries to red if they match the maximum temperature
    temperature_entries = {
        'current': currenttemp_entry,
        'max': maxtemp_entry,
        'minimum': minimumtemp_entry,
        'temp_3': temp3hr_entry,
        'temp_6': temp6hr_entry,
        'temp_9': temp9hr_entry,
        'temp_12': temp12hr_entry,
        'temp_15': temp15hr_entry,
        'temp_18': temp18hr_entry,
        'temp_21': temp21hr_entry,
        'temp_24': temp24hr_entry
    }
    
    max_temp_value = max(temperatures.values())
    min_temp_value = min(temperatures.values())

    for key, value in temperatures.items():
        if value == max_temp_value:
            temperature_entries[key].config(bg='yellow')
        elif value == min_temp_value:
            temperature_entries[key].config(bg='lightblue')
        else:
            temperature_entries[key].config(bg='white')


    #  Enthalpy data box updates
    currenthumidity_entry.delete(0, tk.END)
    currenthumidity_entry.insert(0, current_humidity)
    maxhumidity_entry.delete(0, tk.END)
    maxhumidity_entry.insert(0, max_humidity)
    minimumhumidity_entry.delete(0, tk.END)
    minimumhumidity_entry.insert(0, minimum_humidity)
    humid3hr_entry.delete(0, tk.END)
    humid3hr_entry.insert(0, humid_3)
    humid6hr_entry.delete(0, tk.END)
    humid6hr_entry.insert(0, humid_6)
    humid9hr_entry.delete(0, tk.END)
    humid9hr_entry.insert(0, humid_9)
    humid12hr_entry.delete(0, tk.END)
    humid12hr_entry.insert(0, humid_12)
    humid15hr_entry.delete(0, tk.END)
    humid15hr_entry.insert(0, humid_15)
    humid18hr_entry.delete(0, tk.END)
    humid18hr_entry.insert(0, humid_18)
    humid21hr_entry.delete(0, tk.END)
    humid21hr_entry.insert(0, humid_21)
    humid24hr_entry.delete(0, tk.END)
    humid24hr_entry.insert(0, humid_24)

        # Find the maximum humidity
    humidities = {
        'current': current_humidity,
        'max': max_humidity,
        'minimum': minimum_humidity,
        'humid_3': humid_3,
        'humid_6': humid_6,
        'humid_9': humid_9,
        'humid_12': humid_12,
        'humid_15': humid_15,
        'humid_18': humid_18,
        'humid_21': humid_21,
        'humid_24': humid_24
    }
    
    # Set the corresponding entries to red if they match the maximum humidity
    humidity_entries = {
        'current': currenthumidity_entry,
        'max': maxhumidity_entry,
        'minimum': minimumhumidity_entry,
        'humid_3': humid3hr_entry,
        'humid_6': humid6hr_entry,
        'humid_9': humid9hr_entry,
        'humid_12': humid12hr_entry,
        'humid_15': humid15hr_entry,
        'humid_18': humid18hr_entry,
        'humid_21': humid21hr_entry,
        'humid_24': humid24hr_entry
    }

    max_humidity_value = max(humidities.values())
    min_humidity_value = min(humidities.values())
    
    for key, value in humidities.items():
        if value == max_humidity_value:
            humidity_entries[key].config(bg='yellow')
        elif value == min_humidity_value:
            humidity_entries[key].config(bg='lightblue')
        else:
            humidity_entries[key].config(bg='white')

    # Dew Point data box updates
    currentdewpt_entry.delete(0, tk.END)
    currentdewpt_entry.insert(0, current_dewpt)
    maxdewpt_entry.delete(0, tk.END)
    maxdewpt_entry.insert(0, max_dewpt)
    minimumdewpt_entry.delete(0, tk.END)
    minimumdewpt_entry.insert(0, minimum_dewpt)
    dewpt3hr_entry.delete(0, tk.END)
    dewpt3hr_entry.insert(0, dew_3)
    dewpt6hr_entry.delete(0, tk.END)
    dewpt6hr_entry.insert(0, dew_6)
    dewpt9hr_entry.delete(0, tk.END)
    dewpt9hr_entry.insert(0, dew_9)
    dewpt12hr_entry.delete(0, tk.END)
    dewpt12hr_entry.insert(0, dew_12)
    dewpt15hr_entry.delete(0, tk.END)
    dewpt15hr_entry.insert(0, dew_15)
    dewpt18hr_entry.delete(0, tk.END)
    dewpt18hr_entry.insert(0, dew_18)
    dewpt21hr_entry.delete(0, tk.END)
    dewpt21hr_entry.insert(0, dew_21)
    dewpt24hr_entry.delete(0, tk.END)
    dewpt24hr_entry.insert(0, dew_24)

        # Find the maximum dew point
    dew_points = {
        'current': current_dewpt,
        'max': max_dewpt,
        'minimum': minimum_dewpt,
        'dew_3': dew_3,
        'dew_6': dew_6,
        'dew_9': dew_9,
        'dew_12': dew_12,
        'dew_15': dew_15,
        'dew_18': dew_18,
        'dew_21': dew_21,
        'dew_24': dew_24
    }
    
    
    # Set the corresponding entries to red if they match the maximum dew point
    dew_point_entries = {
        'current': currentdewpt_entry,
        'max': maxdewpt_entry,
        'minimum': minimumdewpt_entry,
        'dew_3': dewpt3hr_entry,
        'dew_6': dewpt6hr_entry,
        'dew_9': dewpt9hr_entry,
        'dew_12': dewpt12hr_entry,
        'dew_15': dewpt15hr_entry,
        'dew_18': dewpt18hr_entry,
        'dew_21': dewpt21hr_entry,
        'dew_24': dewpt24hr_entry
    }

    max_dew_point = max(dew_points.values())
    min_dew_point = min(dew_points.values())
    
    for key, value in dew_points.items():
        if value == max_dew_point:
            dew_point_entries[key].config(bg='yellow')
        elif value == min_dew_point:
            dew_point_entries[key].config(bg='lightblue')
        else:
            dew_point_entries[key].config(bg='white')

    # Enthalpy data box updates
    currententhalpy_entry.delete(0, tk.END)
    currententhalpy_entry.insert(0, current_enthalpy)
    maxenthalpy_entry.delete(0, tk.END)
    maxenthalpy_entry.insert(0, max_enthalpy)
    minimumenthalpy_entry.delete(0, tk.END)
    minimumenthalpy_entry.insert(0, minimum_enthalpy)
    enthalpy3hr_entry.delete(0, tk.END)
    enthalpy3hr_entry.insert(0, enth_3)
    enthalpy6hr_entry.delete(0, tk.END)
    enthalpy6hr_entry.insert(0, enth_6)
    enthalpy9hr_entry.delete(0, tk.END)
    enthalpy9hr_entry.insert(0, enth_9)
    enthalpy12hr_entry.delete(0, tk.END)
    enthalpy12hr_entry.insert(0, enth_12)
    enthalpy15hr_entry.delete(0, tk.END)
    enthalpy15hr_entry.insert(0, enth_15)
    enthalpy18hr_entry.delete(0, tk.END)
    enthalpy18hr_entry.insert(0, enth_18)
    enthalpy21hr_entry.delete(0, tk.END)
    enthalpy21hr_entry.insert(0, enth_21)
    enthalpy24hr_entry.delete(0, tk.END)
    enthalpy24hr_entry.insert(0, enth_24)

        # Find the maximum enthalpy
    enthalpies = {
        'current': current_enthalpy,
        'max': max_enthalpy,
        'minimum': minimum_enthalpy,
        'enth_3': enth_3,
        'enth_6': enth_6,
        'enth_9': enth_9,
        'enth_12': enth_12,
        'enth_15': enth_15,
        'enth_18': enth_18,
        'enth_21': enth_21,
        'enth_24': enth_24
    }
    
    # Set the corresponding entries to red if they match the maximum enthalpy
    enthalpy_entries = {
        'current': currententhalpy_entry,
        'max': maxenthalpy_entry,
        'minimum': minimumenthalpy_entry,
        'enth_3': enthalpy3hr_entry,
        'enth_6': enthalpy6hr_entry,
        'enth_9': enthalpy9hr_entry,
        'enth_12': enthalpy12hr_entry,
        'enth_15': enthalpy15hr_entry,
        'enth_18': enthalpy18hr_entry,
        'enth_21': enthalpy21hr_entry,
        'enth_24': enthalpy24hr_entry
    }
    
    max_enthalpy_value = max(enthalpies.values())
    min_enthalpy_value = min(enthalpies.values())
    
    for key, value in enthalpies.items():
        if value == max_enthalpy_value:
            enthalpy_entries[key].config(bg='yellow')
        elif value == min_enthalpy_value:
            enthalpy_entries[key].config(bg='lightblue')
        else:
            enthalpy_entries[key].config(bg='white')

######################################### GUI START #########################################

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

# gui landing page 
class Page1(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        label = tk.Label(self, text="DEVICE AND API CONFIGURATION", font=("segoe", 12, "bold"))
        label.grid(row=0, column=0, columnspan=4, sticky="w", pady=(10,0))

        #global vars
        global latitude_entry
        global longitude_entry
        global api_key_entry
        global altitude_entry
        global port_entry
        global device_entry
        global requests_entry

        # Row 1 Widgets
        latitude_label = tk.Label(self, text="Latitude (-90 <-> +90):")
        latitude_entry = tk.Entry(self)
        device_label = tk.Label(self, text="BACnet Device ID (0 - 4194302):")
        device_entry = tk.Entry(self)
        latitude_label.grid(row=1, column=0, sticky="w", pady=(10,0))
        latitude_entry.grid(row=1, column=1, sticky="w", pady=(10,0))
        device_label.grid(row=1, column=3, sticky="w", pady=(10,0))
        device_entry.grid(row=1, column=4, sticky="w", pady=(10,0))
         
        # Row 2 widgets
        longitude_label = tk.Label(self, text="Longitude (-180 <-> +180):")
        longitude_entry = tk.Entry(self)
        port_label = tk.Label(self, text="BACnet Port ID:")
        port_entry = tk.Entry(self)
        longitude_label.grid(row=2, column=0, sticky="w")
        longitude_entry.grid(row=2, column=1)
        port_label.grid(row=2, column=3, sticky="w")
        port_entry.grid(row=2, column=4, sticky="w")
        
        # Row 3 widgets
        altitude_label = tk.Label(self, text="Altitude (Metres):")
        altitude_entry = tk.Entry(self)
        altitude_label.grid(row=3, column=0, sticky="w")
        altitude_entry.grid(row=3, column=1, sticky="w")
        requests_label = tk.Label(self, text="Num. Requests 24H (1-1000):")
        requests_entry = tk.Entry(self)
        requests_label.grid(row=3, column=3, sticky="w")
        requests_entry.grid(row=3, column=4, sticky="w")

        # Row 4 label
        api_heading_label = tk.Label(self, text= "WEATHER API SOURCES", font=("segoe", 12, "bold"))
        api_heading_label.grid(row=4, column=0, sticky="w", pady=(10,0))

        # Open weather widgets (R5)
        openweather_api_label = tk.Label(self, text="Open Weather API:")

        api_key_label = tk.Label(self, text="API Key:")
        api_key_entry = tk.Entry(self)

        openweather_api_label.grid(row=5, column=0, sticky="w", pady=(10,0))

        api_key_label.grid(row=5, column=2, sticky="w", pady=(10,0))
        api_key_entry.grid(row=5, column=3, sticky="w", pady=(10,0))

         # Row 6 widgets
        api2_label = tk.Label(self, text="Open-Meteo API (BOM):")
        api2_entry = tk.Entry(self)
        api2_key_label = tk.Label(self, text="API Key:")

        # Set the entry box text and make it uneditable
        api2_entry.insert(0, "No API Key Required")
        api2_entry.config(state='disabled')

        api2_label.grid(row=6, column=0, sticky="w")
        api2_key_label.grid(row=6, column=2)
        api2_entry.grid(row=6, column=3, sticky='w')

        # Row 8 widgets (Start and Stop buttons)
        start_button = tk.Button(self, text="Confirm\nConfiguration", width=15, height=3, bg="green", command=(submit_form))
        stop_button = tk.Button(self, text="STOP", width=7, height=3, bg="red", command=stopProgram)
        start_button.grid(row=8, column=1, pady=(60,0))
        stop_button.grid(row=8, column=3, pady=(60,0))

# open weather table tab 
class Page2(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        templabel = tk.Label(self, text="Temperature", font=("segoe", 10, "bold"))
        templabel.grid(row=0, column=0, columnspan=4, pady=(10, 0), sticky="w")

        global currenttemp_entry, currenthumidity_entry, currentdewpt_entry
        global maxtemp_entry, maxhumidity_entry, maxdewpt_entry
        global minimumtemp_entry, minimumhumidity_entry, minimumdewpt_entry
        global temp3hr_entry, temp6hr_entry, temp9hr_entry, temp12hr_entry, temp15hr_entry, temp18hr_entry, temp21hr_entry, temp24hr_entry
        global humid3hr_entry, humid6hr_entry, humid9hr_entry, humid12hr_entry, humid15hr_entry, humid18hr_entry, humid21hr_entry, humid24hr_entry
        global dewpt3hr_entry, dewpt6hr_entry, dewpt9hr_entry, dewpt12hr_entry, dewpt15hr_entry, dewpt18hr_entry, dewpt21hr_entry, dewpt24hr_entry
        global currententhalpy_entry, maxenthalpy_entry, minimumenthalpy_entry, enthalpy3hr_entry, enthalpy6hr_entry, enthalpy9hr_entry, enthalpy12hr_entry
        global enthalpy15hr_entry, enthalpy18hr_entry, enthalpy21hr_entry, enthalpy24hr_entry

 # Create labels for the rows (temperature)
        temprow_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(temprow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=0, sticky="w", pady=(10, 0), padx=10)


        # creation of temperature entry boxes    
        currenttemp_entry = tk.Entry(self, width=12)
        currenttemp_entry.grid(row=1, column=1, pady=(10,0))
        maxtemp_entry = tk.Entry(self, width=12)
        maxtemp_entry.grid(row=2, column=1, pady=(10,0))
        minimumtemp_entry = tk.Entry(self, width=12)
        minimumtemp_entry.grid(row=3, column=1, pady=(10,0))
        temp3hr_entry = tk.Entry(self, width=12)
        temp3hr_entry.grid(row=4, column=1, pady=(10,0))
        temp6hr_entry = tk.Entry(self, width=12)
        temp6hr_entry.grid(row=5, column=1, pady=(10,0))
        temp9hr_entry = tk.Entry(self, width=12)
        temp9hr_entry.grid(row=6, column=1, pady=(10,0))
        temp12hr_entry = tk.Entry(self, width=12)
        temp12hr_entry.grid(row=7, column=1, pady=(10,0))
        temp15hr_entry = tk.Entry(self, width=12)
        temp15hr_entry.grid(row=8, column=1, pady=(10,0))
        temp18hr_entry = tk.Entry(self, width=12)
        temp18hr_entry.grid(row=9, column=1, pady=(10,0))
        temp21hr_entry = tk.Entry(self, width=12)
        temp21hr_entry.grid(row=10, column=1, pady=(10,0))
        temp24hr_entry = tk.Entry(self, width=12)
        temp24hr_entry.grid(row=11, column=1, pady=(10,0))


        # Create labels for humidity
        humidity_label = tk.Label(self, text="Humidity", font=("segoe", 10, "bold"))
        humidity_label.grid(row=0, column=2, pady=(10, 0), padx=10)

        # Create labels for the rows (humidity)
        humrow_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(humrow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=2, sticky="w", pady=(10, 0), padx=10)

        # creation of humidity entry boxes
        currenthumidity_entry = tk.Entry(self, width=12)
        currenthumidity_entry.grid(row=1, column=3, pady=(10,0))
        maxhumidity_entry = tk.Entry(self, width=12)
        maxhumidity_entry.grid(row=2, column=3, pady=(10,0))
        minimumhumidity_entry = tk.Entry(self, width=12)
        minimumhumidity_entry.grid(row=3, column=3, pady=(10,0))
        humid3hr_entry = tk.Entry(self, width=12)
        humid3hr_entry.grid(row=4, column=3, pady=(10,0))
        humid6hr_entry = tk.Entry(self, width=12)
        humid6hr_entry.grid(row=5, column=3, pady=(10,0))
        humid9hr_entry = tk.Entry(self, width=12)
        humid9hr_entry.grid(row=6, column=3, pady=(10,0))
        humid12hr_entry = tk.Entry(self, width=12)
        humid12hr_entry.grid(row=7, column=3, pady=(10,0))
        humid15hr_entry = tk.Entry(self, width=12)
        humid15hr_entry.grid(row=8, column=3, pady=(10,0))
        humid18hr_entry = tk.Entry(self, width=12)
        humid18hr_entry.grid(row=9, column=3, pady=(10,0))
        humid21hr_entry = tk.Entry(self, width=12)
        humid21hr_entry.grid(row=10, column=3, pady=(10,0))
        humid24hr_entry = tk.Entry(self, width=12)
        humid24hr_entry.grid(row=11, column=3, pady=(10,0))


        # create labels for rows (dew point)
        dewpt_label = tk.Label(self, text="Dew Point", font=("segoe", 10, "bold"))
        dewpt_label.grid(row=0, column=4, pady=(10, 0), padx=10)

        dewpt_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(dewpt_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=4, sticky="w", pady=(10, 0), padx=10)

        # create boxes for dew pt.
        currentdewpt_entry = tk.Entry(self, width=12)
        currentdewpt_entry.grid(row=1, column=5, pady=(10,0))
        maxdewpt_entry = tk.Entry(self, width=12)
        maxdewpt_entry.grid(row=2, column=5, pady=(10,0))
        minimumdewpt_entry = tk.Entry(self, width=12)
        minimumdewpt_entry.grid(row=3, column=5, pady=(10,0))
        dewpt3hr_entry = tk.Entry(self, width=12)
        dewpt3hr_entry.grid(row=4, column=5, pady=(10,0))
        dewpt6hr_entry = tk.Entry(self, width=12)
        dewpt6hr_entry.grid(row=5, column=5, pady=(10,0))
        dewpt9hr_entry = tk.Entry(self, width=12)
        dewpt9hr_entry.grid(row=6, column=5, pady=(10,0))
        dewpt12hr_entry = tk.Entry(self, width=12)
        dewpt12hr_entry.grid(row=7, column=5, pady=(10,0))
        dewpt15hr_entry = tk.Entry(self, width=12)
        dewpt15hr_entry.grid(row=8, column=5, pady=(10,0))
        dewpt18hr_entry = tk.Entry(self, width=12)
        dewpt18hr_entry.grid(row=9, column=5, pady=(10,0))
        dewpt21hr_entry = tk.Entry(self, width=12)
        dewpt21hr_entry.grid(row=10, column=5, pady=(10,0))
        dewpt24hr_entry = tk.Entry(self, width=12)
        dewpt24hr_entry.grid(row=11, column=5, pady=(10,0))

        # create labels for rows (enthalpy point)
        enth_label = tk.Label(self, text="Enthalpy", font=("segoe", 10, "bold"))
        enth_label.grid(row=0, column=6, pady=(10, 0), padx=10)

        enth_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(enth_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=6, sticky="w", pady=(10, 0), padx=10)

        currententhalpy_entry = tk.Entry(self, width=12)
        currententhalpy_entry.grid(row=1, column=7, pady=(10,0))
        maxenthalpy_entry = tk.Entry(self, width=12)
        maxenthalpy_entry.grid(row=2, column=7, pady=(10,0))
        minimumenthalpy_entry = tk.Entry(self, width=12)
        minimumenthalpy_entry.grid(row=3, column=7, pady=(10,0))
        enthalpy3hr_entry = tk.Entry(self, width=12)
        enthalpy3hr_entry.grid(row=4, column=7, pady=(10,0))
        enthalpy6hr_entry = tk.Entry(self, width=12)
        enthalpy6hr_entry.grid(row=5, column=7, pady=(10,0))
        enthalpy9hr_entry = tk.Entry(self, width=12)
        enthalpy9hr_entry.grid(row=6, column=7, pady=(10,0))
        enthalpy12hr_entry = tk.Entry(self, width=12)
        enthalpy12hr_entry.grid(row=7, column=7, pady=(10,0))
        enthalpy15hr_entry = tk.Entry(self, width=12)
        enthalpy15hr_entry.grid(row=8, column=7, pady=(10,0))
        enthalpy18hr_entry = tk.Entry(self, width=12)
        enthalpy18hr_entry.grid(row=9, column=7, pady=(10,0))
        enthalpy21hr_entry = tk.Entry(self, width=12)
        enthalpy21hr_entry.grid(row=10, column=7, pady=(10,0))
        enthalpy24hr_entry = tk.Entry(self, width=12)
        enthalpy24hr_entry.grid(row=11, column=7, pady=(10,0))

        # create clear button
        clear_button = tk.Button(self, text="Clear Data", width=10, height=3, bg="grey", command=(clearOpenWeatherBoxes))
        clear_button.grid(row=12, column=7, pady=(10,0))

        


# Page 3 class defines the 24 hour open weather trend graph
class Page3(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        
        # Create a figure and plot with a specific size
        self.fig = plt.Figure(figsize=(0, 1))  # Adjust the size as needed
        self.ax = self.fig.add_subplot(111)
        self.times = ["Current", "+3hr", "+6hr", "+9hr", "+12hr", "+15hr", "+18hr", "+21hr", "+24hr"]
        self.old_label = None  # To keep track of the old label

        # Embed the plot in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


        # Schedule the plot to update every minute (60000 milliseconds)
        self.update_plot_every_minute()

        # Connect the click event to the callback function
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def update_plot(self):
        # Clear the previous plot
        self.ax.clear()

        # Update the data
        readWeatherXML()
        self.temperatures = [current_temperature, temp_3, temp_6, temp_9, temp_12, temp_15, temp_18, temp_21, temp_24]
        self.humidities = [current_humidity, humid_3, humid_6, humid_9, humid_12, humid_15, humid_18, humid_21, humid_24]
        self.dew_points = [current_dewpt, dew_3, dew_6, dew_9, dew_12, dew_15, dew_18, dew_21, dew_24]
        self.enthalpies = [current_enthalpy, enth_3, enth_6, enth_9, enth_12, enth_15, enth_18, enth_21, enth_24]

        # Plot the updated data
        self.ax.plot(self.times, self.temperatures, label='Temperature (°C)', marker='o')
        self.ax.plot(self.times, self.humidities, label='Humidity (%)', marker='o')
        self.ax.plot(self.times, self.dew_points, label='Dew Point (°C)', marker='o')
        self.ax.plot(self.times, self.enthalpies, label='Enthalpy (kJ/kg)', marker='o')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.legend(fontsize='small')

        # Set y-axis limits and ticks to increments of -10 up to 100
        self.ax.set_ylim(-10, 100)
        self.ax.set_yticks(range(-10, 101, 10))

        # Add a title to the plot
        self.ax.set_title("Open Weather Map API 24 Hour Trend")

        # Redraw the canvas
        self.canvas.draw()

    def update_plot_every_minute(self):
        # Start a new thread to update the plot
        threading.Thread(target=self.update_plot_thread).start()
        self.after(60000, self.update_plot_every_minute)  # Schedule the update every 60000 milliseconds (1 minute)

    def update_plot_thread(self):
        # Update the plot in a separate thread
        self.update_plot()

    def on_click(self, event):
        # Convert time labels to numerical values for comparison
        time_mapping = {label: idx for idx, label in enumerate(self.times)}
        if event.inaxes is not None:
            for line in self.ax.get_lines():
                xdata, ydata = line.get_data()
                label = line.get_label()
                for x, y in zip(xdata, ydata):
                    if abs(time_mapping[x] - event.xdata) < 0.5 and abs(y - event.ydata) < 1:
                        # Display the value on the screen
                        self.display_value(label, y)

    def display_value(self, y, label):
        # Remove the old label if it exists
        if self.old_label:
            self.old_label.destroy()

        # Create a new label to display the value
        self.old_label = tk.Label(self, text=f"{y}: {label}", font=("segoe", 12))
        self.old_label.pack()
 

# page 4 class includes the open meteo (BOM) table data
class Page4(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        global BOMcurrenttemp_entry, BOMcurrenthumidity_entry, BOMcurrentdewpt_entry
        global BOMmaxtemp_entry, BOMmaxhumidity_entry, BOMmaxdewpt_entry
        global BOMminimumtemp_entry, BOMminimumhumidity_entry, BOMminimumdewpt_entry
        global BOMtemp3hr_entry, BOMtemp6hr_entry, BOMtemp9hr_entry, BOMtemp12hr_entry, BOMtemp15hr_entry, BOMtemp18hr_entry, BOMtemp21hr_entry, BOMtemp24hr_entry
        global BOMhumid3hr_entry, BOMhumid6hr_entry, BOMhumid9hr_entry, BOMhumid12hr_entry, BOMhumid15hr_entry, BOMhumid18hr_entry, BOMhumid21hr_entry, BOMhumid24hr_entry
        global BOMdewpt3hr_entry, BOMdewpt6hr_entry, BOMdewpt9hr_entry, BOMdewpt12hr_entry, BOMdewpt15hr_entry, BOMdewpt18hr_entry, BOMdewpt21hr_entry, BOMdewpt24hr_entry
        global BOMcurrententhalpy_entry, BOMmaxenthalpy_entry, BOMminimumenthalpy_entry, BOMenthalpy3hr_entry, BOMenthalpy6hr_entry, BOMenthalpy9hr_entry, BOMenthalpy12hr_entry
        global BOMenthalpy15hr_entry, BOMenthalpy18hr_entry, BOMenthalpy21hr_entry, BOMenthalpy24hr_entry

 # Create labels for the rows (temperature)
        templabel = tk.Label(self, text="Temperature", font=("segoe", 10, "bold"))
        templabel.grid(row=0, column=0, columnspan=4, pady=(10, 0), sticky="w")
        temprow_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(temprow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=0, sticky="w", pady=(10, 0), padx=10)


        # creation of temperature entry boxes    
        BOMcurrenttemp_entry = tk.Entry(self, width=12)
        BOMcurrenttemp_entry.grid(row=1, column=1, pady=(10,0))
        BOMmaxtemp_entry = tk.Entry(self, width=12)
        BOMmaxtemp_entry.grid(row=2, column=1, pady=(10,0))
        BOMminimumtemp_entry = tk.Entry(self, width=12)
        BOMminimumtemp_entry.grid(row=3, column=1, pady=(10,0))
        BOMtemp3hr_entry = tk.Entry(self, width=12)
        BOMtemp3hr_entry.grid(row=4, column=1, pady=(10,0))
        BOMtemp6hr_entry = tk.Entry(self, width=12)
        BOMtemp6hr_entry.grid(row=5, column=1, pady=(10,0))
        BOMtemp9hr_entry = tk.Entry(self, width=12)
        BOMtemp9hr_entry.grid(row=6, column=1, pady=(10,0))
        BOMtemp12hr_entry = tk.Entry(self, width=12)
        BOMtemp12hr_entry.grid(row=7, column=1, pady=(10,0))
        BOMtemp15hr_entry = tk.Entry(self, width=12)
        BOMtemp15hr_entry.grid(row=8, column=1, pady=(10,0))
        BOMtemp18hr_entry = tk.Entry(self, width=12)
        BOMtemp18hr_entry.grid(row=9, column=1, pady=(10,0))
        BOMtemp21hr_entry = tk.Entry(self, width=12)
        BOMtemp21hr_entry.grid(row=10, column=1, pady=(10,0))
        BOMtemp24hr_entry = tk.Entry(self, width=12)
        BOMtemp24hr_entry.grid(row=11, column=1, pady=(10,0))


        # Create labels for humidity
        humidity_label = tk.Label(self, text="Humidity", font=("segoe", 10, "bold"))
        humidity_label.grid(row=0, column=2, pady=(10, 0), padx=10)

        # Create labels for the rows (humidity)
        humrow_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(humrow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=2, sticky="w", pady=(10, 0), padx=10)

        # creation of humidity entry boxes
        BOMcurrenthumidity_entry = tk.Entry(self, width=12)
        BOMcurrenthumidity_entry.grid(row=1, column=3, pady=(10,0))
        BOMmaxhumidity_entry = tk.Entry(self, width=12)
        BOMmaxhumidity_entry.grid(row=2, column=3, pady=(10,0))
        BOMminimumhumidity_entry = tk.Entry(self, width=12)
        BOMminimumhumidity_entry.grid(row=3, column=3, pady=(10,0))
        BOMhumid3hr_entry = tk.Entry(self, width=12)
        BOMhumid3hr_entry.grid(row=4, column=3, pady=(10,0))
        BOMhumid6hr_entry = tk.Entry(self, width=12)
        BOMhumid6hr_entry.grid(row=5, column=3, pady=(10,0))
        BOMhumid9hr_entry = tk.Entry(self, width=12)
        BOMhumid9hr_entry.grid(row=6, column=3, pady=(10,0))
        BOMhumid12hr_entry = tk.Entry(self, width=12)
        BOMhumid12hr_entry.grid(row=7, column=3, pady=(10,0))
        BOMhumid15hr_entry = tk.Entry(self, width=12)
        BOMhumid15hr_entry.grid(row=8, column=3, pady=(10,0))
        BOMhumid18hr_entry = tk.Entry(self, width=12)
        BOMhumid18hr_entry.grid(row=9, column=3, pady=(10,0))
        BOMhumid21hr_entry = tk.Entry(self, width=12)
        BOMhumid21hr_entry.grid(row=10, column=3, pady=(10,0))
        BOMhumid24hr_entry = tk.Entry(self, width=12)
        BOMhumid24hr_entry.grid(row=11, column=3, pady=(10,0))


        # create labels for rows (dew point)
        dewpt_label = tk.Label(self, text="Dew Point", font=("segoe", 10, "bold"))
        dewpt_label.grid(row=0, column=4, pady=(10, 0), padx=10)

        dewpt_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(dewpt_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=4, sticky="w", pady=(10, 0), padx=10)

        # create boxes for dew pt.
        BOMcurrentdewpt_entry = tk.Entry(self, width=12)
        BOMcurrentdewpt_entry.grid(row=1, column=5, pady=(10,0))
        BOMmaxdewpt_entry = tk.Entry(self, width=12)
        BOMmaxdewpt_entry.grid(row=2, column=5, pady=(10,0))
        BOMminimumdewpt_entry = tk.Entry(self, width=12)
        BOMminimumdewpt_entry.grid(row=3, column=5, pady=(10,0))
        BOMdewpt3hr_entry = tk.Entry(self, width=12)
        BOMdewpt3hr_entry.grid(row=4, column=5, pady=(10,0))
        BOMdewpt6hr_entry = tk.Entry(self, width=12)
        BOMdewpt6hr_entry.grid(row=5, column=5, pady=(10,0))
        BOMdewpt9hr_entry = tk.Entry(self, width=12)
        BOMdewpt9hr_entry.grid(row=6, column=5, pady=(10,0))
        BOMdewpt12hr_entry = tk.Entry(self, width=12)
        BOMdewpt12hr_entry.grid(row=7, column=5, pady=(10,0))
        BOMdewpt15hr_entry = tk.Entry(self, width=12)
        BOMdewpt15hr_entry.grid(row=8, column=5, pady=(10,0))
        BOMdewpt18hr_entry = tk.Entry(self, width=12)
        BOMdewpt18hr_entry.grid(row=9, column=5, pady=(10,0))
        BOMdewpt21hr_entry = tk.Entry(self, width=12)
        BOMdewpt21hr_entry.grid(row=10, column=5, pady=(10,0))
        BOMdewpt24hr_entry = tk.Entry(self, width=12)
        BOMdewpt24hr_entry.grid(row=11, column=5, pady=(10,0))

        # create labels for rows (enthalpy point)
        enth_label = tk.Label(self, text="Enthalpy", font=("segoe", 10, "bold"))
        enth_label.grid(row=0, column=6, pady=(10, 0), padx=10)

        enth_labels = ["Current:", "Max:", "Min:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(enth_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=6, sticky="w", pady=(10, 0), padx=10)

        BOMcurrententhalpy_entry = tk.Entry(self, width=12)
        BOMcurrententhalpy_entry.grid(row=1, column=7, pady=(10,0))
        BOMmaxenthalpy_entry = tk.Entry(self, width=12)
        BOMmaxenthalpy_entry.grid(row=2, column=7, pady=(10,0))
        BOMminimumenthalpy_entry = tk.Entry(self, width=12)
        BOMminimumenthalpy_entry.grid(row=3, column=7, pady=(10,0))
        BOMenthalpy3hr_entry = tk.Entry(self, width=12)
        BOMenthalpy3hr_entry.grid(row=4, column=7, pady=(10,0))
        BOMenthalpy6hr_entry = tk.Entry(self, width=12)
        BOMenthalpy6hr_entry.grid(row=5, column=7, pady=(10,0))
        BOMenthalpy9hr_entry = tk.Entry(self, width=12)
        BOMenthalpy9hr_entry.grid(row=6, column=7, pady=(10,0))
        BOMenthalpy12hr_entry = tk.Entry(self, width=12)
        BOMenthalpy12hr_entry.grid(row=7, column=7, pady=(10,0))
        BOMenthalpy15hr_entry = tk.Entry(self, width=12)
        BOMenthalpy15hr_entry.grid(row=8, column=7, pady=(10,0))
        BOMenthalpy18hr_entry = tk.Entry(self, width=12)
        BOMenthalpy18hr_entry.grid(row=9, column=7, pady=(10,0))
        BOMenthalpy21hr_entry = tk.Entry(self, width=12)
        BOMenthalpy21hr_entry.grid(row=10, column=7, pady=(10,0))
        BOMenthalpy24hr_entry = tk.Entry(self, width=12)
        BOMenthalpy24hr_entry.grid(row=11, column=7, pady=(10,0))

        # create clear button
        clear_button = tk.Button(self, text="Clear Data", width=10, height=3, bg="grey", command=(clearOpenMeteoBoxes))
        clear_button.grid(row=12, column=7, pady=(10,0))


# page 5 class includes the open meteo (BOM) line graph
class Page5(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # Create a figure and plot with a specific size
        self.fig = plt.Figure(figsize=(0,1))  # Adjust the size as needed
        self.ax = self.fig.add_subplot(111)
        self.times = ["Current", "+3hr", "+6hr", "+9hr", "+12hr", "+15hr", "+18hr", "+21hr", "+24hr"]
        self.old_label = None  # To keep track of the old label

        # Embed the plot in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Schedule the plot to update every minute (60000 milliseconds)
        self.update_plot_every_minute()

        # Connect the click event to the callback function
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def update_plot(self):
        # Clear the previous plot
        self.ax.clear()

        # Update the data displayed on the plot
        data = readOpenMeteoWeather()
        self.temperatures = [
            data["BOMtemp0h"], data["BOMtemp3h"], data["BOMtemp6h"], data["BOMtemp9h"],
            data["BOMtemp12h"], data["BOMtemp15h"], data["BOMtemp18h"], data["BOMtemp21h"], data["BOMtemp24h"]
        ]
        self.humidities = [
            data["BOMhumidity0h"], data["BOMhumidity3h"], data["BOMhumidity6h"], data["BOMhumidity9h"],
            data["BOMhumidity12h"], data["BOMhumidity15h"], data["BOMhumidity18h"], data["BOMhumidity21h"], data["BOMhumidity24h"]
        ]
        self.dew_points = [
            data["BOMdewpoint0h"], data["BOMdewpoint3h"], data["BOMdewpoint6h"], data["BOMdewpoint9h"],
            data["BOMdewpoint12h"], data["BOMdewpoint15h"], data["BOMdewpoint18h"], data["BOMdewpoint21h"], data["BOMdewpoint24h"]
        ]
        self.enthalpies = [
            data["BOMenthalpy0h"], data["BOMenthalpy3h"], data["BOMenthalpy6h"], data["BOMenthalpy9h"],
            data["BOMenthalpy12h"], data["BOMenthalpy15h"], data["BOMenthalpy18h"], data["BOMenthalpy21h"], data["BOMenthalpy24h"]
        ]

        # Plot the updated data
        self.ax.plot(self.times, self.temperatures, label='Temperature (°C)', marker='o')
        self.ax.plot(self.times, self.humidities, label='Humidity (%)', marker='o')
        self.ax.plot(self.times, self.dew_points, label='Dew Point (°C)', marker='o')
        self.ax.plot(self.times, self.enthalpies, label='Enthalpy (kJ/kg)', marker='o')
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Value')
        self.ax.legend(fontsize='small')

        # Set y-axis limits and ticks to increments of -10 up to 100
        self.ax.set_ylim(-10, 100)
        self.ax.set_yticks(range(-10, 101, 10))

        # Add a title to the plot
        self.ax.set_title("Open-Meteo API (BOM) 24 Hour Trend")

        # Redraw the canvas
        self.canvas.draw()

    def update_plot_every_minute(self):
        # Start a new thread to update the plot
        threading.Thread(target=self.update_plot_thread).start()
        self.after(60000, self.update_plot_every_minute)  # Schedule the update every 60000 milliseconds (1 minute)

    def update_plot_thread(self):
        # Update the plot in a separate thread
        self.update_plot()

    def on_click(self, event):
        # Convert time labels to numerical values for comparison
        time_mapping = {label: idx for idx, label in enumerate(self.times)}
        if event.inaxes is not None:
            for line in self.ax.get_lines():
                xdata, ydata = line.get_data()
                label = line.get_label()
                for x, y in zip(xdata, ydata):
                    if abs(time_mapping[x] - event.xdata) < 0.5 and abs(y - event.ydata) < 1:
                        # Display the value on the screen
                        self.display_value(label, y)

    def display_value(self, y, label):
        # Remove the old label if it exists
        if self.old_label:
            self.old_label.destroy()

        # Create a new label to display the value
        self.old_label = tk.Label(self, text=f"{y}: {label}", font=("segoe", 12))
        self.old_label.pack()

# enable buttons for tabs and placement 
class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)
        p3 = Page3(self)
        p4 = Page4(self)
        p5 = Page5(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p5.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        def show_page(page, button):
            # Show the selected page
            page.show()

            # Highlight the active button (change color)
            for btn in [b1, b2, b3, b4, b5]:
                btn.configure(bg='lightblue')  # Reset other buttons
            button.configure(bg='orange')  # Set active button color

            # Change Page 1 color to blue when another page is opened
            if page != p1:
                b1.configure(bg='lightblue')  # Set Page 1 color to blue

    # create TK buttons and assign functions to them
        b1 = tk.Button(buttonframe, text="Configuration", command=lambda: show_page(p1, b1), bg='orange')
        b2 = tk.Button(buttonframe, text="Source 1: Open Weather API", command=lambda: (show_page(p2, b2), runReadThread()) , bg='lightblue')
        b3 = tk.Button(buttonframe, text="Source 1: 24HR Trend", command=lambda: show_page(p3, b3), bg='lightblue')
        b4 = tk.Button(buttonframe, text="Source 2: Open-Meteo (BOM)", command=lambda: (show_page(p4, b4), runReadThread()), bg='lightblue')
        b5 = tk.Button(buttonframe, text="Source 2: 24HR Trend", command=lambda: show_page(p5, b5), bg='lightblue')

    # pack tab buttons and stack from the left
        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")
        b5.pack(side="left")

        p1.show()
        # Create the clock label
        global clock_label
        clock_label = tk.Label(self, font=("segoe", 10, 'bold'))
        clock_label.pack()

        # Start updating the time
        update_time()


    # Opens GUI window, configures size and front page widget packing
root = tk.Tk()
main_view = MainView(root)  # Create an instance of your MainView
main_view.pack(side="top", fill="both", expand=True)
root.geometry("700x500")
root.title("Weather API Fetching Virtual BACnet Device (V1.0)")
root.resizable(False, False)

# loads in the previous config settings except for the personal API key
loadSettingsXML()

if __name__ == "__main__":
    # will run license verification before window initialisation
    file_path = './nssm-2.24/appData.txt'
    key_multiplier = 263

    if not verifyKey(file_path, key_multiplier):
        sys.exit()


# updates the line graph plot
    def update():
        root.update_idletasks()
        root.update()
        root.after(10, update)  # Update every 10 seconds
    
    update()


    root.mainloop()
