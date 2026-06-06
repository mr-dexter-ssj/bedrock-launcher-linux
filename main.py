# This is main.py
# It's intended to detect if the welcome screen was shown and then launch the Installation flow or the Launcher itself
# The rest of the logic will be called from here to the respective functions in different files

import json
import os
from src.functions.setup import *
from src.functions.first_launch import *

beLauncherVersion = "Alpha 0.1"
srcRoot = Path(__file__).resolve().parent
print(str(srcRoot))
configPath = os.path.expanduser("~/.bedrocklauncher") #Remember to change this to the final brand name
instancesDirectory = configPath + "/instances"
instancesDb = configPath + "/instances.json"
#Check if config dir exists & if config needs (re)generation
if str(os.path.exists(configPath)) == "False" :
    print("Doing startSetup")
    setup(configPath)

# Check if the installation flow was finished
installationFlowFile = "BLINSTALLDIRECTORY"
if str(os.path.exists(installationFlowFile)) == "False":
    print("Launching Wizard")
    firstLaunch(srcRoot, beLauncherVersion, configPath, instancesDirectory, instancesDb)
#else:
    #launcher()
