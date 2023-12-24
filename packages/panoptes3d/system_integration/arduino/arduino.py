import serial
import numpy as np

import time

from math import atan2, asin, pi, sqrt, sin, cos, acos


PORT='COM3'

def listen(port):
    # Function listens for a response from the arduino and returns the requested data or the completion character
    output = str(port.readline().decode('utf-8'))
    output = output.replace("\r", "")
    output = output.replace("\n", "")
    if output.count("|") == 2:
        output = output.replace("|", "")
        output = output.replace("[", "")
        output = output.replace("]", "")
        if output.__contains__(","):
            csvData = list(filter(None, output.split(',')))
            response = []
            for entry in csvData:
                response.append(float(entry))

            return response
        elif output == "#":
            print("Recived command success character")
        elif output == "r":
            print("\nArduino setup complete. Ready for commands.")
            return True
        else:
            return output
        
    elif output.count("|") != 0 and output.count("|") != 2:
       print("Unexpected serial response.")
    
    else:
        print("Unexpected serial response. Possible Arduino serial communication timeout reached.")
        return None


with serial.Serial(PORT, 9600, timeout=0.2) as arduino:
    ready = False
    while not ready:
            ready = listen(arduino)
            break

    arduino.write("<2>".encode('utf-8'))
    while True:
        #cmd = input("CMD: ")
        arduino.write("<3>".encode('utf-8'))
        response = listen(arduino)
        #print(response)
        altitude = response[1]
        azimuth = response[3]

        print(round(altitude), round(azimuth))
        time.sleep(0.5)
    


