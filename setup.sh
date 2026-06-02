#!/bin/bash
 
echo "Setting up project environments..."
  
# Spectrometer
echo "[1/2] Installing spectrometer dependencies..."
cd ~/RPi-project/spectrometer || { echo "ERROR: Could not find spectrometer folder."; exit 1; }
 
python3 -m venv --system-site-packages venv || { echo "ERROR: Failed to create venv for spectrometer."; exit 1; }
 
source venv/bin/activate || { echo "ERROR: Failed to activate venv for spectrometer."; exit 1; }
 
pip install -r spectrometer_reqs_lite.txt || { echo "ERROR: Failed to install spectrometer dependencies."; exit 1; }
 
deactivate

echo "Spectrometer done."

# Weather station
echo "[2/2] Installing weather station dependencies..."
cd ~/RPi-project/weather_station || { echo "ERROR: Could not find weather_station folder."; exit 1; }
 
python3 -m venv --system-site-packages venv || { echo "ERROR: Failed to create venv for weather station."; exit 1; }
 
source venv/bin/activate || { echo "ERROR: Failed to activate venv for weather station."; exit 1; }
 
pip install -r weather_station_reqs_lite.txt || { echo "ERROR: Failed to install weather station dependencies."; exit 1; }
 
deactivate

echo "Weather station done."

 
echo "Setup complete."