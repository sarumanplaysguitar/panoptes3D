import os
import sys
import json

from yaml import safe_load

PARENT_DIRECTORY = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
sys.path.append(PARENT_DIRECTORY)

from logger.astro_logger import astroLogger

'''
When run on a system with moxa-pocs, this will find static system information and put it into system_info.json
'''
def main():
    logger = astroLogger(enable_color=True)
    logger.info("Fetching current system settings...")
    logger.debug("Accessing settings.yaml")
    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", "r") as file:
        settings = safe_load(file)
    logger.debug("Done")
    logger.info("Fetch complete")
    
    settingsJSON = json.dumps(settings)
    
    with open(f"{os.path.dirname(__file__)}/json_data/settings.json", "w") as file:
        file.write(settingsJSON)
    logger.info(f"Wrote json data to {os.path.dirname(__file__)}/json_data/settings.json")

if __name__ == "__main__":
    main()