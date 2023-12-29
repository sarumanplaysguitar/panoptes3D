#!/usr/bin/python3

def readPan3DPickle():

    with open(f"{BASE_DIR}/pickle/panoptes3d.pickle", "rb") as f:
        OnOff = pickle.load(f) # Bool

    return OnOff

def writePan3DPickle(OnOff):
    with open(f"{BASE_DIR}/pickle/panoptes3d.pickle", "wb") as f:
        pickle.dump(OnOff, f)

def main(args):

    OnOff = readPan3DPickle()

    if args.start:
        if OnOff:
            print("PANOPTES3D: Already running!")
            logger.error("Can't start, already running.")

        else:
            subprocess.Popen(["python3", f"{BASE_DIR}/packages/panoptes3d/system_integration/getData.py"])
            writePan3DPickle(True)
        

    if args.stop:

        writePan3DPickle(False)

        if OnOff:
            print("PANOPTES3D: Sending stop command.")
            logger.info("Sending stop command.")
        else:
            print("PANOPTES3D: Already off! Reset pickle to off state.")
            logger.info("Already off! Reset pickle to off state.")
    
    if args.upload:
        print("PANOPTES3D: Automatically uploading telemetry.ino...")

        os.system(f"python3 {BASE_DIR}/packages/panoptes3d/system_integration/install_arduino.py")
        

if __name__ == '__main__':
    import argparse
    import pickle
    import os
    import sys
    import subprocess

    BASE_DIR = os.path.dirname(__file__).replace("/user_scripts", "")
    sys.path.append(BASE_DIR)

    from logger.astro_logger import astroLogger
    logger = astroLogger(enable_color=True)

    parser = argparse.ArgumentParser(description="Manage the panoptes 3D package.", formatter_class=argparse.RawTextHelpFormatter)
    mutuallyExclusiveOnOff = parser.add_mutually_exclusive_group()
    
    mutuallyExclusiveOnOff.add_argument('--start', '-on', action='store_true', help="Turn on panoptes 3D, which will gather data from the system and connected sensors and send it to the remote client.")
    mutuallyExclusiveOnOff.add_argument('--stop', '--off', action='store_true', help="Turn off panoptes 3D, which will stop collecting sensor and system data.")
    mutuallyExclusiveOnOff.add_argument('--upload', '-u', action='store_true', help="Automatically upload arduino sketch to the arduino micro. Only works if there is one arduino micro currently plugged into the system.")
    args = parser.parse_args()
    main(args)
