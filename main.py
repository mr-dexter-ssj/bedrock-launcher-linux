# This is main.py
# It's intended to detect if the welcome screen was shown and then launch the Installation flow or the Launcher itself
# The rest of the logic will be called from here to the respective functions in different files

import json
import os
from src.functions.setup import *
from src.functions.first_launch import *

beLauncherVersion = "Alpha 0.1"

#Check if config dir exists & if config needs (re)generation
configPath = os.path.expanduser("~/.bedrocklauncher") #Remember to change this to the final brand name
if str(os.path.exists(os.path.expanduser(configPath))) == "False" :
    print("Doing startSetup")
    setup(configPath)

# Check if the installation flow was finished
installationFlowFile = "BLINSTALLDIRECTORY"
if str(os.path.exists(installationFlowFile)) == "False":
    print("Launching Wizard")
    firstLaunch(beLauncherVersion, configPath)
#else:
    #launcher()
