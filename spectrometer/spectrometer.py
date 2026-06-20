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
    return(data) 

def query():
    while True:
        dataSamples = logdata()
        v = np.mean(dataSamples)          #Voltage reading
        std_v = np.std(dataSamples)       #Standard deviation
        print(f"Voltage = {v:.5f}\n")

        query_str = input("Repeat recording? (y/N) : ").strip().lower()

        if query_str != "y":
            break
    return [v, std_v]


####### Logic for data acquisition #########################

def test(f, nData):
    input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    start_time = time.time()
    f.write(f"\n{'Time(s)':<10}{'Voltage(V)':<10}\n")                         #Add title of values on third row of file

    data = []
    for x in range(nData):
        dataSamples = logdata()
        x_time = time.time() - start_time  #Data for x-axis, time
        y_voltage = np.mean(dataSamples)   #Data for y-axis, voltage
        data.append((x_time,y_voltage))    #Data - x,y

        #Write x_time and y_voltage into log file
        line = f"{x_time:<10.2f}{y_voltage:<10.5f}\n"
        f.write(line)
        print(line)

    avg_voltage = np.mean([d[1] for d in data])
    print(f"Voltage(V) = {avg_voltage:.5f}")
    elapsed_time = time.time() - start_time
    print(f"Elapsed time = {elapsed_time:.2f} seconds")

    return data

def concentration_read(f, vdark, nData):
    start_time = time.time()
    input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    vblank = query()                       #Voltage and std reading of blank

    f.write(f"V_blank = {vblank[0]:.5f}\n") 
    f.write(f"{'Conc(mM)':<10}{'Absorbance':<12}{'V_sample(V)':<12}{'Std_Sample(V)':<14}\n") #Add headers
    
    data = []
    for x in range(nData):
        conc = float(input("What concentration (in mM) are you testing? : ")) #Data for x-axis, concentration
        input("Please insert the sample and press enter.")
        vsample = query()                  #Voltage and std reading of sample
        
        absorbance = np.log10((vblank[0] - vdark[0])/(vsample[0] - vdark[0])) #Data for y-axis, absorbance
        data.append((conc,absorbance)) #Data - x,y

        f.write(f"{conc:<10.6f}{absorbance:<12.5f}{vsample[0]:<12.5f}{vsample[1]:<14.5f}\n")      #Write concentration and absorbance into log file
        print(f"Conc = {conc:.6f}, V = {vsample[0]:.5f}, Abs = {absorbance:.5f}\n")
    
    elapsed_time = time.time() - start_time
    print(f"Elapsed time = {elapsed_time:.2f} seconds. Data recording has finished.")
    
    return data

def angular_read(f, vdark, nData):
    start_time = time.time()
    dgrate = float(input("What is the spacing of your diffraction grating in nm? : "))

    f.write(f"\n{'Wavelength(nm)':<15}{'Absorbance':<12}{'V_solvent(V)':<13}{'V_sample(V)':<12}{'Std_Sample(V)':<14}\n") #Add headers

    data = []
    for x in range(nData):
        angle = float(input("What angle are you testing? : "))  #Record angle from diffraction grating to detector
        input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
        vblank = query()                   #Voltage reading of blank
        
        input("Please insert a sample of your solution (the sample), then press enter.")
        vsample = query()                  #Voltage reading of sample
        
        wlength = np.abs(dgrate*np.sin(angle/360*2*np.pi))     #Data for x-axis, wavelength
        absorbance = np.log10((vblank[0] - vdark[0])/(vsample[0] - vdark[0])) #Data for y-axis, absorbance
        data.append((wlength,absorbance)) #Data - x,y

        f.write(f"{wlength:<15.2f}{absorbance:<12.5f}{vblank[0]:<13.5f}{vsample[0]:<12.5f}{vsample[1]:<14.5f}\n")  #Write wavelength and absorbance into log file
        print(f"Wavelength = {wlength:.2f}, V = {vsample[0]:.5f}, Abs = {absorbance:.5f}\n")

    elapsed_time = time.time() - start_time
    print(f"Elapsed time = {elapsed_time:.2f} seconds. Data recording has finished.")

    return data

def kinetic(f, vdark, nData):
    input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    start_time = time.time()
    vblank = query()

    f.write(f"V_blank = {vblank[0]:.5f}\n")
    f.write(f"{'Time(s)':<10}{'Absorbance':<12}{'V_sample(V)':<12}{'Std_Sample(V)':<14}\n") #Add headers

    input("Please load the reaction to follow, then press enter to begin recording the experiment.")
    expt_time = time.time()                #Starting time of experiment in seconds

    data = []
    for x in range(nData):
        dataSamples = logdata()
        current_time = time.time()         #Current time in seconds

        x_time = current_time - expt_time  #Data for x-axis, time since start of experiment
        absorbance = np.log10((vblank[0] - vdark[0])/(np.mean(dataSamples)-vdark[0])) #Data for y-axis, voltage
        data.append((x_time,absorbance)) #Data - x,y

        f.write(f"{x_time:<10.2f}{absorbance:<12.5f}{np.mean(dataSamples):<12.5f}{np.std(dataSamples):<14.5f}\n")      #Write time and absorbance into log file
        print(f"Time = {x_time:.2f}, Abs = {absorbance:.5f}")

    elapsed_time = time.time() - start_time
    print(f"Elapsed time = {elapsed_time:.2f} seconds. Data recording has finished.")

    return data


####### Exiting the script cleanly #########################

def exit_plot(event):
    if event.key in ['x', 'escape', 'q', 'enter']:  # press x, escape, q or enter to exit plot
        plt.close("all")

############################################################
# Python script for data acquisition                       #
############################################################

def main():
    ###### Name of file to be saved as #####################
    filename = input("Please enter your file name : ")


    ####### Type of experiment #############################
    # - Concentration experiment measures the absorbance of
    #   the sample at different concentrations.
    # - Angle experiment measures the absorbance of the
    #   sample at different angles.
    # - Kinetic experiment measures the absorbance of the
    #   sample as time progresses.

    while True:
        type_expt = input("Are you testing concentration(c), angle(a) or kinetic(k)? : ")
        if type_expt in ("a", "c", "k", "test", "q"):
            break
        print('Invalid input. Please enter a, c, k, or q to quit. : ')
    
    if type_expt == "q":
        print("Exiting script.")
        return
    

    ####### Dark voltage ###################################
    # The dark voltage measures the ambient voltage reading
    # from the photodiode when the light source is switched
    # off. This reading is deducted from the sample readings
    # to calibrate the sample reading.

    print("Before we start, a dark voltage is needed.")
    input("Please turn off the light source, then press enter.")

    if HARDWARE:
        vdark = query()         #Actual data
    else:
        vdark = [0.01,0.01]     #Mock value
    

    ####### Number of data points ##########################
    nData = int(input("How many samples are you testing? : "))


    #Saving the data
    f = open(filename+".log", 'w')             #Close file only after experiment
    f.write(f"V_dark = {vdark[0]:.5f}\n")     #Write vdark value into log file


    ###### Main logic ######################################
    graph_title = ()                           #For x- and y-axes labels
    if type_expt == "a":
        data = angular_read(f, vdark, nData)
        graph_title += ("Wavelength(nm)","Absorbance")
    
    elif type_expt == "c":
        data = concentration_read(f, vdark, nData)
        graph_title += ("Concentration(mM)","Absorbance")

    elif type_expt == "k":
        data = kinetic(f, vdark, nData)
        graph_title += ("Time(s)","Absorbance")

    elif type_expt == "test":
        data = test(f, nData)
        graph_title += ("Time(s)","Voltage(V)")
    
    f.close()                                  #Close log file


    ##### Plot data ########################################
    
    #Unpacking data (list of tuples)
    x = [d[0] for d in data] 
    y = [d[1] for d in data] 
    
    fig, ax = plt.subplots()
    ax.plot(x,y,'.-')
    ax.set_xlabel(graph_title[0])
    ax.set_ylabel(graph_title[1])

    plt.savefig(filename+".png")
    fig.canvas.mpl_connect('key_press_event', exit_plot)
    plt.show()


############################################################
# Running main                                             #
############################################################

if __name__ == "__main__":
    main()