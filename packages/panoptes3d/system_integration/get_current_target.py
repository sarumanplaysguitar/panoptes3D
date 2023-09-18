import os
import sys
import pickle
import json

PARENT_DIRECTORY = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
sys.path.append(PARENT_DIRECTORY)

from observational_scheduler.obs_scheduler import target
from logger.astro_logger import astroLogger

def main():
    logger = astroLogger(enable_color=True)
    logger.info("Fetching current target and system state...")
    logger.debug("Accessing current_target.pickle")
    with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as file:
        current_target = pickle.load(file)
    logger.debug("Done")

    logger.debug("Accessing system_info.pickle")
    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle", "rb") as file:
        system_info = pickle.load(file)
    logger.debug("Done")
    logger.info("Fetch complete.")

    current_target = current_target.__dict__
    
    allData = {**current_target, **system_info}
    allDataJSON = json.dumps(allData)

    with open(f"{os.path.dirname(__file__)}/json_data/target.json", "w") as file:
        file.write(allDataJSON)
    logger.info(f"Wrote json data to {os.path.dirname(__file__)}/json_data/target.json")

if __name__ == "__main__":
    main()