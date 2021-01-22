from datetime import datetime
import json
import os
import serial

UWB_SRC_ADDR = "5"
OUTFILE = os.path.join('rangelogs', datetime.now().strftime('%Y-%m-%d_%H_%M_%S') + '.json')

ser = serial.Serial('/dev/ttyS0', 115200, timeout=1)
print("Starting pi" + UWB_SRC_ADDR)
while True:
	timeStr = json.dumps(datetime.utcnow().isoformat()).strip('"')
        line = ser.readline()
	lineDict = line.split(',')
        if '#' not in line and len(lineDict) > 3:
            srcID = UWB_SRC_ADDR
            dstID = lineDict[0].strip()
            distance = lineDict[1].strip()
            rssi = lineDict[2].strip()
            counter = lineDict[3].strip()
            uwb_dict = {
                    'object_type': 'UWB',
                    'src': srcID,
                    'dst': dstID,
                    'distance': distance,
                    'ble_rssi': rssi,
                    'timestamp': timeStr,
                    'counter': counter
            }
            uwb_json = json.dumps(uwb_dict)
            print(uwb_json)
            with open(OUTFILE, 'a') as outfile:
                outfile.write(uwb_json)
                outfile.write(',\n')

