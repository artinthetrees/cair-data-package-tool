import os # base python, no pip install needed

#from PyQt5 import QtWidgets
from qtpy import QtWidgets

from pathlib import Path # base python, no pip install needed

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils # local module, no pip install needed
import cair_data_package_tool.back_door_edit as back_door_edit
import cair_data_package_tool.version_check as version_check

class PkgCreateWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay,trackersToAddToTool):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.trackersToAddToTool = trackersToAddToTool
        
        widget = QtWidgets.QWidget()
        
        self.buttonNewPkg = QtWidgets.QPushButton(text="Create New Data Package",parent=self)
        self.buttonNewPkg.clicked.connect(self.create_new_pkg)

        self.buttonContinuePkg = QtWidgets.QPushButton(text="Continue Existing Data Package",parent=self)
        self.buttonContinuePkg.clicked.connect(self.continue_pkg)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonNewPkg)
        layout.addWidget(self.buttonContinuePkg)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_new_pkg(self):
        
        parentFolderPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Parent Directory Where Data Package Directory Should Be Created!')
        
        if not parentFolderPath:
            messageText = "<br>" + "You must select a parent directory where the Data Package Directory should be created to proceed."
            self.userMessageBox.append(messageText)
            return

        pkgPath = dsc_pkg_utils.new_pkg(trackersToAddToTool=self.trackersToAddToTool,pkg_parent_dir_path=parentFolderPath)

        if not pkgPath:
            messageText = "<br>" + "A Data Package Directory could not be created at " + parentFolderPath + ". Check to see if a Data Package Directory (i.e. a directory called \"dsc-pkg\") already exists at this location."
            self.userMessageBox.append(messageText)
            return
        else: 
            # create an in-use file to "check out" the dsc-pkg and prevent modification of this local copy by more than one person at a time  
            back_door_edit.writeMetadataDirLockFile(metadataDirPath=pkgPath,lockFileMode="manual")

            # if the user is switching data package dir after initially specifying a different data package dir in this session of using the app, then if the checkout/switch to new data package dir is 
            # successful, we need to "return/check in" the data package dir we are switching from
            if self.pkgPath:
                print("user is switching from previously specified data package dir to another newly created data package dir - work on deleting checkout file from previously specified data package dir to indicate it is no longer in use")
                if os.path.exists(os.path.join(self.pkgPath,back_door_edit.metadataDirLockFileName)):
                    os.remove(os.path.join(self.pkgPath,back_door_edit.metadataDirLockFileName))
                    print("checkout file in data package dir user is switching away from has been deleted in order to indicate that it is no longer in use")
                else:
                    print("something went wrong - no checkout file found in data package dir user is switching away from")
            else:
                print("user is specifying a newly created data package directory for the first time this session - do not need to work on deleting checkout file from previously specified data package directory as there is no previously specified data package directory") 

        
        messageText = "<br>" + "Created new HEAL DSC Data Package Directory at: "  + pkgPath
        self.userMessageBox.append(messageText)

        messageText = "<br>" + "Your working Data Package Directory has been set at: "  + pkgPath
        self.userMessageBox.append(messageText)

        self.pkgPath = pkgPath
        self.workingDataPkgDirDisplay.setText(self.pkgPath)
        
        
        

    def continue_pkg(self):
        
        pkgPath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Your Existing Data Package Directory!')
        
        if not pkgPath:
            messageText = "<br>" + "You must select an existing Data Package Directory to proceed."
            self.userMessageBox.append(messageText)
            return

        requiredFiles = []
        for i in self.trackersToAddToTool:
            requiredFiles.append(i["trackerFileName"])
        
        requiredDirPrefix = "dsc-pkg"

        if not str(Path(pkgPath).name).startswith(requiredDirPrefix):
            messageText = "<br>" + "The directory you selected as your existing Data Package Directory does not have a name that starts with the required Data Package Directory prefix of " + requiredDirPrefix + ". Check that you selected the correct directory. You can use the Create New Data Package push button above to create a new Data Package Directory with the required Data Package Directory prefix."
            self.userMessageBox.append(messageText)
            return

        requiredFilesExist = [os.path.isfile(os.path.join(pkgPath,f)) for f in requiredFiles]

        if not all(requiredFilesExist):
            messageText = "<br>" + "The directory you selected as your existing Data Package Directory does not contain all required files for an initialized Data Package Directory. Required files include: " + "<br><br>" + "<br>".join(requiredFiles) + "<br><br>" + "Check that you selected the correct directory. You can use the Create New Data Package push button above to create a new Data Package Directory with the required files." 
            self.userMessageBox.append(messageText)
            return

        # check if this data package dir is in use by another user, 
        # if it is, don't allow the current user to select this data package to work on
        # if it is not, allow the current user to select this data package to work on AND write a file that "checks out" this data package dir so that if another user tries to use it at the same time it will not allow it
        if back_door_edit.checkMetadataDirLockFile(metadataDirPath=pkgPath,metadataDirLockFileName=back_door_edit.metadataDirLockFileName,self=self)["lockFileExists"]:
            return
        else: 
            # create an in-use file to "check out" the dsc-pkg and prevent modification of this local copy by more than one person at a time  
            back_door_edit.writeMetadataDirLockFile(metadataDirPath=pkgPath,metadataDirLockFileName=back_door_edit.metadataDirLockFileName,lockFileMode="manual")
            
            # if the user is switching data package dir after initially specifying a different data package dir in this session of using the app, then if the checkout/switch to new data package dir is 
            # successful, we need to "return/check in" the data package dir we are switching from
            if self.pkgPath:
                print("user is switching from previously specified data package dir to another existing data package dir - work on deleting checkout file from previously specified data package dir to indicate it is no longer in use")
                if os.path.exists(os.path.join(self.pkgPath,back_door_edit.metadataDirLockFileName)):
                    os.remove(os.path.join(self.pkgPath,back_door_edit.metadataDirLockFileName))
                    print("checkout file in data package dir user is switching away from has been deleted in order to indicate that it is no longer in use")
                else:
                    print("something went wrong - no checkout file found in data package dir user is switching away from")
            else:
                print("user is specifying an existing data package directory for the first time this session - do not need to work on deleting checkout file from previously specified data package directory as there is no previously specified data package directory") 

        messageText = "<br>" + "Your working Data Package Directory has been set at: "  + pkgPath + "<br><br>Checking if updates to dsc-pkg files are needed...<br>"
        self.userMessageBox.append(messageText)
        QtWidgets.QApplication.processEvents() # print accumulated user status messages

        self.pkgPath = pkgPath
        self.workingDataPkgDirDisplay.setText(self.pkgPath)

        versionCheck = version_check.version_check(workingDataPkgDir=self.pkgPath,trackersImplemented=self.trackersToAddToTool)
        
        versionCheckAllUpToDate = versionCheck[0]
        versionCheckMessageText = versionCheck[1]

        messageText = "<br>" + versionCheckMessageText
        
        if versionCheckAllUpToDate:
            saveFormat = '<span style="color:green;">{}</span>'
        else:
            saveFormat = '<span style="color:red;">{}</span>'

        self.userMessageBox.append(saveFormat.format(messageText)) 

    