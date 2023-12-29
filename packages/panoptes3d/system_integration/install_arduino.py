import os
import sys
import subprocess

sys.path.append(os.path.dirname(__file__).replace('/packages/panoptes3d/system_integration', ""))

from logger.astro_logger import astroLogger

# TODO: Add color print statements

def main():

    logger.info("Beginning auto-upload process for panoptes3d.")

    # Get information about connected arduinos and split the strings into a list (1 entry = 1 board)
    cmd = ['arduino-cli', 'board', 'list']
    response = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
    response = response.split('\n')

    print("Recieved port and board information from the arduino-CLI")
    logger.info("Recieved port and board information from the arduino-CLI")

    logger.info("Searching for arduino micro in the list of available arduino boards...")
    for line in response:
        if "arduino:avr:micro" in line:
            port = line.split(" ")[0]
            logger.info("Arduino micro found on port " + port)
            print("Found arduino micro on port " + port)
            
            # Use the arduino cli to compile and auto-upload the telemetry.ino sketch to the micro
            print("Starting upload process...")
            logger.info("Starting upload process...")
            parentDir = os.path.dirname(__file__)
            os.system("~/bin/arduino-cli core update-index")
            os.system("~/bin/arduino-cli core install arduino:avr")
            logger.info("Installing required arduino libraries.")
            print("Installing libraries...")
            os.system("~/bin/arduino-cli lib install 'Adafruit LSM303 Accel@1.1.8'")
            os.system("~/bin/arduino-cli lib install 'Adafruit LIS2MDL@2.1.7'")
            os.system("~/bin/arduino-cli lib install 'Adafruit Unified Sensor@1.1.14'")
            os.system(f"~/bin/arduino-cli compile -b arduino:avr:micro {parentDir}/arduino/telemetry")
            os.system(f"~/bin/arduino-cli upload -p {port} -b arduino:avr:micro {parentDir}/arduino/telemetry")

            print("Done!")
            logger.info("Done!")
            break

if __name__ == "__main__":
    logger = astroLogger(enable_color=True)
    main()
