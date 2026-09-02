import os # base python, no pip install needed
import sys # base python, no pip install needed

from qtpy import QtWidgets
#from PyQt5 import QtWidgets

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils # local module, no pip install needed

from layout_csvviewwidget import CSVViewWindow

class CSVViewPushToLoadWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay, fileBaseName, fileStartsWith, fileTypeTitle,viewerMode="view"):
        super().__init__()
        self.w = None  # No external window yet.
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.fileBaseName = fileBaseName
        self.fileStartsWith = fileStartsWith
        self.fileTypeTitle = fileTypeTitle
        self.viewerMode = viewerMode
        
        widget = QtWidgets.QWidget()

        if self.viewerMode == "view":
            buttonText = "View CSV"
        elif self.viewerMode == "select to edit":
            buttonText = "View CSV - select one record to edit"

        if self.fileTypeTitle:
            if self.viewerMode == "view":
                buttonText = "View " + self.fileTypeTitle 
            elif self.viewerMode == "select to edit":
                buttonText = "View " + self.fileTypeTitle + " - Select one record to edit"
        
        self.buttonViewCsv = QtWidgets.QPushButton(text=buttonText, parent=self)
        #self.buttonViewCsv.clicked.connect(self.view_csv)
        self.buttonViewCsv.clicked.connect(lambda: self.view_csv(self.viewerMode))
        

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonViewCsv)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def view_csv(self,viewerMode):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        workingDataPkgDir = dsc_pkg_utils.getWorkingDataPkgDir(self=self)
        if not workingDataPkgDir:
            return

        if self.fileBaseName:
            self.fileName = os.path.join(workingDataPkgDir,self.fileBaseName)

            # check that file exists in working data pkg dir, if not, return
            if not os.path.exists(self.fileName):
                messageText = "<br>There is no " + self.fileTypeTitle + " file in your working Data Package Directory; Your working Data Package Directory must contain a " + self.fileTypeTitle + " file to proceed - The file should be named: " + self.fileBaseName + ". If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. <br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
            
            # check that file is closed (user doesn't have it open in excel for example)
            try: 
                with open(self.fileName,'r+') as f:
                    print("file is closed, proceed!!")
            except PermissionError:
                    messageText = "<br>The " + self.fileTypeTitle + " file in your working Data Package Directory is open in another application, and must be closed to proceed; Check if the " + self.fileTypeTitle + " file is open in Excel or similar application, close the file, and try again. <br><br>"
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    return

        else:
            self.fileName = workingDataPkgDir

            # check that all at least one of the desired file types exist to view and that all files of that type are closed (user doesn't have it open in excel for example)
            trackersList = [filename for filename in os.listdir(workingDataPkgDir) if filename.startswith(self.fileStartsWith)]
            print("trackersList: ", trackersList)
            
            if trackersList:
                for tracker in trackersList:

                    try: 
                        with open(os.path.join(workingDataPkgDir,tracker),'r+') as f:
                            print("file is closed, proceed!!")
                    except PermissionError:
                            messageText = "<br>At least one " + self.fileTypeTitle + " file that already exists in your working Data Package Directory is open in another application, and must be closed to proceed; Check if any " + self.fileTypeTitle + " files are open in Excel or similar application, close the file(s), and try again. <br><br>"
                            saveFormat = '<span style="color:red;">{}</span>'
                            self.userMessageBox.append(saveFormat.format(messageText))
                            return
            else: 
                messageText = "<br>There are no " + self.fileTypeTitle + " files in your working Data Package Directory to view. There must be at least one " + self.fileTypeTitle + " file in your working Data Package Directory in order to proceed to view a file of this type. Files of this type should have a file name that starts with: " + self.fileStartsWith + ".<br><br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

        if self.w is None:
            self.w = CSVViewWindow(fileName=self.fileName,fileStartsWith=self.fileStartsWith,fileTypeTitle=self.fileTypeTitle,viewerMode=self.viewerMode)
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            self.w = CSVViewWindow(fileName=self.fileName,fileStartsWith=self.fileStartsWith,fileTypeTitle=self.fileTypeTitle,viewerMode=self.viewerMode)
            self.w.show()

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    window = CSVViewPushToLoadWindow()
    window.show()
    sys.exit(app.exec_())