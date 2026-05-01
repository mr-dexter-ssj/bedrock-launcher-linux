# This is main.py
# It's intended to detect if the welcome screen was shown and then launch the Installation flow or the Launcher itself
# The rest of the logic will be called from here to the respective functions in different files

import json
import os
from functions.setup import startSetup, genConfig

#Check if config dir exists & if config needs (re)generation
configPath = "~/.bedrocklauncher" #Remember to change this to the final brand name
if str(os.path.exists(os.path.expanduser(configPath))) == "False" :
    print("Doing startSetup")
    startSetup(configPath)

if str(os.path.isfile(os.path.expanduser(configPath + "/config.json"))) == "False" :
    print("Doing genConfig")
    genConfig(configPath)

# Check if the installation flow was finished
configJson = open(os.path.expanduser(configPath + "/config.json"))
configDict = json.loads(configJson)
if configDict["configFlowFinished"] == "false":
    #start config flow
    print("Should start config window")
else:
    #skip to launch()



