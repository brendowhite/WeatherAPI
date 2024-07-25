@echo off
SET "SERVICE_NAME=BACnetWeatherDevice"
SET "APPLICATION_PATH=%~dp0weatherFetch.exe"
SET "APPLICATION_DIR=%~dp0"
SET "NSSM_PATH=%~dp0nssm-2.24\win64\nssm.exe"

:: Check if NSSM exists in the specified directory
IF NOT EXIST "%NSSM_PATH%" (
    echo NSSM executable not found in the specified directory.
    exit /b 1
)

:: Install the service
"%NSSM_PATH%" install "%SERVICE_NAME%" "%APPLICATION_PATH%"
"%NSSM_PATH%" set "%SERVICE_NAME%" "%APPLICATION_DIR%"


:: Set additional parameters
"%NSSM_PATH%" set "%SERVICE_NAME%" AppExit Default Restart
"%NSSM_PATH%" set "%SERVICE_NAME%" DisplayName "BACnet Weather Device"
"%NSSM_PATH%" set "%SERVICE_NAME%" Description "This service fetches weather data for BACnet devices."
"%NSSM_PATH%" set "%SERVICE_NAME%" Start SERVICE_DELAYED_AUTO_START
"%NSSM_PATH%" set "%SERVICE_NAME%" DependOnService Tcpip
"%NSSM_PATH%" set "%SERVICE_NAME%" AppNoConsole 1
"%NSSM_PATH%" set "%SERVICE_NAME%" AppStopMethodConsole 30000

:: Start the service
"%NSSM_PATH%" start "%SERVICE_NAME%"