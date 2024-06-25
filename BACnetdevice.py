import weakref
import BAC0
from bacpypes.basetypes import EngineeringUnits, DateTime
from bacpypes.primitivedata import CharacterString, Date, Time
import time

from BAC0.core.devices.local.models import (
    analog_input,
    datetime_value,
    character_string,
)
from BAC0.core.devices.local.object import ObjectFactory
from BAC0.core.devices.local.models import make_state_text

def start_device():
    print("Starting BACnet device")
    new_device = BAC0.lite(deviceId=10032)
    time.sleep(1)

    # Analog Values
    _new_objects = analog_input(
        instance=1,
        name="Current_Temp",
        description="Current Temperature in degC",
        presentValue=10,
        properties={"units": "degreesCelsius"},
    )
    _new_objects = analog_input(
        instance=2,
        name="Current_Pressure",
        description="Current Pressure in kPa",
        presentValue=100,
        properties={"units": "kilopascals"},
    )
    _new_objects = analog_input(
        instance=3,
        name="Dew Point",
        description="Dew Point Temperature",
        presentValue=50,
        properties={"units": "degreesCelsius"}
    )
    _new_objects = analog_input(
        instance=4,
        name="Enthalpy",
        description="Specific Enthalpy",
        presentValue=25,
        properties={"units":"kilojoulesPerKilogram"}
    )

    _new_objects.add_objects_to_application(new_device)
    return new_device

try:
    my_bacnet_device = start_device()
    while True:
        time.sleep(60)  # Wait for 60 seconds before starting a new device instance
except Exception as e:
    print(f"Error: {e}")
