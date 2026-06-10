import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, QThreadPool, QRunnable, QObject, Signal
import datetime
import subprocess
import os
import traceback
import sys
import tarfile
import shutil
import json

class WorkerSignals(QObject):
    finished = Signal(object)
    error = Signal(object)
    result = Signal(object)
    progress = Signal(tuple)

class Worker(QRunnable):
    def __init__(self, fn,  *args, **kwargs):
        super().__init__()
        self.signals = WorkerSignals()
        self.threadId = kwargs.get("thread_id", 0)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            self.signals.error.emit(e)
       

@Slot()
def install(window, configPath, instancesDirectory, instancesDb):
    threadId = 0
    threadCount = window.threadpool.maxThreadCount()
    errorList = []
    
    #####Misc functions#####
    ##Error handling
    def errorHandler(e):
        #Display error message (Not implemented)
        print("An error has ocurred: " + str(e))
        QApplication.quit()
    ##Printing logs to window.outputView
    def logResult(dataTuple):
        window.outputView.append(f"[INFO] {dataTuple[0]}")
    ###########################################################################################################

    #Configure starting date-time
    window.outputView.append(f"[{str(datetime.datetime.now())[:-7]}] {window.outputView.placeholderText()}")
    window.outputView.append(f"[DEBUG] Multithreading with maximum {threadCount} threads")

    #Check for umu-launcher
    window.outputView.append("Checking for umu-launcher")
    try:
        import umu
        umuVersion = umu.__version__
        window.outputView.append(f"Found umu-launcher version {umuVersion}")
    except Exception as e:
        window.outuptView.append("Failed umu-launcher check. The installer can't continue." + str(e))
        errorHandler(e)
    
    #Determine necessary files
    window.outputView.append("Determining necessary files...")
    xcurl = window.xcurlConsentCheck.isChecked()
    proxyPass = window.proxyPassConsentCheck.isChecked()
    educationEdition = window.educationConsentCheck.isChecked()
    if not window.pathFolderLineEdit.text() == "":
        createNewInstance = True
    else:
        createNewInstance = False
    window.outputView.append(f"XCurl: {xcurl}")
    window.outputView.append(f"ProxyPass: {proxyPass}")
    window.outputView.append(f"Education Edition: {educationEdition}")
    window.outputView.append(f"Create instance: {createNewInstance}")

    #Check JVM availability
    window.outputView.append("Checking for JVM...")
    try:
        subprocess.run(["java", "--version"], capture_output=False)
        window.outputView.append("Success!")
    except Exception as jvmCheckFailed:
       window.outputView.append("[WARNING] Java check failed:" + str(jvmCheckFailed))

    #####Configure the initial installation#####
    #Flow:
    # 1. Make instancesDirectory
    # 2. Get and freeze necessary data
    # 3. Copy necessary files and validate (threaded)
    #initialInstallationData -> contains data from the initial installation setup
    #setupInitialInstallation() -> copy and validate files
    #printResultProtonGDK() -> prints the result to the outputView text edit
    #setupInitialInstallationThreaded() -> spawns a new thread and runs setupInitialInstallation() there. (See the Worker() class on top of the file for more info)
    #Note: Many features are still unimplemented
    #Prepare the provided files
    window.outputView.append("Configuring first installation")
    os.mkdir(instancesDirectory)
        #Freeze the variables
    installSelectedFolder = window.pathFolderLineEdit.text()
    installName = window.nameLineEdit.text()
    installVersion = window.versionComboBox.currentText()

    initialInstallationData = {
        "selectedFolder": installSelectedFolder,
        "name": installName,
        "version": installVersion 
        #"icon": 
    }
    def setupInitialInstallation(initialInstallationData):
        destDir = f"{instancesDirectory}/{initialInstallationData['name']}/binaries"
        window.installWorker.signals.progress.emit((f"[DEBUG] destDir = {destDir}",))
        try:
            shutil.copytree(initialInstallationData["selectedFolder"], destDir)
        #except FileExistsError:
            #purgeInstallation()
        #    print("[WARNING] An error that was supposed to be handled was raised, but does not have any handling logic.")
        except Exception as e:
            errorHandler(e)
        
        #Validate that Minecraft.Windows.exe is present
        if not os.path.isfile(f"{destDir}/Minecraft.Windows.exe"):
            window.installWorker.signals.progress.emit(("[WARNING] Minecraft.Windows.exe binary not found in the initial installation. Reverting (Not implemented)",))
            #revertInstallation() -> add createNewInstance = False plz
            #########################window.installWorker.signals.error.emit("Installation of Minecraft binaries reverted because Minecraft.Windows.exe was not found.") #So far, errorOcurred does nothing, I have to find a way to send it back
        else:
            with open(instancesDb, "wt") as instancesJson:
                formattedData = {
                    "path": f"{instancesDirectory}/{initialInstallationData['name']}",
                    "version": installVersion
                    #"icon": icon
                }
                dataToWrite = {
                    initialInstallationData["name"]: formattedData
                }
                instancesJson.write(json.dumps(dataToWrite, indent=4))
                window.installWorker.signals.progress.emit((f"Installation metadata saved to {instancesDb}",))
            window.installWorker.signals.progress.emit((f"Configured installation {initialInstallationData['name']}",))
            window.installWorker.signals.finished.emit(downloadXCurlandCaCert)
    #def printResultSetupInitialInstallation(dataTuple):
    #    window.outputView.append(f"[INFO] {dataTuple[0]}")
    def setupInitialInstallationThreaded(fn):
        window.installWorker = Worker(fn, initialInstallationData)
        window.outputView.append(f"Installing {initialInstallationData["name"]}")
        window.threadpool.start(window.installWorker)
        #window.installWorker.signals.progress.connect(printResultSetupInitialInstallation)
        window.installWorker.signals.progress.connect(logResult)
        ###############window.installWorker.signals.error.connect(errorList.append)
    ###########################################################################################################

    #####Make "/tools/"#####
    toolsFolder = configPath + "/tools"
    if not os.path.exists(toolsFolder):
        os.mkdir(toolsFolder)
        window.outputView.append(f"Created directory {toolsFolder}")
    
    #####Download ProtonGDK#####
    #downloadProtonGDK() -> the main downloading logic
    #printResultProtonGDK() -> prints the result to the outputView text edit
    #downloadProtonGDKThreaded() -> spawns a new thread and runs downloadProtonGDK() there. (See the Worker() class on top of the file for more info)
    #Note: This downloads the latest fix of ProtonGDK (lucaspah fork) and extracts it. If needed, this can be changed to a .json database.
    def downloadProtonGDK(configPath):
        window.protonWorker.signals.progress.emit(("Downloading ProtonGDK",))
        protonGDKLink = "https://github.com/LukasPAH/GDK-Proton-Custom/releases/download/release-10-32-3/GDK-Proton10-32-Custom-3.tar.gz"
        protonGDKTarGz = requests.get(protonGDKLink)
        protonGDKFolder = toolsFolder + "/ProtonGDK/"

        if not os.path.exists(protonGDKFolder):
            os.mkdir(protonGDKFolder)

        open(os.path.expanduser(protonGDKFolder) + "ProtonGDK.tar.gz", 'wb').write(protonGDKTarGz.content)
        window.protonWorker.signals.progress.emit(("Finished downloading ProtonGDK",))

        window.protonWorker.signals.progress.emit(("Extracting ProtonGDK",))
        tarfileProtonGDK = tarfile.open(protonGDKFolder + "ProtonGDK.tar.gz")
        tarfileProtonGDK.extractall(protonGDKFolder + "ProtonGDK")
        tarfileProtonGDK.close()
        window.protonWorker.signals.progress.emit(("Configured ProtonGDK",))
    #def printResultProtonGDK(dataTuple):
    #    window.outputView.append(f"[INFO] {dataTuple[0]}")
    def downloadProtonGDKThreaded(fn):
        window.protonWorker = Worker(fn, configPath)
        window.threadpool.start(window.protonWorker)
        #window.protonWorker.signals.progress.connect(printResultProtonGDK)
        window.protonWorker.signals.progress.connect(logResult)
        window.protonWorker.signals.error.connect(errorHandler)
    ###########################################################################################################

    #####Download ProxyPass#####
    #downloadProxyPass() -> the main downloading logic
    #printResultProxyPass() -> prints the result to the outputView text edit
    #downloadProxyPassThreaded() -> spawns a new thread and runs downloadProxyPass() there. (See the Worker() class on top of the file for more info)
    def downloadProxyPass(configPath):
        #!!!!!!!!!!!!!PENDING: download the required proxypass according to the version of the first installation
        window.worker.signals.progress.emit(("Downloading ProxyPass",))
        proxyPassUrl = "https://github.com/Kas-tle/ProxyPass/releases/download/master-65/ProxyPass.jar"
        proxyPassJar = requests.get(proxyPassUrl)

        proxyPassFolder = toolsFolder + "/ProxyPass/"
        if not os.path.exists(proxyPassFolder):
            os.makedirs(proxyPassFolder)

        open(os.path.expanduser(proxyPassFolder) + "ProxyPass.jar", 'wb').write(proxyPassJar.content)
        window.worker.signals.progress.emit(("Finished downloading ProxyPass.",))
    #@Slot()
    #def printResultProxyPass(dataTuple):
    #    window.outputView.append(f"[INFO] {dataTuple[0]}")
    def downloadProxyPassThreaded(fn):
        window.worker = Worker(fn, configPath)
        window.threadpool.start(window.worker)
        #window.worker.signals.progress.connect(printResultProxyPass)
        window.worker.signals.progress.connect(logResult)
        #window.worker.signals.finished.connect(printResultProxyPass)
    ###########################################################################################################
    
    #####Download XCurl#####
    # -> the main downloading logic
    # -> prints the result to the outputView text edit
    # -> spawns a new thread and runs a() there. (See the Worker() class on top of the file for more info)
    def downloadXCurlandCaCert(configPath):
        xcurlUrl = "https://mirror.msys2.org/mingw/mingw64/mingw-w64-x86_64-curl-8.17.0-1-any.pkg.tar.zst"

        window.xcurlWorker.signals.progress.emit((f"Downloading mingw64-curl",))
        xcurlArchPackage = requests.get(xcurlUrl)

        xcurlTmpFolder = configPath + "/.tmp"
        if not os.path.exists(xcurlTmpFolder):
            os.makedirs(xcurlTmpFolder)
            window.xcurlWorker.signals.progress.emit((f"Created directory: {xcurlTmpFolder}",))

        open(xcurlTmpFolder + "/mingw-x64-curl.pkg.tar.zst", 'wb').write(xcurlArchPackage.content)
        window.xcurlWorker.signals.progress.emit((f"Downloaded mingw64-curl",))

        caCertUrl = "https://curl.se/ca/cacert.pem"
        window.xcurlWorker.signals.progress.emit((f"Downloading ca-bundle.crt (cacert.pem) from {caCertUrl}",))
        caCert = requests.get(caCertUrl)

        open(xcurlTmpFolder + "/ca-bundle.crt", 'wb').write(caCert.content)
        window.xcurlWorker.signals.progress.emit((f"Downloaded ca-bundle.crt",))

        ###Move the files
        destDir = f"{instancesDirectory}/{initialInstallationData['name']}/etc/ssl/certs"
        #Mingw
        #cacert
        os.makedirs(destDir)
        window.xcurlWorker.signals.progress.emit((f"Created {destDir}",))
        shutil.move(f"{xcurlTmpFolder}/ca-bundle.crt", f"{destDir}/ca-bundle.crt")
        window.xcurlWorker.signals.progress.emit((f"Configured ca-bundle.crt [DEBUG] (Moved from {xcurlTmpFolder}/ca-bundle.crt to {destDir}/ca-bundle.crt)",))

        #Clear /.tmp (do not delete /.tmp, just clear it's contents)
        #clearTmp() xd
    #@Slot()
    #def printResultXcurl(dataTuple):
    #    window.outputView.append(f"[INFO] {dataTuple[0]}") #This can be abstracted to be a single function and not one er install flow, to do.
    def downloadXcurlThreaded(fn):
        window.xcurlWorker = Worker(fn, configPath)
        window.threadpool.start(window.xcurlWorker)
        #window.xcurlWorker.signals.progress.connect(printResultXcurl)
        window.xcurlWorker.signals.progress.connect(logResult)
        #window.xcurlWorker.signals.finished.connect(printResultXcurl)
    ###########################################################################################################

    #####Download Education Edition#####
    #downloadProxyPass() -> the main downloading logic
    #printResultProxyPass() -> prints the result to the outputView text edit
    #downloadProxyPassThreaded() -> spawns a new thread and runs downloadProxyPass() there. (See the Worker() class on top of the file for more info)
    #def downloadEducationEdition():
    #    api = theapilol
    #    linkMatrix = requests.get()
    ###########################################################################################################
    downloadProtonGDKThreaded(downloadProtonGDK)
    if proxyPass:
        downloadProxyPassThreaded(downloadProxyPass)
    if createNewInstance:
        setupInitialInstallationThreaded(setupInitialInstallation)
    if xcurl:
        window.installWorker.signals.finished.connect(downloadXcurlThreaded)
    #if educationEdition:
    #    setupEducationEdition()
    #if not errorOcurred == "0"
    #    showDisclaimerOfNonFatalErrors()
