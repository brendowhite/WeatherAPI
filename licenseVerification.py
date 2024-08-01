import uuid 
import sys

def getMacAddress():
    mac = uuid.getnode()
    return mac

def readLicenseFile(file_path):
    with open(file_path, 'r') as file:
        value = int(file.read().strip())
        return value


def verifyKey(file_path, multiplier):
    stored_value = readLicenseFile(file_path)
    current_mac = getMacAddress()
    expected_value = current_mac * multiplier
    
    if stored_value == expected_value:
        print("Verification successful. The key matches.")
        return True
    else:
        print("Verification failed. The key does not match.")
        return False
    
# run verification script

file_path = './nssm-2.24/appData.txt'
key_multiplier = 263

if not verifyKey(file_path, key_multiplier):
    sys.exit("Exiting script due to failed verification.")
