import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, QThreadPool, QRunnable, QObject, Signal
import datetime
import subprocess
import os
import traceback
import sys

class WorkerSignals(QObject):
    finished = Signal(tuple)
    error = Signal(tuple)
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
        #self.fn(self.configPath)
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit(self.threadId)
       

@Slot()
def install(window, configPath, app):
    threadId = 0
    exctype, value = 0
    threadCount = window.threadpool.maxThreadCount()
    window.outputView.append(f"[DEBUG] Multithreading with maximum {threadCount} threads")

    #Check for umu-launcher
    window.outputView.append("Checking for umu-launcher")
    try:
        import umu
        umuVersion = umu.__version__
        window.outputView.append(f"Found umu-launcher version {umuVersion}")
    except Exception as e:
        window.outuptView.append("Failed umu-launcher check. The installer can't continue." + str(e))
        #sys.exit() --------->   (I feel it's more brute force, so I do app.quit())
        app.quit()
    
    #Configure starting date-time
    window.outputView.append(f"[{str(datetime.datetime.now())[:-7]}] {window.outputView.placeholderText()}")

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
    
    #####Download ProtonGDK#####
    #Note: This downloads the latest fix of ProtonGDK (lucaspah fork). If needed, this can be changed to a .json database.
    def downloadProtonGDK():
        protonGDKLink = "https://github.com/LukasPAH/GDK-Proton-Custom/releases/download/release-10-32-3/GDK-Proton10-32-Custom-3.tar.gz"
        try:
            protonGDKTarGz = requests.get(protonGDKLink)
        except Exception as e:
            print("Hi")
        


    #####Download ProxyPass#####
    #downloadProxyPass() -> the main downloading logic
    #printResultProxyPass() -> prints the result to the outputView text edit
    #downloadProxyPassThreaded() -> spawns a new thread and runs downloadProxyPass() there. (See the Worker() class on top of the file for more info)
    def downloadProxyPass(configPath):
        proxyPassUrl = "https://github.com/Kas-tle/ProxyPass/releases/download/master-65/ProxyPass.jar"
        try:
            proxyPassJar = requests.get(proxyPassUrl)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            window.worker.signals.error.emit((exctype, value, traceback.format_exc()))
        proxyPassFolder = configPath + "/ProxyPass/"
        if not os.path.exists(proxyPassFolder):
            os.mkdir(proxyPassFolder)
        try:
            open(os.path.expanduser(proxyPassFolder) + "ProxyPass.jar", 'wb').write(proxyPassJar.content)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            window.worker.signals.error.emit((exctype, value, traceback.format_exc()))
    @Slot()
    def printResultProxyPass(threadId):
        window.outputView.append(f"Finished downloading ProxyPass. On thread {threadId}.")
    @Slot()
    def printErrorProxyPass(*args):
        window.outputView.append(f"Error downloading ProxyPass. {exctype}. {value}")
        app.quit() #This will be changed to window dialog displaying error info and close button to close.
    def downloadProxyPassThreaded(fn):
        window.worker = Worker(fn, configPath)
        window.threadpool.start(window.worker)
        window.worker.signals.error.connect(printErrorProxyPass)
        window.worker.signals.finished.connect(printResultProxyPass) 
    if proxyPass:
        downloadProxyPassThreaded(downloadProxyPass)
    #if xcurl:
    #    downloadXCurlThreaded()

