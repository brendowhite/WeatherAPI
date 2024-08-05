import uuid
import tkinter as tk


def getDeviceMacAddress():
    mac = uuid.getnode()
    return mac

def readLicenseKey():
    try:
        with open("./nssm-2.24/license_key.txt", "r") as f:
            existing_license_key = f.read().strip()
        # Populate the license_entry box with the existing license key
            license_entry.delete(0, tk.END)
            license_entry.insert(0, existing_license_key)
    except FileNotFoundError:
        pass  # No existing license key found

def verifyKey():
    multiplier = 263
    entered_key = int(license_entry.get())
    current_mac = getDeviceMacAddress()
    expected_value = current_mac * multiplier
    real_value = entered_key
    
    if expected_value == real_value:
        # Write the verification key to a text file
        with open("./nssm-2.24/license_key.txt", "w") as f:
            f.write(str(real_value))
        # Display a green label
        result_label.config(text="Valid License", fg="green")
    else:
        # Display a red label
        result_label.config(text="Invalid License", fg="red")
        # Check if license_key.txt exists
        

# Create the GUI window
root = tk.Tk()
root.title("License Manager")

license_entry = tk.Entry(root)
license_entry.grid(row=2, column=1, sticky="w")

# Call the readLicenseKey function upon window execution
readLicenseKey()

mac_address = getDeviceMacAddress()

requestLabel = tk.Label(root, text="License Validation:", font=6)
requestLabel.grid(row=0, column=0, sticky="w")

label = tk.Label(root, text="Please send this code to ...@email.com:")
label.grid(row=1, column=0, sticky="w")

entry = tk.Entry(root)
entry.insert(0, mac_address)
entry.grid(row=1, column=1, sticky="w")

licenselabel = tk.Label(root, text="Enter License Key:")
licenselabel.grid(row=2, column=0, sticky="w")

confirm_button = tk.Button(root, bg='green', text="Validate License", command=verifyKey)
confirm_button.grid(row=3, column=1, pady=(10,0))

# Create a label to display the result
result_label = tk.Label(root, text="")
result_label.grid(row=3, column=0, pady=(10,0))

root.geometry("400x150")
root.resizable(False, False)
root.mainloop()
