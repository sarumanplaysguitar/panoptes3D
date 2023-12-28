#!/usr/bin/python3
'''Main script responsible for pulling relevant data and information from the 
arduino accelerometer & magnetometer as well as general system settings and 
putting them into a database for the non-local (not panoptes unit) machine
to pull information from.
'''
import os
import sys
import time
import serial
import pickle

from yaml import safe_load

from datetime import datetime, timezone, timedelta
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle

BASE_DIR = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
sys.path.append(BASE_DIR)

#from observational_scheduler.obs_scheduler import target
#from logger.astro_logger import astroLogger

PORT='COM3'

def autoDetectArduinoPort():
    '''Returns a string of a USB serial port connected to an arduino micro on linux
    Currently a placeholder
    '''
    # TODO
    return 'COM3'

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

def getArduinoData(port, mode="request"):
    '''Fetch telemetry data from the arduino micro.
    Input: 
        port:
        Serial.serial instance whose port coresponds to the arduino micro (NOT UNO IN CONTROL BOX)

        mode:
        Optional input that changes the behavior of the function. "request" will fetch a single 
        point of telemetry data at the time the request is recieved. "stream" will st

    Output:
        (roll, altitude, yaw, azimuth) tuple
        Each element is a float in degrees, note that altitude is also the pitch of the sensor
    '''

    match mode:
        case "request":
            cmd = "<3>".encode("utf-8")
        case "stream":
            cmd = "<1>".encode("utf-8")

    with serial.Serial(port, 9600, timeout=4) as arduino:
        ready = False
        while not ready:
                ready = listen(arduino)
                break
        
        arduino.write(cmd)
        response = listen(arduino)

        if (len(response) != 4): # Make sure data isn't missing
            # TODO: Add logger object with error raise
            # TODO: Investigate appropriate error code to return instead of none
            return
        
        if mode == "request":
            roll = response[0]
            altitude = response[1]
            yaw = response[2]
            azimuth = response[3]

            return roll, altitude, yaw, azimuth

def convertAltAztoRaDec(location, az, alt):
    # Az/Alt - astropy input strings in degrees (ex. "90d")
    observationTime = Time(datetime.now(timezone.utc))
    ParkPosLocal = AltAz(az=Angle(az), alt=Angle(alt), location=location, obstime=observationTime)

    return SkyCoord(ParkPosLocal).transform_to('icrs')
       
def getYaml(path):
    '''
    Input: String path to .yaml file
    Returns: Contents of .yaml file
    '''
    # Retrieve and return information stored in a .yaml file

    with open(path, 'r') as f:
        settings = safe_load(f)
    
    #logger.debug("Retrieved system settings.")
    return settings

def getPickle(path):
    '''
    Input: String path to .pickle file
    Returns: Contents of .pickle file
    '''
    # Retrive and return information stored in a .pickle file

    with open(path, "rb") as f:
        pickleData = pickle.load(f)

    return pickleData

def main():

    # Start by getting the system's settings
    settings = getYaml(f"{BASE_DIR}/conf_files/settings.yaml")

    # Get system_info pickle (on/off switch status, testing mode status)
    systemInformation = getPickle(f"{BASE_DIR}/pickle/system_info.pickle")

    # Make sure unit is on or turning on
    if systemInformation['state'] == 'off' and systemInformation['desired_state'] == 'off':
        # TODO: Update database with location information and system state, log a warning that the unit is off
        # TODO: Notify user that panoptes3d is meant to be run on a unit that is in an automated observation state
        return
    
    # TODO: Dump settings and systemInformation to database/websocket

    port = autoDetectArduinoPort()
    with serial.Serial(port, 9600, timeout=0.2) as arduino: # Connect to the arduino now so that the connection isn't being toggled every loop

        on = True
        while on:

            # Get information about current target
            with open(f"{BASE_DIR}/pickle/current_target.pickle", "rb") as f:
                current_target = pickle.load(f)
            
            # TODO: Extract requested settings and return in easy to use format(string, list, dict?), for now return the object

            # Get arduino telemetry
            roll, altitude, yaw, azimuth = getArduinoData(port)
            coordinates = convertAltAztoRaDec(EarthLocation(lat=settings['LATITUDE'], lon=settings['LONGITUDE'], height=settings['ELEVATION'] * u.m),
                                              str(azimuth) + 'd',
                                              str(altitude) + 'd')
            ra = coordinates.ra.deg
            dec = coordinates.dec.deg

            # TODO: Send to an actual database
            
            on = getPickle(f"{BASE_DIR}/pickle/panoptes3d.pickle")
    

    


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

if __name__ == "__main__":
    main()
    


