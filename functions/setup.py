import os
import sys
import json
def startSetup(configPath):
    print("Initiating installation setup")
    try:
        os.mkdir(os.path.expanduser(configPath))
    except Exception as e:
        print("An error ocurred while setting up the installation. " + str(e)) #This will be replaced with an actual error dialog
        sys.exit(1)

def genConfig(configPath):
    print("Generating config...")
    defaultConfig = {
        "configFlowFinished": "false"
    }
    try:
        with open(os.path.expanduser(configPath + "/config.json"), "a") as configFileEditable:
            json.dump(defaultConfig, configFileEditable, indent=4)
    except Exception as e:
        print(str(e) + " at genConfig") #Replace with dialog
        sys.exit(1)
    print("Config file generated in" + str(os.path.expanduser(configPath + "/config.json"))) # Replace with dialog