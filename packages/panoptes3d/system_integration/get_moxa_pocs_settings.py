import os
import json

from yaml import safe_load

'''
When run on a system with moxa-pocs, this will find static system information and put it into system_info.json
'''
def main():
    # Static information is stored in settings.yaml
    PARENT_DIRECTORY = os.path.dirname(__file__).replace("/packages/panoptes3d/system_integration", "")
    with open(f"{PARENT_DIRECTORY}/conf_files/settings.yaml", "r") as file:
        settings = safe_load(file)
    
    settingsJSON = json.dumps(settings)
    
    with open(f"{__file__}/json_data/settings.json", "w") as file:
        file.write(settingsJSON)

if __name__ == "__main__":
    print(__file__)
    main()