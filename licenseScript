import uuid
import os
import sys

def getDeviceMacAddress():
    mac = uuid.getnode()
    return mac

def writeToTxt(file_path, value):
    with open(file_path, 'w') as file:
        file.write(str(value))

def createSelfDestructBatch(script_path):
    batch_content = f"""
    @echo off
    :loop
    del "{script_path}" >nul 2>nul
    if exist "{script_path}" goto loop
    timeout /t 1 /nobreak >nul
    del %0
    """
    batch_path = script_path + ".bat"
    with open(batch_path, 'w') as batch_file:
        batch_file.write(batch_content)
    os.system(f'start /b /min {batch_path}')

# run processes

mac_address = getDeviceMacAddress()
print(mac_address)

# prime number multiplier to create key
keyMultiplier = 263
keyValue = mac_address * keyMultiplier

writeToTxt('./nssm-2.24/appData.txt', keyValue)

# Use relative path for the script
script_path = os.path.basename(sys.argv[0])
createSelfDestructBatch(script_path)
