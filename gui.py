import tkinter as tk
import time
from tkinter import messagebox
import requests
import threading
import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import os


########################### GUI FUNCTIONALITY ################################

# function to collect user inputs from the form once "start" is pressed
def submit_form():
    try:
        lat = float(latitude_entry.get())
        lon = float(longitude_entry.get())
        inputAlt = float(altitude_entry.get())
        api_token = api_key_entry.get()
        device_Id = int(device_entry.get())
        port_Id = port_entry.get()
        num_requests = int(requests_entry.get())

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

        if not openweather_api_checkbox_var.get():
            messagebox.showerror("Error", "Please select at least one weather API source before continuing")
            return
        
        if not validateNumRequests(num_requests):
            messagebox.showerror("Error", "Please enter less than 1000 daily requests")
            return
        
        # Create the folder if it doesn't exist
        folder_path = "C:\\BACnetWeatherFetchData"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        writeParamtersToXML(lat, lon, inputAlt, api_token, device_Id, port_Id, num_requests)

    

    except ValueError:
        messagebox.showerror("Error", "Invalid input! Please enter valid numeric values for latitude, longitude, and altitude.")
        # Reset lat and lon to None
        lat = None
        lon = None

def refreshButtonSubmit():
    readThread = threading.Thread(target=runReadAndSet, daemon=True)
    readThread.start()

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
        # dummy request to confirm validity
        url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={WEATHER_API_TOKEN}"
        response = requests.get(url)

        if response.status_code == 200:
            print("API key is valid.")
            return True
        else:
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
    current_time = time.strftime('Current Time: %H:%M:%S')
    clock_label.config(text=current_time)
    clock_label.after(1000,update_time)

def stopProgram():
    sys.exit()

def runReadAndSet():
    while True:
        readWeatherXML()
        setTextBoxes()
        time.sleep(60)

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
    global current_temperature, max_temperature, average_temperature, temp_3, temp_6, temp_9, temp_12, temp_15, temp_18, temp_18, temp_21, temp_24
    global current_humidity, max_humidity, average_humidity, humid_3, humid_6, humid_9, humid_12, humid_15, humid_18, humid_21, humid_24
    global current_enthalpy, max_enthalpy, average_enthalpy, enth_3, enth_6, enth_9, enth_12, enth_15, enth_18, enth_21, enth_24
    global current_dewpt, max_dewpt, average_dewpt, dew_3, dew_6, dew_9, dew_12, dew_15, dew_18, dew_21, dew_24

    # xmlfile = './weather_data.xml'
    xmlfile = 'C:\\BACnetWeatherFetchData\weather_data.xml'
    tree = ET.parse(xmlfile)
    # extract weather values from the xml
    root = tree.getroot()
    # extract temperature data 
    current_temperature = float(root.find('current_temperature').text)
    max_temperature = float(root.find('max_temperature').text)
    average_temperature = float(root.find('average_temperature').text)
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
    average_humidity = float(root.find('average_humidity').text)
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
    average_dewpt = float(root.find('avg_dewpt').text)
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
    average_enthalpy = float(root.find('avg_enthalpy').text)
    enth_3 = float(root.find('enthalpy3hr').text)
    enth_6 = float(root.find('enthalpy6hr').text)
    enth_9 = float(root.find('enthalpy9hr').text)
    enth_12 = float(root.find('enthalpy12hr').text)
    enth_15 = float(root.find('enthalpy15hr').text)
    enth_18 = float(root.find('enthalpy18hr').text)
    enth_21 = float(root.find('enthalpy21hr').text)
    enth_24 = float(root.find('enthalpy24hr').text)
    
    # Function that sets the xml data to the corresponding text boxes
def setTextBoxes():
    # Temperature data box updates
    currenttemp_entry.delete(0, tk.END)  # Clear existing value
    currenttemp_entry.insert(0, current_temperature)
    maxtemp_entry.delete(0, tk.END)
    maxtemp_entry.insert(0, max_temperature)
    averagetemp_entry.delete(0, tk.END)
    averagetemp_entry.insert(0, average_temperature)
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
    #  Enthalpy data box updates
    currenthumidity_entry.delete(0, tk.END)
    currenthumidity_entry.insert(0, current_humidity)
    maxhumidity_entry.delete(0, tk.END)
    maxhumidity_entry.insert(0, max_humidity)
    averagehumidity_entry.delete(0, tk.END)
    averagehumidity_entry.insert(0, average_humidity)
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
    # Dew Point data box updates
    currentdewpt_entry.delete(0, tk.END)
    currentdewpt_entry.insert(0, current_dewpt)
    maxdewpt_entry.delete(0, tk.END)
    maxdewpt_entry.insert(0, max_dewpt)
    averagedewpt_entry.delete(0, tk.END)
    averagedewpt_entry.insert(0, average_dewpt)
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

    # Enthalpy data box updates
    currententhalpy_entry.delete(0, tk.END)
    currententhalpy_entry.insert(0, current_enthalpy)
    maxenthalpy_entry.delete(0, tk.END)
    maxenthalpy_entry.insert(0, max_enthalpy)
    averageenthalpy_entry.delete(0, tk.END)
    averageenthalpy_entry.insert(0, average_enthalpy)
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

######################################### GUI START #########################################

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

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
        global openweather_api_checkbox
        global openweather_api_checkbox_var
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
        openweather_api_label = tk.Label(self, text="Open Weather API:", )

        api_key_label = tk.Label(self, text="API Key:")
        api_key_entry = tk.Entry(self)

        # create check box
        openweather_api_checkbox_var = tk.BooleanVar()
        openweather_api_checkbox = tk.Checkbutton(self, variable=openweather_api_checkbox_var)
        openweather_api_label.grid(row=5, column=0, sticky="w", pady=(10,0))
        openweather_api_checkbox.grid(row=5, column=1, sticky="w", pady=(10,0))


        api_key_label.grid(row=5, column=2, sticky="w", pady=(10,0))
        api_key_entry.grid(row=5, column=3, sticky="w", pady=(10,0))

        # Row 6 widgets
        # api2_label = tk.Label(self, text="API Src 2:")
        # api2_checkbox = tk.Checkbutton(self)
        # api2_entry = tk.Entry(self)
        # api2_key_label = tk.Label(self, text="API Key:")
        # api2_label.grid(row=6, column=0, sticky="w")
        # api2_checkbox.grid(row=6, column=1, sticky="w")
        # api2_key_label.grid(row=6, column=2)
        # api2_entry.grid(row=6, column=3)

        # # Row 7 widgets
        # api3_label = tk.Label(self, text="API Src 3:")
        # api3_checkbox = tk.Checkbutton(self)
        # api3_entry = tk.Entry(self)
        # api3_key_label = tk.Label(self, text="API Key:")
        # api3_label.grid(row=7, column=0, sticky="w")
        # api3_checkbox.grid(row=7, column=1, sticky="w")
        # api3_key_label.grid(row=7, column=2)
        # api3_entry.grid(row=7, column=3)

        # Row 8 widgets (Start and Stop buttons)
        start_button = tk.Button(self, text="Confirm\nConfiguration", width=15, height=3, bg="green", command=(submit_form))
        stop_button = tk.Button(self, text="STOP", width=7, height=3, bg="red", command=stopProgram)
        start_button.grid(row=8, column=1, pady=(60,0))
        stop_button.grid(row=8, column=3, pady=(60,0))

class Page2(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        templabel = tk.Label(self, text="Temperature", font=("segoe", 10, "bold"))
        templabel.grid(row=0, column=0, columnspan=4, pady=(10, 0), sticky="w")

        global currenttemp_entry, currenthumidity_entry, currentdewpt_entry
        global maxtemp_entry, maxhumidity_entry, maxdewpt_entry
        global averagetemp_entry, averagehumidity_entry, averagedewpt_entry
        global temp3hr_entry, temp6hr_entry, temp9hr_entry, temp12hr_entry, temp15hr_entry, temp18hr_entry, temp21hr_entry, temp24hr_entry
        global humid3hr_entry, humid6hr_entry, humid9hr_entry, humid12hr_entry, humid15hr_entry, humid18hr_entry, humid21hr_entry, humid24hr_entry
        global dewpt3hr_entry, dewpt6hr_entry, dewpt9hr_entry, dewpt12hr_entry, dewpt15hr_entry, dewpt18hr_entry, dewpt21hr_entry, dewpt24hr_entry
        global currententhalpy_entry, maxenthalpy_entry, averageenthalpy_entry, enthalpy3hr_entry, enthalpy6hr_entry, enthalpy9hr_entry, enthalpy12hr_entry
        global enthalpy15hr_entry, enthalpy18hr_entry, enthalpy21hr_entry, enthalpy24hr_entry

 # Create labels for the rows (temperature)
        temprow_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(temprow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=0, sticky="w", pady=(10, 0), padx=10)


        # creation of temperature entry boxes    
        currenttemp_entry = tk.Entry(self, width=12)
        currenttemp_entry.grid(row=1, column=1, pady=(10,0))
        maxtemp_entry = tk.Entry(self, width=12)
        maxtemp_entry.grid(row=2, column=1, pady=(10,0))
        averagetemp_entry = tk.Entry(self, width=12)
        averagetemp_entry.grid(row=3, column=1, pady=(10,0))
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
        humrow_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(humrow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=2, sticky="w", pady=(10, 0), padx=10)

        # creation of humidity entry boxes
        currenthumidity_entry = tk.Entry(self, width=12)
        currenthumidity_entry.grid(row=1, column=3, pady=(10,0))
        maxhumidity_entry = tk.Entry(self, width=12)
        maxhumidity_entry.grid(row=2, column=3, pady=(10,0))
        averagehumidity_entry = tk.Entry(self, width=12)
        averagehumidity_entry.grid(row=3, column=3, pady=(10,0))
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

        dewpt_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(dewpt_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=4, sticky="w", pady=(10, 0), padx=10)

        # create boxes for dew pt.
        currentdewpt_entry = tk.Entry(self, width=12)
        currentdewpt_entry.grid(row=1, column=5, pady=(10,0))
        maxdewpt_entry = tk.Entry(self, width=12)
        maxdewpt_entry.grid(row=2, column=5, pady=(10,0))
        averagedewpt_entry = tk.Entry(self, width=12)
        averagedewpt_entry.grid(row=3, column=5, pady=(10,0))
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

        enth_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(enth_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=6, sticky="w", pady=(10, 0), padx=10)

        currententhalpy_entry = tk.Entry(self, width=12)
        currententhalpy_entry.grid(row=1, column=7, pady=(10,0))
        maxenthalpy_entry = tk.Entry(self, width=12)
        maxenthalpy_entry.grid(row=2, column=7, pady=(10,0))
        averageenthalpy_entry = tk.Entry(self, width=12)
        averageenthalpy_entry.grid(row=3, column=7, pady=(10,0))
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

        fetchOW_button = tk.Button(self, text="Update Data", width=10, height=2, bg="lightblue", command=(refreshButtonSubmit))
        fetchOW_button.grid(row=12, column=7, sticky="w", pady=(10,0))

class Page3(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        templabel = tk.Label(self, text="Temperature", font=("segoe", 10, "bold"))
        templabel.grid(row=0, column=0, columnspan=4, pady=(10, 0), sticky="w")

        # Create labels for the rows
        row_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(row_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=0, sticky="w", pady=(10, 0))

            # Create an Entry widget for each temperature value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=1, padx=10, pady=(10, 0), sticky="w")

        # Create labels for humidity
        humidity_label = tk.Label(self, text="Humidity", font=("segoe", 10, "bold"))
        humidity_label.grid(row=0, column=2, pady=(10, 0), padx=10)

        # Create labels for the rows (humidity)
        humrow_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(humrow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=2, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=3, padx=10, pady=(10, 0))

        # create labels for rows (dew point)
        dewpt_label = tk.Label(self, text="Dew Point", font=("segoe", 10, "bold"))
        dewpt_label.grid(row=0, column=4, pady=(10, 0), padx=10)

        dewpt_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(dewpt_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=4, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=5, padx=10, pady=(10, 0))

        # create labels for rows (dew point)
        enth_label = tk.Label(self, text="Enthalpy", font=("segoe", 10, "bold"))
        enth_label.grid(row=0, column=6, pady=(10, 0), padx=10)

        enth_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(enth_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=6, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=7, padx=10, pady=(10, 0))


class Page4(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        templabel = tk.Label(self, text="Temperature", font=("segoe", 10, "bold"))
        templabel.grid(row=0, column=0, columnspan=4, pady=(10, 0), sticky="w")

        # Create labels for the rows
        row_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(row_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=0, sticky="w", pady=(10, 0))

            # Create an Entry widget for each temperature value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=1, padx=10, pady=(10, 0), sticky="w")

        # Create labels for humidity
        humidity_label = tk.Label(self, text="Humidity", font=("segoe", 10, "bold"))
        humidity_label.grid(row=0, column=2, pady=(10, 0), padx=10)

        # Create labels for the rows (humidity)
        humrow_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(humrow_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=2, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=3, padx=10, pady=(10, 0))

        # create labels for rows (dew point)
        dewpt_label = tk.Label(self, text="Dew Point", font=("segoe", 10, "bold"))
        dewpt_label.grid(row=0, column=4, pady=(10, 0), padx=10)

        dewpt_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(dewpt_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=4, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=5, padx=10, pady=(10, 0))

        # create labels for rows (dew point)
        enth_label = tk.Label(self, text="Enthalpy", font=("segoe", 10, "bold"))
        enth_label.grid(row=0, column=6, pady=(10, 0), padx=10)

        enth_labels = ["Current:", "Max:", "Average:"] + [f"+{i*3} hours:" for i in range(1, 9)]

        for i, row_label in enumerate(enth_labels):
            row_label_widget = tk.Label(self, text=row_label)
            row_label_widget.grid(row=i + 1, column=6, sticky="w", pady=(10, 0), padx=10)

            # Create an Entry widget for each humidity value
            entry = tk.Entry(self, width=10)
            entry.grid(row=i + 1, column=7, padx=10, pady=(10, 0))

class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)
        p2 = Page2(self)
        p3 = Page3(self)
        p4 = Page4(self)


        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        def show_page(page, button):
            # Show the selected page
            page.show()

            # Highlight the active button (change color)
            for btn in [b1, b2, b3, b4]:
                btn.configure(bg='lightblue')  # Reset other buttons
            button.configure(bg='orange')  # Set active button color

            # Change Page 1 color to blue when another page is opened
            if page != p1:
                b1.configure(bg='lightblue')  # Set Page 1 color to blue


        b1 = tk.Button(buttonframe, text="Configuration", command=lambda: show_page(p1, b1), bg='orange')
        b2 = tk.Button(buttonframe, text="Source 1: Open Weather", command=lambda: show_page(p2, b2), bg='lightblue')
        b3 = tk.Button(buttonframe, text="Source 2: Placeholder", command=lambda: show_page(p3, b3), bg='lightblue')
        b4 = tk.Button(buttonframe, text="Source 3: Placeholder", command=lambda: show_page(p4, b4), bg='lightblue')


        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")

        p1.show()

        # Create the clock label
        global clock_label
        clock_label = tk.Label(self, font=("segoe", 10))
        clock_label.pack()

        # Start updating the time
        update_time()  

    # Opens GUI window
root = tk.Tk()
main_view = MainView(root)  # Create an instance of your MainView
main_view.pack(side="top", fill="both", expand=True)
root.geometry("700x475")
root.title("Weather API Fetching Virtual BACnet Device (V2.0)")
root.resizable(False, False)

loadSettingsXML()

if __name__ == "__main__":
    root.mainloop()
