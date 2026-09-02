from qtpy import QtWidgets
#from PyQt5 import QtWidgets

from pathlib import Path # base python, no pip install needed

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils 
import cair_data_package_tool.version_check as version_check

from layout_general_scrollannotate_widget import ScrollAnnotateWindow

class AddWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay,trackerDict,trackersToAddToTool):
        super().__init__()
        self.w = None  # No external window yet.

        # inherited vars
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.trackerDict = trackerDict
        self.trackersToAddToTool = trackersToAddToTool

        # pull out of trackerDict inherited var for immediate use
        self.trackerType = self.trackerDict["trackerType"]
        self.schemaVersion = self.trackerDict["schemaVersion"]
        self.trackerName = self.trackerDict["trackerName"]
        self.trackerTitle = self.trackerDict["trackerTitle"]
        
        widget = QtWidgets.QWidget()
        
        self.buttonAnnotate = QtWidgets.QPushButton(text="Add a new " + self.trackerType,parent=self)
        self.buttonAnnotate.clicked.connect(self.annotate)

        self.buttonEdit = QtWidgets.QPushButton(text="Edit an existing " + self.trackerType,parent=self)
        self.buttonEdit.clicked.connect(self.edit)

        self.buttonAddBasedOn = QtWidgets.QPushButton(text="Add a new " + self.trackerType + " based on an existing " + self.trackerType,parent=self)
        self.buttonAddBasedOn.clicked.connect(self.annotate_based_on)

        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()

        advanced_layout = QtWidgets.QVBoxLayout()
        advanced_layout.addWidget(self.buttonAddBasedOn)
        advanced_groupbox = QtWidgets.QGroupBox("Advanced")
        advanced_groupbox.setLayout(advanced_layout)
        
        layout.addWidget(self.buttonAnnotate)
        layout.addWidget(self.buttonEdit)
        layout.addWidget(advanced_groupbox)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def annotate(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        workingDataPkgDir = dsc_pkg_utils.getWorkingDataPkgDir(self=self)
        if not workingDataPkgDir:
            return
        else:
            self.workingDataPkgDir = workingDataPkgDir
        
        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self):
            return

        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,
                workingDataPkgDir=self.workingDataPkgDir,
                trackerDict=self.trackerDict,
                trackersToAddToTool=self.trackersToAddToTool,
                mode="add")
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,
                workingDataPkgDir=self.workingDataPkgDir,
                trackerDict=self.trackerDict,
                trackersToAddToTool=self.trackersToAddToTool,
                mode="add")
            self.w.show()

    def edit(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        workingDataPkgDir = dsc_pkg_utils.getWorkingDataPkgDir(self=self)
        if not workingDataPkgDir:
            return
        else:
            self.workingDataPkgDir = workingDataPkgDir

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self):
            return

        # for editing need to check if json txt annotation files are updated - if not updated, will break the form import
        # so do full check for if update is necessary to get update status of trackers and json txt annotation files
        versionCheck = version_check.version_check(workingDataPkgDir=self.workingDataPkgDir,trackersImplemented=[self.trackerDict])
        
        versionCheckAllUpToDate = versionCheck[0]
        versionCheckMessageText = versionCheck[1]
        versionCheckDf = versionCheck[2]

        filesCheckList = [] # initialize the list of json txt annotation files that are up to date and can be edited now as empty
        versionCheckDf["path-stem"] = [Path(p) for p in versionCheckDf["file"]] 
        versionCheckDf["path-stem"] = [p.stem for p in versionCheckDf["path-stem"]] 
        versionCheckDfSave = versionCheckDf
        
        addToMessage = "<br><br>checking json txt annotation files for ability to edit...<br>"
        saveFormat = '<span style="color:blue;">{}</span>'
        # check if any json txt annotation files are not up to date and get a list if they exist
        versionCheckDf = versionCheckDf[versionCheckDf["trackerType"] == self.trackerDict["trackerNameCamelCase"]]
        versionCheckDf = versionCheckDf[versionCheckDf["fileType"] == "json txt"]
        
        if not versionCheckDf.empty: # at least one json txt annotation file
            print("found at least one json txt annotation file")
            
            addToMessage = addToMessage + "found at least one json txt annotation file...<br>"
            versionCheckUpToDateDf = versionCheckDf[versionCheckDf["upToDate"] == "Yes"]
            versionCheckNotUpToDateDf = versionCheckDf[versionCheckDf["upToDate"] != "Yes"]

            if not versionCheckUpToDateDf.empty: # at least one json txt annotation file is up to date
                print("found at least one json txt annotation file that is up to date; json txt annotation files that are up to date may be edited")
                addToMessage = addToMessage + "found at least one json txt annotation file that is up to date; json txt annotation files that are up to date may be edited...<br>"
                
                filesCheckList = versionCheckUpToDateDf["file"].tolist() # if at least one json txt annotation file is up to date and can be edited now, populate the list of json txt annotation files that are up to date and can be edited now
                jsonTxtUpToDateList = versionCheckUpToDateDf["path-stem"].tolist()
                jsonTxtUpToDateString = "<br>".join(jsonTxtUpToDateList) 

                if not versionCheckNotUpToDateDf.empty: #at least one json txt annotation file is NOT up to date
                    
                    addToMessage = addToMessage + "found at least one json txt annotation file that is NOT up to date; json txt annotation files that are NOT up to date can NOT be edited...<br>"
                
                    jsonTxtNotUpToDateList = versionCheckNotUpToDateDf["path-stem"].tolist()
                    jsonTxtNotUpToDateString = "<br>".join(jsonTxtNotUpToDateList)

                    addToMessage = addToMessage + "the following json txt annotation files are up to date and can be edited NOW:<br><br>" + jsonTxtUpToDateString + "<br><br>"
                    addToMessage = addToMessage + "the following json txt annotation files are NOT up to date and can NOT be edited NOW:<br><br>" + jsonTxtNotUpToDateString + "<br><br>"
                
                    versionCheckCanBeUpdatedDf = versionCheckNotUpToDateDf[versionCheckNotUpToDateDf["canBeUpdated"] == "Yes"]
                    versionCheckCanNotBeUpdatedDf = versionCheckNotUpToDateDf[versionCheckNotUpToDateDf["canBeUpdated"] != "Yes"]

                    if not versionCheckCanBeUpdatedDf.empty: # at least one json txt annotation file can be updated
                        
                        jsonTxtCanBeUpdatedList = versionCheckCanBeUpdatedDf["path-stem"].tolist()
                        jsonTxtCanBeUpdatedString = "<br>".join(jsonTxtCanBeUpdatedList)

                        addToMessage = addToMessage + "the following json txt annotation files are NOT up to date, but can be updated, and may be edited once they are updated:<br><br>" + jsonTxtCanBeUpdatedString + "<br><br>Head to the \"Data Package\" tab >> \"Audit and Update\" sub-tab to update your working data package directory files!<br>"
                

                else: # all json txt annotation files are up to date
                    addToMessage = addToMessage + "all json txt annotation files are up to date and may be edited NOW..<br>"
                    saveFormat = '<span style="color:green;">{}</span>'
                    
            else: # no json txt files are up to date - return
                print("no json txt annotation files are up to date, none may be edited")
                addToMessage = addToMessage + "<br><br>no json txt annotation files available to edit because none are up to date with current schema - head to the \"Data Package\" tab >> \"Update and Audit\" sub-tab to update your working data package directory files, then try again.<br>"
                saveFormat = '<span style="color:red;">{}</span>'
                messageText = addToMessage
                self.userMessageBox.append(saveFormat.format(messageText))
                return
                
        else: # no json txt annotation files exist - return
            print("no json txt annotation files")
            addToMessage = "<br><br>no json txt annotation files available to edit because none exist yet - you must add at least one term to the term tracker before you can edit a term...<br>"
            saveFormat = '<span style="color:red;">{}</span>'
            messageText = addToMessage
            self.userMessageBox.append(saveFormat.format(messageText))
            return 
        
        messageText = addToMessage
        self.userMessageBox.append(saveFormat.format(messageText)) 


        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, 
                workingDataPkgDir=self.workingDataPkgDir, 
                trackerDict=self.trackerDict,
                filesCheckList=filesCheckList,
                trackersToAddToTool=self.trackersToAddToTool, 
                mode="edit")
            self.w.show()
            self.w.select_load_file()
        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, 
                workingDataPkgDir=self.workingDataPkgDir, 
                trackerDict=self.trackerDict,
                filesCheckList=filesCheckList, 
                trackersToAddToTool=self.trackersToAddToTool,
                mode="edit")
            self.w.show()
            self.w.select_load_file()       

    def annotate_based_on(self,checked):

        # check if user has set a working data package dir - if not exit gracefully with informative message
        workingDataPkgDir = dsc_pkg_utils.getWorkingDataPkgDir(self=self)
        if not workingDataPkgDir:
            return

        # check self.schemaVersion against version in operational schema version file 
        # if no operational schema version file exists OR 
        # if version in operational schema version file is less than self.schemaVersion 
        # return with message that update of tracker version is needed before new annotations can be added
        if not dsc_pkg_utils.checkTrackerCreatedSchemaVersionAgainstCurrent(self=self,trackerTypeFileNameString="term-tracker",trackerTypeMessageString="Term Tracker"):
            return

        # for adding based on need to check if json txt annotation files are updated - if not updated, will break the form import
        # so do full check for if update is necessary to get update status of trackers and json txt annotation files
        versionCheck = version_check.version_check(workingDataPkgDir=workingDataPkgDir,trackersImplemented=[self.trackerDict])
        
        versionCheckAllUpToDate = versionCheck[0]
        versionCheckMessageText = versionCheck[1]
        versionCheckDf = versionCheck[2]

        filesCheckList = [] # initialize the list of json txt annotation files that are up to date and can be edited now as empty
        versionCheckDf["path-stem"] = [Path(p) for p in versionCheckDf["file"]] 
        versionCheckDf["path-stem"] = [p.stem for p in versionCheckDf["path-stem"]] 
        versionCheckDfSave = versionCheckDf
        
        addToMessage = "<br><br>checking json txt annotation files for ability to add new file based on existing file...<br>"
        saveFormat = '<span style="color:blue;">{}</span>'
        # check if any json txt annotation files are not up to date and get a list if they exist
        versionCheckDf = versionCheckDf[versionCheckDf["trackerType"] == "termTracker"]
        versionCheckDf = versionCheckDf[versionCheckDf["fileType"] == "json txt"]
        
        if not versionCheckDf.empty: # at least one json txt annotation file
            print("found at least one json txt annotation file")
            
            addToMessage = addToMessage + "found at least one json txt annotation file...<br>"
            versionCheckUpToDateDf = versionCheckDf[versionCheckDf["upToDate"] == "Yes"]
            versionCheckNotUpToDateDf = versionCheckDf[versionCheckDf["upToDate"] != "Yes"]

            if not versionCheckUpToDateDf.empty: # at least one json txt annotation file is up to date
                print("found at least one json txt annotation file that is up to date; json txt annotation files that are up to date may be used as the basis for a new annotation file")
                addToMessage = addToMessage + "found at least one json txt annotation file that is up to date; json txt annotation files that are up to date may be used as the basis for a new annotation file...<br>"
                
                filesCheckList = versionCheckUpToDateDf["file"].tolist() # if at least one json txt annotation file is up to date and can be edited now, populate the list of json txt annotation files that are up to date and can be edited now
                jsonTxtUpToDateList = versionCheckUpToDateDf["path-stem"].tolist()
                jsonTxtUpToDateString = "<br>".join(jsonTxtUpToDateList) 

                if not versionCheckNotUpToDateDf.empty: #at least one json txt annotation file is NOT up to date
                    
                    addToMessage = addToMessage + "found at least one json txt annotation file that is NOT up to date; json txt annotation files that are NOT up to date can NOT be used as the basis for a new annotation file...<br>"
                
                    jsonTxtNotUpToDateList = versionCheckNotUpToDateDf["path-stem"].tolist()
                    jsonTxtNotUpToDateString = "<br>".join(jsonTxtNotUpToDateList)

                    addToMessage = addToMessage + "the following json txt annotation files are up to date and can be used as the basis for a new annotation file NOW:<br><br>" + jsonTxtUpToDateString + "<br><br>"
                    addToMessage = addToMessage + "the following json txt annotation files are NOT up to date and can NOT be used as the basis for a new annotation file NOW:<br><br>" + jsonTxtNotUpToDateString + "<br><br>"
                
                    versionCheckCanBeUpdatedDf = versionCheckNotUpToDateDf[versionCheckNotUpToDateDf["canBeUpdated"] == "Yes"]
                    versionCheckCanNotBeUpdatedDf = versionCheckNotUpToDateDf[versionCheckNotUpToDateDf["canBeUpdated"] != "Yes"]

                    if not versionCheckCanBeUpdatedDf.empty: # at least one json txt annotation file can be updated
                        
                        jsonTxtCanBeUpdatedList = versionCheckCanBeUpdatedDf["path-stem"].tolist()
                        jsonTxtCanBeUpdatedString = "<br>".join(jsonTxtCanBeUpdatedList)

                        addToMessage = addToMessage + "the following json txt annotation files are NOT up to date, but can be updated, and may be used as the basis for a new annotation file once they are updated:<br><br>" + jsonTxtCanBeUpdatedString + "<br><br>Head to the \"Data Package\" tab >> \"Audit and Update\" sub-tab to update your working data package directory files!<br>"
                

                else: # all json txt annotation files are up to date
                    addToMessage = addToMessage + "all json txt annotation files are up to date and may be used as the basis for a new annotation file NOW..<br>"
                    saveFormat = '<span style="color:green;">{}</span>'
                    
            else: # no json txt files are up to date - return
                print("no json txt annotation files are up to date, none may be edited")
                addToMessage = addToMessage + "<br><br>no json txt annotation files available to be used as the basis for a new annotation file because none are up to date with current schema - head to the \"Data Package\" tab >> \"Update and Audit\" sub-tab to update your working data package directory files, then try again.<br>"
                saveFormat = '<span style="color:red;">{}</span>'
                messageText = addToMessage
                self.userMessageBox.append(saveFormat.format(messageText))
                return
                
        else: # no json txt annotation files exist - return
            print("no json txt annotation files")
            addToMessage = "<br><br>no json txt annotation files available to be used as the basis for a new annotation file because none exist yet - you must add at least one term to the term tracker before you can edit a term...<br>"
            saveFormat = '<span style="color:red;">{}</span>'
            messageText = addToMessage
            self.userMessageBox.append(saveFormat.format(messageText))
            return 
        
        messageText = addToMessage
        self.userMessageBox.append(saveFormat.format(messageText)) 


        # form will only be opened if a valid working data pkg dir is set, and that dir will be passed to the form widget
        if self.w is None:
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, 
                workingDataPkgDir=workingDataPkgDir, 
                filesCheckList=filesCheckList, 
                trackersToAddToTool=self.trackersToAddToTool,
                mode="add-based-on")
            self.w.show()
            self.w.select_load_file()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.
            self.w = ScrollAnnotateWindow(
                workingDataPkgDirDisplay=self.workingDataPkgDirDisplay, 
                workingDataPkgDir=workingDataPkgDir, 
                filesCheckList=filesCheckList, 
                trackersToAddToTool=self.trackersToAddToTool,
                mode="add-based-on")
            self.w.show()
            self.w.select_load_file()

    

        
      

         
        
        


    
    