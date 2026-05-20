import requests
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, QThreadPool, QRunnable, QObject, Signal
import datetime
import subprocess
import os
import traceback
import sys

class WorkerSignals(QObject):
    finished = Signal(int, str)
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(tuple)

class dlProxyPass(QRunnable):
    def __init__(self, configPath,  *args, **kwargs):
        super().__init__()
        self.configPath = configPath
        self.signals = WorkerSignals()
        self.threadId = kwargs.get("thread_id", 0)

    @Slot()
    def run(self):
        #Download and setup ProxyPass
        proxyPassUrl = "https://github.com/Kas-tle/ProxyPass/releases/download/master-65/ProxyPass.jar"
        try:
            proxyPassJar = requests.get(proxyPassUrl)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            whatWasDone = "Download"
            self.signals.finished.emit(self.threadId, whatWasDone)
        proxyPassFolder = self.configPath + "/ProxyPass/"
        if not os.path.exists(proxyPassFolder):
            os.mkdir(proxyPassFolder)
        try:
            open(os.path.expanduser(proxyPassFolder) + "ProxyPass.jar", 'wb').write(proxyPassJar.content)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            whatWasDone = "Save"
            self.signals.finished.emit(self.threadId, whatWasDone)

@Slot()
def install(window, configPath):
    threadId = 0
    whatWasDone = "nothinglol"
    window.threadpool = QThreadPool()
    threadCount = window.threadpool.maxThreadCount()
    window.outputView.append(f"Multithreading with maximum {threadCount} threads")
    window.outputView.append(f"[{str(datetime.datetime.now())[:-7]}] {window.outputView.placeholderText()}")
    window.outputView.append("Determining necessary files...")
    #Determine necessary files
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
    @Slot()
    def printResultToTextEdit(threadId, whatWasDone):
        if whatWasDone == "Download":
            window.outputView.append(f"Finished downloading ProxyPass. On thread {threadId}")
        elif whatWasDone == "Save":
            window.outputView.append(f"Saved ProxyPass. On thread {threadId}")
    def downloadProxyPassThreaded():
        worker = dlProxyPass(configPath)
        window.threadpool.start(worker)
        worker.signals.finished.connect(printResultToTextEdit) 
    if proxyPass:
        downloadProxyPassThreaded()
    #if xcurl:
    #    downloadXCurlThreaded()

