import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, QThreadPool, QRunnable, QObject, Signal
import datetime
import subprocess
import os
import traceback
import sys
import tarfile

class WorkerSignals(QObject):
    finished = Signal(tuple)
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
        ###self.signals.finished.emit(self.threadId)
       

@Slot()
def install(window, configPath, app):
    threadId = 0
    ###exctype, value = "0", "0"
    threadCount = window.threadpool.maxThreadCount()


    #####Error handling#####
    def errorHandler(e):
        #Display error message (Not implemented)
        ###sys.exit()
        print("An error has ocurred: " + str(e))
        QApplication.quit()

    
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
        ###sys.exit()
        errorHandler(e)
    
    #Determine necessary files
    window.outputView.append("Determining necessary files...")
    xcurl = window.xcurlConsentCheck.isChecked()
    proxyPass = window.proxyPassConsentCheck.isChecked()
    educationEdition = window.educationConsentCheck.isChecked()
    window.outputView.append(f"XCurl: {xcurl}")
    window.outputView.append(f"ProxyPass: {proxyPass}")
    window.outputView.append(f"Education Edition: {educationEdition}")

    #Check JVM availability
    window.outputView.append("Checking for JVM...")
    try:
        subprocess.run(["java", "--version"], capture_output=False)
        window.outputView.append("Success!")
    except Exception as jvmCheckFailed:
       window.outputView.append("[WARNING] Java check failed:" + str(jvmCheckFailed))

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
        protonGDKLink = "https://github.com/LukasPAH/GDK-Proton-Custom/releases/download/release-10-32-3/GDK-Proton10-32-Custom-3.tar.gz"
        try:
            protonGDKTarGz = requests.get(protonGDKLink)
        except Exception as e:
            raise(e)
        protonGDKFolder = toolsFolder + "/ProtonGDK/"
        if not os.path.exists(protonGDKFolder):
            os.mkdir(protonGDKFolder)
        try:
            open(os.path.expanduser(protonGDKFolder) + "ProtonGDK.tar.gz", 'wb').write(protonGDKTarGz.content)
            window.protonWorker.signals.finished.emit(threadId)
        except Exception as e:
            raise(e)
        try:
            tarfileProtonGDK = tarfile.open(protonGDKFolder + "ProtonGDK.tar.gz")
            tarfileProtonGDK.extractall(protonGDKFolder + "ProtonGDK")
            tarfileProtonGDK.close()
        except Exception as e:
            raise(e)
    def printResultProtonGDK():
        window.outputView.append("Finished downloading ProtonGDK (lucaspah fork)")
    def downloadProtonGDKThreaded(fn):
        window.protonWorker = Worker(fn, configPath)
        window.threadpool.start(window.protonWorker)
        window.protonWorker.signals.finished.connect(printResultProtonGDK)
        window.protonWorker.signals.error.connect(errorHandler)
    ###########################################################################################################

    #####Download ProxyPass#####
    #downloadProxyPass() -> the main downloading logic
    #printResultProxyPass() -> prints the result to the outputView text edit
    #downloadProxyPassThreaded() -> spawns a new thread and runs downloadProxyPass() there. (See the Worker() class on top of the file for more info)
    def downloadProxyPass(configPath):
        proxyPassUrl = "https://github.com/Kas-tle/ProxyPass/releases/download/master-65/ProxyPass.jar"
        try:
            proxyPassJar = requests.get(proxyPassUrl)
        except Exception as e:
            raise(e)
        proxyPassFolder = toolsFolder + "/ProxyPass/"
        if not os.path.exists(proxyPassFolder):
            os.makedirs(proxyPassFolder)
        try:
            open(os.path.expanduser(proxyPassFolder) + "ProxyPass.jar", 'wb').write(proxyPassJar.content)
            window.worker.signals.finished.emit(threadId)
        except Exception:
            raise(e)
    @Slot()
    def printResultProxyPass(threadId):
        window.outputView.append(f"Finished downloading ProxyPass. On thread {threadId}.")
    def downloadProxyPassThreaded(fn):
        window.worker = Worker(fn, configPath)
        window.threadpool.start(window.worker)
        window.worker.signals.finished.connect(printResultProxyPass)
    ###########################################################################################################
    
    downloadProtonGDKThreaded(downloadProtonGDK)
    if proxyPass:
        downloadProxyPassThreaded(downloadProxyPass)
    #if xcurl:
    #    downloadXCurlThreaded()
