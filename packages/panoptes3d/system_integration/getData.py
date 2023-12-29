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
import subprocess

from yaml import safe_load

from datetime import datetime, timezone, timedelta
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, Angle

BASE_DIR = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
sys.path.append(BASE_DIR)

from observational_scheduler.obs_scheduler import target
from logger.astro_logger import astroLogger

def autoDetectArduinoPort():
    '''Returns a string of a USB serial port connected to an arduino micro on linux
    Currently a placeholder
    '''

    # Get information about connected arduinos and split the strings into a list (1 entry = 1 board)
    cmd = ['arduino-cli', 'board', 'list']
    response = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    response = response.split('\n')
    logger.info("Recieved port and board information from the arduino-CLI")

    # Find the entry corresponding to an arduino micro, and rip the serial port from it
    for line in response:
        if "arduino:avr:micro" in line:
            port = line.split(" ")[0]
            logger.debug("Arduino micro found on port " + port)
            return port

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
            logger.info(f"Recieved the following data requested by the command: {response}")

            return response
        elif output == "#":
            print("PANOPTES3D: Recived command success character")
            logger.info("Recieved successful command execution character from the Arduino.")
        elif output == "r":
            print("\nPANOPTES3D: Arduino setup complete. Ready for commands.")
            logger.info("Succesfully connected and initialized the Arduino micro.")
            return True
        else:
            return output
        
    elif output.count("|") != 0 and output.count("|") != 2:
       logger.error("Arduino serial communication error. Expected command response within two '|' characters. ")
       print("PANOPTES3D: Unexpected serial response.")
    
    else:
        logger.warn("Unexpected serial response. Possible Arduino serial communication timeout reached.")
        print("PANOPTES3D: Unexpected serial response. Possible Arduino serial communication timeout reached.")
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
            logger.debug("Telemetry fetch mode set to 'request'")
        case "stream":
            cmd = "<1>".encode("utf-8")
            logger.debug("Telemetry fetch mode set to 'stream'")

    if not port.is_open:
        port.open()
        
    port.write(cmd)
    logger.debug(f"Sent {cmd} to the arduino serial port.")
    response = listen(port)
    logger.debug(f"Recived {response} from the arduino serial port.")

    if (len(response) != 4): # Make sure data isn't missing
        logger.critical(f"Recieved incorrect length of data from the arduino micro. Expected 4 data entries, but recieved {len(response)}")
        # TODO: Investigate appropriate error code to return instead of none
        return
    
    if mode == "request":
        roll = response[0]
        altitude = response[1]
        yaw = response[2]
        azimuth = response[3]
        logger.info("Recieved and parsed telemetry data.")
        logger.debug(f"Recieved sensor data: {roll=} {altitude=} {yaw=} {azimuth=}")

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
        yamlContents = safe_load(f)
    
    logger.debug(f"Read the contents of yaml file: {path}")
    return yamlContents

def getPickle(path):
    '''
    Input: String path to .pickle file
    Returns: Contents of .pickle file
    '''
    # Retrive and return information stored in a .pickle file

    with open(path, "rb") as f:
        pickleData = pickle.load(f)

    logger.debug(f"Read the contents of pickle file {path}")
    return pickleData

def getData(location, port, getNonTelemetry=True):
    '''Returns all data available to panoptes3d when called.
    Inputs:
        location - An astropy.coordinates.EarthLocation instance 
            Represents the current location of the panoptes unit in terms of latitude, longitude, and elevation. Note that
            elevation requires an astropy.units definition in meters (denoted as units.m by astropy convention)
        port - Serial.serial instance 
            Port coresponds to the arduino micro in the camera box.
        getNonTelemetry - optional bool, default True
            Bool that can be used to exclude non-telemetry data from this functions output. This is included in case
            future changes to the pickle/yaml format change. Setting this to False is intended to be a fast, temporary
            work around to errors caused by formatting/name changes in core .yaml files.
    Output:
        data - dict
            A dictionary containing lots of information about the current system.
            Key:             Description:
            roll             roll in degrees about the sensor's x-axis
            altitude         pitch in degrees about the sensor's y-axis (is also altitude in the alt az coordinate frame)
            yaw              yaw in degrees about the sensor's z-axis
            azimuth          azimuth in degrees right of north, based off a tilt-compensated compass bearing (Calculation done on arduino)
            ra               right acension in degrees based off of the altitude and azimuth
            dec              declination in degrees based off of the altitude and azimuth
            sysState         current state of the automated observation mode. Is a string, either 'on' or 'off'
            sysDesiredState  desired state of the automated observation mode. It is a string, signaling if the unit is in the procces of turning 'on' or 'off'
            testingMode      currently not implemented, but will be a string for which hardware module is being tested. Current value = string: 'NotImplemented'
            mountState       currently not implemented, but will be a string with options such as 'slewing', 'tracking', 'home'. Current value = string: 'NotImplemented'
            targetName       The name of the current target the unit is trying to observe, is a user-entered string
            targetCmd        The currently stored command at the time of reading the pickle file. This controls the majority of system behaviors.
                             This is a quick overview of the strings and what they're values mean:
                             'slew to target' - system will try to slew to the current target
                             'park' - system will try to park the mount
                             'parked' - system will set this to the cmd variable once it is done parking
                             'emergency park' - currently not implemented, but system will send this command if camera thread has not finished in an expected time frame
                             'observation complete' - system sends this once cameras are done taking pictures
                             'take images' - system sends this after it has slewed to the target, at which point the cameras start taking images
            targetPosRa      The right ascension of the current target in HH MM SS as requested by the user (string)
            targetPosDec     The declination of the current target in DD MM SS as requested by the user (string)
            camSettings      Camera settings dictionary with keys for 'primary_cam' and 'secondary_cam', whose values 
                             are dicts with keys 'exposure_time'(seconds), 'num_captures', and 'take_images' bool
            targetNotes      A string entered by the user that is paired with the target.
    '''

    logger.info("Fetching all system data for panoptes3d...")

    if not port.is_open:
        port.open()

    logger.debug("Getting telemetry information from arduino micro...")
    roll, altitude, yaw, azimuth = getArduinoData(port)
    coordinates = convertAltAztoRaDec(location, str(azimuth) + 'd', str(altitude) + 'd')

    ra = coordinates.ra.deg
    dec = coordinates.dec.deg

    # Return the telemetry data if requested by getNonTelemetry option
    if not getNonTelemetry:
        data = {'roll': roll, 'altitude': altitude, 'yaw': yaw, 'azimuth': azimuth, 'ra': ra, 'dec': dec}
        logger.info("Telemetry data recived.")
        return data

    # Get information not related to telemetry from various pickle and yaml files
    systemInformation = getPickle(f"{BASE_DIR}/pickle/system_info.pickle")
    currentTarget = getPickle(f"{BASE_DIR}/pickle/current_target.pickle")

    # Make massive data dict
    data = {
        'roll': roll, 
        'altitude': altitude, 
        'yaw': yaw,
        'azimuth': azimuth, 
        'ra': ra, 
        'dec': dec,
        'sysState': systemInformation['state'],
        'sysDesiredState': systemInformation['desired_state'],
        'testingMode': 'NotImplemented', # Coming in 1.0 releases for mounts
        'mountState': 'NotImplemented', # Coming in 1.0 releases for mounts
        'targetName': currentTarget.name,
        'targetCmd': currentTarget.cmd,
        'targetPosRa': currentTarget.position['ra'],
        'targetPosDec': currentTarget.position['dec'],
        'camSettings': currentTarget.camera_settings,
        'targetNotes': currentTarget.observation_notes
        }

    logger.info("All data recieved for panoptes3d")
    return data

def updateDataBase(data):
    '''Updates database/sends the recieved data to a format where it can be accessed by a remote client
    '''
    print(data)

def main():

    print("PANOPTES3D: Started.")

    # Start by getting the system's settings
    settings = getYaml(f"{BASE_DIR}/conf_files/settings.yaml")
    unitLocation = EarthLocation(lat=settings['LATITUDE'], lon=settings['LONGITUDE'], height=settings['ELEVATION'] * u.m)
    # TODO: Dump settings to database/websocket

    port = autoDetectArduinoPort()
    with serial.Serial(port, 9600, timeout=4) as arduino: # Connect to the arduino now so that the connection isn't being toggled every loop

        data = {'sysState': 'on'} # needed in case the getData function is being run with getNonTelemetry=False
        on = True
        while on:

            data = getData(unitLocation, arduino)
            updateDataBase(data)
            
            on = getPickle(f"{BASE_DIR}/pickle/panoptes3d.pickle")

            if data['sysState'] == 'off':
                print("PANOPTES3D: The unit is turned off, lowering data polling rate to 5 minutes to save resources.")
                logger.info("Unit is turned off, lowering data polling rate to 5 minutes.")
                nextSensorPoll = datetime.now() + timedelta(minutes=5)
                while on:
                    if nextSensorPoll <= datetime.now():
                        break

                    on = getPickle(f"{BASE_DIR}/pickle/panoptes3d.pickle")

                    time.sleep(5)

            else:
                time.sleep(5)
    
    print("PANOPTES3D: Stopped.")

if __name__ == "__main__":
    logger = astroLogger(enable_color=True)
    main()
