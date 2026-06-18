############################################################
# Initialisation                                           #
############################################################

###### Import modules ###################################### 
import sys
import matplotlib.pyplot as plt
import numpy as np
import time 

###### Hardware initialisation #############################
# This script is designed to work on an RPi 5 with hardware
# connected over I2C. The required libraries (board, busio,
# adafruit_ads1x15) require hardware to function and is not
# useful on Windows.
#
# Hardware initialisation is wrapped in 2 try-except blocks
# to allow for development and testing on a Windows system,
# or without the need for hardware connection.
#
# 1. ImportError check - check for missing packages
#    (expected on Windows). 
#
# 2. Hardware connection check - runs if packages are ok.
#    This catches any I2C/ADS1015 connection failures
#    (bad wiring, wrong address etc).
#
# If hardware initialisation succeeds (normal function):
#   - HARDWARE is set to True
#   - Real measurements are taken
#
# If hardware initialsation fails:
#   - HARDWARE is set to False
#   - The user may continue to use fake/mock data
#   - The user can test changes to script without needing
#     the photodiode connected.
try:
    import board
    import busio
    import adafruit_ads1x15.ads1015 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    PACKAGES_OK = True

except ImportError as e:
    PACKAGES_OK = False
    print(f"Certain packages not available : {e}")

if PACKAGES_OK:
    try:
        i2c = busio.I2C(board.SCL, board.SDA)     #For SCL and SDA pins on board
        ads = ADS.ADS1015(i2c)                    #Input SCL and SDA pins to ADS1015 function
        HARDWARE = True
        print("Hardware connected")

    except Exception as e:
        print(f"Hardware connection failed: {e}")
        sys.exit("Exiting script.")
else:
    HARDWARE=False
    
    while True:
        response = input("Continue with fake data? [y/n] : " ).strip().lower()

        if response == "y":
            break
        else:
            sys.exit("Exiting script.")

####### Define initial variables ###########################
sps = 250                                 #Samples per second
s_size = 100                              #Sample size
s_int = 1.00/sps                          #Sampling interval, units: seconds

############################################################
# Define functions to be used                              #
############################################################

####### I/O based on 07.1.1_ADC ############################
# analogRead() will crash if HARDWARE = False and it somehow
# runs. tryanalog() guards it with the if clause, so these 2
# are linked

def analogRead():                               #Read ADC value, only from Chn 0
    while True:
        try:
            chan = AnalogIn(ads,0)              #Reading from Chn 0
            current = (chan.value,chan.voltage) #Extract Digital Value and Voltage
            return(current[0], current[1])      #Actual output
        
        except Exception as e:                  #If connection fails, it will prompt to retake reading
            print(f"Hardware read failed: {e}")
            input("Check connection and press enter to retry.")

####### Wrapper to substitute mock values ##################
def tryanalog():
    if HARDWARE:
        return analogRead()                      #Actual output
    else:
        return(512, np.random.normal(1.65, 0.1)) #Mock values

####### Data logging from the chip #########################
def logdata(): 
    data = []                             #Empty list to store data
    startTime = time.time()
    t1 = startTime 
    t2 = t1 
    for x in range(0,s_size): 
        data.append(tryanalog()[1])       #Extract Voltage values only
        while(t2-t1 < s_int):             #To delay the extraction of data
            t2 = time.time()
        t1 += s_int
    return(data)                          #Output is a list of s_size voltages 

############################################################
# Python script for data acquisition                       #
############################################################

####### Read voltage #######################################

def main():
    dataSamples = logdata()
    v = np.mean(dataSamples)
    print(f"Voltage = {v:.5f}\n")

############################################################
# Running main                                             #
############################################################

if __name__ == "__main__":
    main()
