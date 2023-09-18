import os
import sys
import pickle
import json

PARENT_DIRECTORY = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
sys.path.append(PARENT_DIRECTORY)

from observational_scheduler.obs_scheduler import target
from logger.astro_logger import astroLogger

def main():

    with open(f"{PARENT_DIRECTORY}/pickle/current_target.pickle", "rb") as file:
        current_target = pickle.load(file)

    with open(f"{PARENT_DIRECTORY}/pickle/system_info.pickle") as file:
        system_info = pickle.load(file)

    current_target = current_target.__dict__()
    
    allData = {**current_target, **system_info}
    print(allData)
    allDataJSON = json.dumps(allData)

    with open(f"{__file__}/json_data/target.json", "w") as file:
        file.write(allDataJSON)

if __name__ == "__main__":
    main()