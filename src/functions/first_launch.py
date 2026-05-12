import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtCore import QFile, QIODevice, Slot, QUrl
from PySide6.QtGui import QDesktopServices
import src.functions.assets

def firstLaunch(beLauncherVersion):
    #Init stuff
    app = QApplication(sys.argv)
    ui_file_name = "src/ui/setup.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)

    #Configure the version label
    window.versionLabel.setText(window.versionLabel.text().format(beLauncherVersion))
    #Page 0 - Welcome screen
    @Slot()
    def page1():
        window.stackedWidget.setCurrentIndex(1)
    window.commandLinkButton.clicked.connect(page1)
    @Slot()
    def openDocumentation():
        QDesktopServices.openUrl(QUrl("https://github.com/mr-dexter-ssj/bedrock-launcher-linux"))
    window.documentationButton.clicked.connect(openDocumentation)
    #Page 1 - Set up the first instance
    @Slot()
    def openFolder():
        selectedFolder = QFileDialog.getExistingDirectory(caption="Open Folder", dir="~")
        window.pathFolderLineEdit.setText(selectedFolder)
    window.openFolderButton.clicked.connect(openFolder)
    @Slot()
    def getHelp():
        window.stackedWidget.setCurrentIndex(6)
    window.helpButton.clicked.connect(getHelp)
    @Slot()
    def nextPage():
        window.stackedWidget.setCurrentIndex(window.stackedWidget.currentIndex() + 1)
    window.nextButton.clicked.connect(nextPage)
    #Page 2 - ProxyPass consent screen 
    @Slot()
    def openKastleGithub():
        QDesktopServices.openUrl(QUrl("https://github.com/Kas-tle/ProxyPass/"))
    window.learnMoreButton.clicked.connect(openKastleGithub)
    @Slot()
    def goBack():
        window.stackedWidget.setCurrentIndex(window.stackedWidget.currentIndex() - 1)
    window.backButton_2.clicked.connect(goBack)
    window.nextButton_2.clicked.connect(nextPage)
    #Page 3 - Education Edition consent screen
    window.backButton_3.clicked.connect(goBack)
    ###---install() is located in another file (****NOT IMPLEMENTED YET****!!!!!!!!!)
    #Page 4 - Install screen
    ###---Only button here is cancelButton, which interrupts install()
    #Page 5 - All Done screen
    ###---finishButton calls finish()
    #Page 6 - Help page
    @Slot()
    def goBackFromHelp():
        window.stackedWidget.setCurrentIndex(1)
    window.backButton.clicked.connect(goBackFromHelp)
 



    #More init stuff
    window.show()
    sys.exit(app.exec())