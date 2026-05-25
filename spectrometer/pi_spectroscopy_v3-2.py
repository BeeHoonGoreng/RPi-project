############################################################
# Initialisation                                           #
############################################################

###### Import modules ###################################### 
import matplotlib.pyplot as plt
import numpy as np
import time 


## MOCK DATA
try:
    import board
    import busio
    import adafruit_ads1x15.ads1015 as ADS    #Folder "adafruit_ads1x15" must be in the same directory
    from adafruit_ads1x15.analog_in import AnalogIn

    i2c = busio.I2C(board.SCL, board.SDA)     #For SCL and SDA pins on board
    ads = ADS.ADS1015(i2c)                    #Input SCL and SDA pins to ADS1015 function

    HARDWARE = True
    print("Hardware connected")
except Exception as e:
    HARDWARE = False
    print(f"{e}")

####### Define initial variables ###########################
sps = 250                                 #Samples per second
s_size = 100                              #Sample size
s_int = 1.00/sps                          #Sampling interval, units: seconds
nData = 20                                #Number of data points

############################################################
# Define functions to be used                              #
############################################################

####### I/O based on 07.1.1_ADC ############################
def analogRead():                         #Read ADC value, only from Chn 0
    if HARDWARE:
        chan = AnalogIn(ads, 0)          #Reading from Chn 0
        current = (chan.value,chan.voltage)   #Extract Digital Value and Voltage
    else:
        current = (512, np.random.normal(1.65, 0.1))
        
    return (current[0],current[1])

####### Data logging from the chip #########################
def query():
    while True:
        dataSamples = logdata()
        v = np.mean(dataSamples)          #Voltage reading
        std_v = np.std(dataSamples)       #Standard deviation
        print("Voltage = {:10.5f}\n".format(v))
        query_str = input("Proceed? (y/n) : ")
        if query_str == "y" or query_str == "Y":
            break
    return [v, std_v]

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

def test():
    yes = input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    start_time = time.time()
    title = "{:10}{:10}\n".format("Time(s)","Voltage(V)")
    f.write(title)                         #Add title of values on third row of file
    y_volt = []
    for x in range(0,nData):
        dataSamples = logdata()
        current_time = time.time()         #Current time in seconds
        x_time = current_time - start_time #Data for x-axis, time
        y_voltage = np.mean(dataSamples)   #Data for y-axis, voltage
        y_volt.append(y_voltage)
        str_t = "{:10.2f}{:10.5f}\n".format(x_time,y_voltage)
        f.write(str_t)                     #Write x_time and y_voltage into log file
        g.write(str_t)                     #Write x_time and y_voltage into tsv file
        print("{:10.2f}{:10.5f}\n".format(x_time,y_voltage))
    print("Voltage(V) = ", np.mean(y_volt))
    end_time = time.time()
    print("Elapsed time = {:6.2f} seconds".format(end_time-start_time))

def concentration_read():
    start_time = time.time()
    nData = int(input("How many samples are you testing? : "))
    yes = input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    vblank = query()                       #Voltage and std reading of blank
    f.write("V_blank = {:10.5f}\n\n".format(vblank[0]))
    f.write("{:10}{:12}{:12}{:14}\n".format("Conc(mM)","Absorbance", "V_sample(V)", "Std_Sample(V)")) #Add headers
    for x in range(0,nData):
        conc = float(input("What concentration (in mM) are you testing? : ")) #Data for x-axis, concentration
        yes = input("Please insert the sample and press enter.")
        vsample = query()                  #Voltage and std reading of sample
        absorbance = np.log10((vblank[0] - vdark[0])/(vsample[0] - vdark[0])) #Data for y-axis, absorbance
        str_t = "{:10.6f}{:12.5f}{:12.5f}{:14.5f}\n".format(conc, absorbance, vsample[0], vsample[1])
        f.write(str_t)                     #Write concentration and absorbance into log file
        g.write(str_t)                     #Write concentration and absorbance into tsv file
        print("Conc = {:10.6f}, V = {:8.5f}, Abs = {:9.5f}\n".format(conc, vsample[0], absorbance))
    end_time = time.time()
    print("Elapsed time = {:6.2f} seconds. Data recording has finished.".format(end_time-start_time))

def angular_read():
    start_time = time.time()
    nData = int(input("How many angles are you testing? : "))
    dgrate = float(input("What is the spacing of your diffraction grating in nm? : "))
    f.write("{:15}{:12}{:13}{:12}{:14}\n".format("Wavelength(nm)","Absorbance","V_solvent(V)","V_sample(V)","Std_Sample(V)")) #Add headers
    for x in range(0,nData):
        angle = float(input("What angle are you testing? : "))  #Record angle from diffraction grating to detector
        yes = input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
        vblank = query()                   #Voltage reading of blank
        yes = input("Please insert a sample of your solution (the sample), then press enter.")
        vsample = query()                  #Voltage reading of sample
        absorbance = np.log10((vblank[0] - vdark[0])/(vsample[0] - vdark[0])) #Data for y-axis, absorbance
        wlength = np.abs(dgrate*np.sin(angle/360*2*np.pi))     #Data for x-axis, wavelength
        str_t = "{:15.2f}{:12.5f}{:13.5f}{:12.5f}{:14.5f}\n".format(wlength, absorbance, vblank[0], vsample[0], vsample[1])
        f.write(str_t)                     #Write wavelength and absorbance into log file
        g.write(str_t)                     #Write wavelength and absorbance into tsv file
        print("Wavelength = {:5.2f}, V = {:8.5f}, Abs = {:9.5f}\n".format(wlength, vsample[0], absorbance))
    end_time = time.time()
    print("Elapsed time = {:6.2f} seconds. Data recording has finished.".format(end_time-start_time))

def kinetic():
    yes = input("Please insert a sample of solvent (the blank) and turn on the light source, then press enter.")
    start_time = time.time()
    vblank = query()
    f.write("V_blank = {:10.5f}\n\n".format(vblank[0]))
    f.write("{:10}{:12}{:12}{:14}\n".format("Time(s)","Absorbance","V_sample(V)","Std_Sample(V)")) #Add headers
    yes = input("Please load the reaction to follow, then press enter to begin recording the experiment.")
    expt_time = time.time()                #Starting time of experiment in seconds
    for x in range(0,nData):
        dataSamples = logdata()
        current_time = time.time()         #Current time in seconds
        x_time = current_time - expt_time  #Data for x-axis, time since start of experiment
        absorbance = np.log10((vblank[0] - vdark[0])/(np.mean(dataSamples)-vdark[0])) #Data for y-axis, voltage
        str_t = "{:10.2f}{:12.5f}{:12.5f}{:14.5f}\n".format(x_time, absorbance, np.mean(dataSamples), np.std(dataSamples))
        f.write(str_t)                     #Write time and absorbance into log file
        g.write(str_t)                     #Write time and absorbance into tsv file
        print("Time = {:6.2f}, Abs = {:9.5f}\n".format(x_time, absorbance))
    end_time = time.time()
    print("Elapsed time = {:6.2f} seconds. Data recording has finished.".format(end_time-start_time))

############################################################
# Python script for data acquisition                       #
############################################################

###### Name of file to be saved as ######################### 
filename = input("Please enter your file name : ")

####### Type of experiment #################################
"""
Concentration experiment measures the absorbance of the sample
at different concentrations.
Angle experiment measures the absorbance of the sample at
different angles.
Kinetic experiment measures the absorbance of the sample as
time progresses.
"""
type_expt = input("Are you testing concentration(c), angle(a) or kinetic(k)? : ")

####### Dark voltage #######################################
"""
The dark voltage measures the ambient voltage reading from the
photodiode when the light source is switched off. This reading
is deducted from the sample readings to calibrate the sample
reading.
"""
print("Before we start, a dark voltage is needed.")
yes = input("Please turn off the light source, then press enter.")
vdark = query()

# Save two files: .log for all the data, .tsv for data for graph plot
f = open(filename+".log", 'w')             #Close file only after experiment
g = open(filename+".tsv", 'w')
f.write("{:10}{:10.5f}\n".format("V_dark =",vdark[0])) #Write vdark value into log file

####### Main script ########################################
graph_title = ()                           #For x- and y-axes labels
if type_expt == "a":
    angular_read()
    graph_title += ("Wavelength(nm)","Absorbance")
elif type_expt == "c":
    concentration_read()
    graph_title += ("Concentration(mM)","Absorbance")
elif type_expt == "k":
    kinetic()
    graph_title += ("Time(s)","Absorbance")
elif type_expt == "test":
    test()
    graph_title += ("Time(s)","Voltage(V)")
else:
    print('No method specified!')
f.close()                                  #Close log file
g.close()                                  #Close tsv file

##### Plot data ############################################
data = np.loadtxt(filename+".tsv")

x = [] 
y = [] 

if np.shape(data) == (4,):
    x.append(data[0])
    y.append(data[1])
else:
    for i in range(0,len(data)): 
        x.append(data[i,0]) 
        y.append(data[i,1]) 
 
plt.plot(x,y,'.-')
plt.xlabel(graph_title[0]); plt.ylabel(graph_title[1])
plt.savefig(filename+".png")
plt.show()
