@echo off
SET "SERVICE_NAME=BACnetWeatherDevice"
SET "NSSM_PATH=%~dp0nssm-2.24\win64\nssm.exe"

:: Check if NSSM exists in the specified directory
IF NOT EXIST "%NSSM_PATH%" (
    echo NSSM executable not found in the specified directory.
    exit /b 1
)

:: Prompt for confirmation to stop and uninstall the service
SET /P CONFIRM=Are you sure you want to stop and uninstall the "%SERVICE_NAME%" service? (Y/N):
IF /I "%CONFIRM%" NEQ "Y" (
    echo Operation cancelled.
    exit /b 0
)

:: Stop the service
"%NSSM_PATH%" stop "%SERVICE_NAME%"
IF ERRORLEVEL 1 (
    echo Failed to stop the service "%SERVICE_NAME%".
    exit /b 1
)

:: Uninstall the service
"%NSSM_PATH%" remove "%SERVICE_NAME%" confirm
IF ERRORLEVEL 1 (
    echo Failed to uninstall the service "%SERVICE_NAME%".
    exit /b 1
)

echo Service "%SERVICE_NAME%" has been stopped and uninstalled.
