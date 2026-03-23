from pathlib import Path
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QLabel, QMessageBox, QMainWindow, QPushButton, QGridLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, Qt

#-----GUI Definition-----
class WelcomeInstallScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bedrock Launcher")
        self.resize(600, 550)
        layout = QGridLayout(self)
        welcomeLabel = QLabel("Welcome to Bedrock Launcher")
        welcomeLabel.setAlignment(Qt.AlignCenter)
        startButton = QPushButton("Start")
        startButton.setIcon(QIcon.fromTheme("document-save"))

        layout.addWidget(welcomeLabel, 0 ,0)
        layout.addWidget(startButton, 1, 0)

app = QApplication()
app.setStyle("breeze")
window = WelcomeInstallScreen()
window.show()
app.exec()