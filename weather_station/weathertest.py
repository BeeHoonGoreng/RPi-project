#!/usr/bin/env python3 -u

############################################################
# Initialisation                                           #
############################################################

###### Import modules ######################################
import sys
import time, struct
from datetime import datetime

try:
    import serial
    import schedule
    import adafruit_dht
    import board

except ImportError as e:
    print(f"Certain packages not available : {e}")
    # sys.exit("Exiting script.")

############################################################
# CHANNEL CREATION OF HUMIDITY AND TEMPERATURE DHT22 SENSOR#
############################################################
DHT_PIN = 4
DHT_SENSOR = adafruit_dht.DHT22(board.D4)


############################################################
# CHANNEL CREATION OF NOVA PM SENSOR                       #
############################################################

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1
PERIOD_CONTINUOUS = 0

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
ser.open()
ser.flushInput()

byte, data = 0, ""

def read_response():
    byte = 0
    while byte != b"\xaa":
        byte = ser.read(size=1)

    d = ser.read(size=9)

    if DEBUG:
        dump(d, '< ')
    return byte + d

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = b"\xaa\xb4" + bytes([cmd])
    ret += bytes(data)
    ret += b"\xff\xff" + bytes([checksum]) + b"\xab"

    if DEBUG:
        dump(ret, '> ')
    return ret

def process_data(d):
    r = struct.unpack('<HHxxBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(d[2:8])%256
    return [pm25, pm10]

def cmd_query_data():
    ser.write(construct_command(CMD_QUERY_DATA))
    d = read_response()
    values = []
    if d[1:2] == b"\xc0":
        values = process_data(d)
    return values

def cmd_set_sleep(sleep):
    mode = 0 if sleep else 1
    ser.write(construct_command(CMD_SLEEP, [0x1, mode]))
    read_response()
    
def cmd_set_mode(mode=MODE_QUERY):
    ser.write(construct_command(CMD_MODE, [0x1, mode]))
    read_response()
    
def cmd_set_working_period(period):
    ser.write(construct_command(CMD_WORKING_PERIOD, [0x1, period]))
    read_response()

cmd_set_sleep(0)
cmd_set_working_period(PERIOD_CONTINUOUS)
cmd_set_mode(MODE_QUERY);

def fmt(value, unit):
    return f"{value:.2f} {unit}" if isinstance(value, (int, float)) else "ERR"


############################################################
# TESTING THE SENSORS                                      #
############################################################

##### INPUT ################################################

INTERVAL = 3 # seconds
N_READINGS = 20 # 1 minute

############################################################

print("Begin diagnosis.\n")
start_time = time.time()
print(f"Running {N_READINGS} readings over {N_READINGS * INTERVAL} seconds...\n")
print(f"{'#':<4} {'Time':<10} {'PM2.5':<8} {'PM10':<8} {'Temp':<8} {'Humidity':<10} {'Status'}")
print("-" * 65)

results = []
for i in range(N_READINGS):
    record = {"pm25" : None, "pm10" : None,
              "temp" : None, "humidity" : None,
              "dht_err": None, "pm_err": None}

    # Testing DHT22
    try:
        record["temp"]     = DHT_SENSOR.temperature
        record["humidity"] = DHT_SENSOR.humidity
    except Exception as e:
        record["dht_err"] = str(e)

    # Testing Nova sensor
    try:
        record["pm25"], record["pm10"] = cmd_query_data()
    except Exception as e:
        record["pm_err"] = str(e)

    results.append(record)

    # Test if None and formats to string
    t = fmt(record["temp"], "*C")
    h  = fmt(record["humidity"], "%")
    pm25 = fmt(record["pm25"], "µg")
    pm10 = fmt(record["pm10"], "µg")
    timestamp = time.strftime('%H:%M:%S', time.localtime())

    # Status logic
    status = []
    if record["dht_err"]: status.append(f"DHT:{record['dht_err']}")
    if record["pm_err"]:  status.append(f"PM:{record['pm_err']}")
    status_str = ", ".join(status) if status else "OK"

    print(f"{i+1:<4} {timestamp:<10} {pm25:>8} {pm10:>8} {t:<8} {h:>10} {status_str}")

    if i < N_READINGS - 1:
        time.sleep(INTERVAL)

elapsed_time = time.time() - start_time
dht_failures = sum(1 for r in results if r["dht_err"])
pm_failures =  sum(1 for r in results if r["pm_err"])

print("\n" + "=" * 65)
print("DIAGNOSIS")
print("=" * 65)

print(f"\nDHT22 - {N_READINGS - dht_failures}/{N_READINGS} OK")
if dht_failures > 0:
    print(f"\tWARNING : {dht_failures} failures. Sensor is not stable, check wiring.")
else:
    print("\tDHT22 OK!")

print(f"\nNova PM - {N_READINGS - pm_failures}/{N_READINGS} OK")
if pm_failures > 0:
    print(f"\tWARNING : {pm_failures} failures. Sensor is not stable, check usb port/connections.")
else:
    print("\tNova PM OK!")

print("\nOVERALL")

if dht_failures == 0 and pm_failures == 0:
    print("\tAll sensors good. Ready to begin weather.py")
    print("Goodbye! :)")

else:
    print("\tIssues were detected. Review warnings before continuing")