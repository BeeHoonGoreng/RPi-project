<<<<<<< HEAD
# RPi Documentation
Ridhuan Syafiq

## Objectives

- Replicate spectrometer and weather station projects on RPi 5.

- Check hardware/software for any depreciation/incompatibility with
  RPi5.

- Repackage teaching materials.

- Get as many RPi running.

## Key differences between RPi 5 vs RPi 3

- Internet works fine with NUS_Guest. Need to use handphone for OTP,
  will give access for 5 days.

- RPi 5 does not support installation of packages system-wide,
  necessitates the use of virtual environments. (discussed below)

- 

## Protocol for setting up new RPis

1.  Download [Raspberry Pi
    Imager](https://www.raspberrypi.com/software/).

2.  Plug in microsd card into a USB reader and follow set-up
    instructions on the imager app.

3.  Specifications

    <table>
    <colgroup>
    <col style="width: 22%" />
    <col style="width: 77%" />
    </colgroup>
    <thead>
    <tr>
    <th>Setup steps</th>
    <th>Choice</th>
    </tr>
    </thead>
    <tbody>
    <tr>
    <td>Device</td>
    <td>Raspberry Pi 5</td>
    </tr>
    <tr>
    <td>OS</td>
    <td><p>Raspberry Pi OS (64-bit). Released 2026-04-21.</p>
    <p>64 bit is important for RPi5 compatibility.<br />
    Version is important for consistency. Might have to an additional step
    of downloading this particular image from archive if newer versions are
    released.</p></td>
    </tr>
    <tr>
    <td>Storage</td>
    <td>Select the USB reader</td>
    </tr>
    <tr>
    <td>Hostname</td>
    <td>***</td>
    </tr>
    <tr>
    <td>Localisation</td>
    <td>Capital city &gt; Singapore (Singapore)<br />
    Timezone &gt; Asia/Singapore<br />
    Keyboard layout &gt; us</td>
    </tr>
    <tr>
    <td>User</td>
    <td>Username &gt; pi<br />
    Password &gt; 12345</td>
    </tr>
    <tr>
    <td>Wi-Fi</td>
    <td><strong>OPTIONAL<br />
    </strong>SSID &gt; NUS_Guest</td>
    </tr>
    <tr>
    <td>Remote authentication/Raspberry Pi Connect</td>
    <td>Default settings (not activated)</td>
    </tr>
    </tbody>
    </table>

4.  This will wipe the sd card and automatically format to FAT32.

5.  Plug-and-play into the RPi 5.

6.  Go to terminal to check date and time.

    Check: `timedatectl`  
    Change: `sudo date -s "25 MAY 2026 11:37:00"` (change accordingly).

## Setting up virtual environments for each project

**One time set-up**

## Weather station

adafruit-dht is depreciated. need to update to
[adafruit-circuitpython-dht](https://github.com/adafruit/Adafruit_CircuitPython_DHT)

## Adjusted code

pi_spectroscopy_v3-2.py, line 28 to 31

``` python
# OLD

def analogRead():                         #Read ADC value, only from Chn 0
    chan = AnalogIn(ads, ADS.P0)          #Reading from Chn 0
    current = (chan.value,chan.voltage)   #Extract Digital Value and Voltage
    return (current[0],current[1])
  
# NEW

def analogRead():                         
    chan = AnalogIn(ads, 0)               #Change this line (manually set int=0)
    current = (chan.value,chan.voltage)   
    return (current[0],current[1])
```

## Misc. Notes

python and python3 both refer to the same path. is there a difference?

maybe make the code more idiot-proof (long-term)
=======
# RPi-project
test test
>>>>>>> 60b5d66116ffaa78f546040b6346623d78a45289
