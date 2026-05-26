############################################################
# Initialisation                                           #
############################################################

###### Import modules ###################################### 
import numpy as np
import time 
import board
import busio
import adafruit_ads1x15.ads1015 as ADS    #Folder "adafruit_ads1x15" must be in the same directory
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)     #For SCL and SDA pins on board
ads = ADS.ADS1015(i2c)                    #Input SCL and SDA pins to ADS1015 function


####### Define initial variables ###########################
sps = 250                                 #Samples per second
s_size = 100                              #Sample size
s_int = 1.00/sps                          #Sampling interval, units: seconds

############################################################
# Define functions to be used                              #
############################################################

####### I/O based on 07.1.1_ADC ############################
def analogRead():                         #Read ADC value, only from Chn 0
    chan = AnalogIn(ads, 0)          #Reading from Chn 0
    current = (chan.value,chan.voltage)   #Extract Digital Value and Voltage
    return (current[0],current[1])

####### Data logging from the chip #########################
def logdata(): 
    data = []                             #Empty list to store data
    startTime = time.time()
    t1 = startTime 
    t2 = t1 
    for x in range(0,s_size): 
        data.append(analogRead()[1])      #Extract Voltage values only
        while(t2-t1 < s_int):             #To delay the extraction of data
            t2 = time.time()
        t1 += s_int
    return(data) 

############################################################
# Python script for data acquisition                       #
############################################################

####### Read voltage #######################################
dataSamples = logdata()
volts = np.mean(dataSamples)
str_t = "{:10}{:10.5f}\n\n".format("Voltage =",volts)
print(str_t)
