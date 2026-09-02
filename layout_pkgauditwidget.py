import os # base python, no pip install needed

#from PyQt5 import QtWidgets
from qtpy import QtWidgets

from pathlib import Path # base python, no pip install needed

import pandas as pd # pandas already installed as a healdata_utils dependency, no pip install needed
import json # base python, no pip install needed

import cair_data_package_tool.schema_utils as schema_utils
import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils # local module, no pip install needed
import cair_data_package_tool.version_check as version_check
import cair_data_package_tool.version_update_tracker as version_update_tracker


class PkgAuditWindow(QtWidgets.QMainWindow):

    def __init__(self, workingDataPkgDirDisplay, trackersToAddToTool):
        super().__init__()
        self.w = None  # No external window yet.
        
        self.pkgPath = None # Initialize with no working data package directory path
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.trackersToAddToTool = trackersToAddToTool
        
        widget = QtWidgets.QWidget()
        
        # self.buttonCheckPkgVersions = QtWidgets.QPushButton(text="Check Package Versions",parent=self)
        # self.buttonCheckPkgVersions.clicked.connect(self.check_pkg_versions)

        self.buttonUpdatePkgVersions = QtWidgets.QPushButton(text="Update Package Versions",parent=self)
        self.buttonUpdatePkgVersions.clicked.connect(self.update_pkg_versions)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(self.buttonCheckPkgVersions)
        layout.addWidget(self.buttonUpdatePkgVersions)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def check_pkg_versions(self):
        print("check package versions")
        
        
        
    def update_pkg_versions(self):
        print("update package versions")

        # check if user has set a working data package dir - if not exit gracefully with informative message
        workingDataPkgDir = dsc_pkg_utils.getWorkingDataPkgDir(self=self)
        if not workingDataPkgDir:
            return

        # check if update is necessary
        checkVersions = version_check.version_check(workingDataPkgDir=workingDataPkgDir,trackersImplemented=self.trackersToAddToTool)
        allUpToDate = checkVersions[0]
        message = checkVersions[1]
        collectDf = checkVersions[2]
      
        if not allUpToDate: # at least one file is not up to date
            # create a copy of working data pkg dir in which to do the update - 
            # at the end can clean up but don't want the possibility that the update fails and the original is corrupted in the process
            # if an update in progress folder already exists exit with informative message - this may indicate that the user had a previously failed update since a successful update would lead to clean up of this folder
            
            if not dsc_pkg_utils.copyDataPkgDirToUpdate(workingDataPkgDir): # couldn't create update Dir because already exists
                messageText = "<br>Updates are needed. However, an update of your working data package directory may already be in progress. Check for a folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\". If this folder exists, an update may have been initiated but not completed. If you didn't purposely create or keep this folder, please delete this folder and then come back here and try to update again. <br>"
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return
            else: # created update dir (copy of working data pkg dir at same level with update-in-progress appended to orig name)
                messageText = "<br>Updates are needed. An \"update-in-progress\" version of your working data package directory has been successfully created - This copy will be used to perform the updates and will be cleaned up at the end of a successful update - You should see a new folder in the same parent directory as your working data package directory that starts with \"dsc-pkg\" and ends with \"update-in-progress\".<br><br>Working on updates..<br>"
                saveFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            
                # a copy of the working data package dir and the operational subdir has been created in the update in progress dir
                # need to update the tracker and json txt file paths in collectDf to reflect the versions in the update in progress dir
                # so that updates will be made to the versions in that dir instead of the original working data pkg dir
                updateDir = dsc_pkg_utils.getDataPkgDirToUpdate(workingDataPkgDir)

                # strip original working data pkg dir from filenames
                collectDf["file"] = [os.path.basename(p) for p in collectDf["file"]]
                # add update in progress working data pkg dir to filenames
                collectDf["file"] = [os.path.join(updateDir,p) for p in collectDf["file"]]
              
            if "tracker" in collectDf["fileType"].values: # at least one tracker exists in update dir
                
                trackerDf = collectDf[collectDf["fileType"] == "tracker"]

                messageText = "<br>The following csv trackers were detected:<br>" + "<br>".join(trackerDf["file"].tolist())
                self.userMessageBox.append(messageText)
                                
                if "No" in trackerDf["upToDate"].values: # at least one tracker is not up to date
                    trackerDfNeedsUpdate = trackerDf[trackerDf["upToDate"] == "No"]

                    messageText = "<br>The following csv trackers need to be updated:<br>" + "<br>".join(trackerDfNeedsUpdate["file"].tolist())
                    self.userMessageBox.append(messageText)
                    
                    if "Yes" in trackerDfNeedsUpdate["canBeUpdated"].values: # at least one tracker can be updated
                        trackerDfCanBeUpdated = trackerDfNeedsUpdate[trackerDfNeedsUpdate["canBeUpdated"] == "Yes"]

                        messageText = "<br>The following csv trackers need to be updated AND can be updated:<br>" + "<br>".join(trackerDfCanBeUpdated["file"].tolist()) + "<br><br>Starting updates<br>"
                        self.userMessageBox.append(messageText)
                        QtWidgets.QApplication.processEvents() # print accumulated user status messages 

                        # update the trackers here
                        trkPathList = trackerDfCanBeUpdated["file"].tolist()
                        trkTypeCamelCaseList = trackerDfCanBeUpdated["trackerType"].tolist()
                        trkUpdateStatusList = []
                        for p,t in zip(trkPathList,trkTypeCamelCaseList):
                            t_trkDict = [i for i in self.trackersToAddToTool if i["trackerNameCamelCase"] == t]
                            t_trkDict = t_trkDict[0]

                            trkUpdateStatus = version_update_tracker.version_update_tracker(getTrk=p,trkDict=t_trkDict)
                            trkUpdateStatusList.append(trkUpdateStatus)
                            if trkUpdateStatus:
                                messageText = "<br>The following " + t + " was successfully updated:<br>" + p + "<br>"
                                saveFormat = '<span style="color:green;">{}</span>'
                                self.userMessageBox.append(saveFormat.format(messageText))

                                # update json txt annotation files that were added to the tracker by writing 
                                # new json txt annotation files based on contents of updated tracker
                                # 1) check if all json txt annotation files in working data pkg dir have been added to the tracker
                                # 2)    for those not added, check if valid
                                # 3)        for those not added, if valid, update json directly and add to tracker
                                # 4)        for those not added, if invalid, attempt to update the json directly anyway, and somehow alert user to check these files and correct them
                                # 5)    for those added, write new json txt annotation file based on updated tracker contents for the annotation

                                print("reading in tracker")
                                trackerDf = pd.read_csv(p)
                                trackerDf.fillna("", inplace = True)
                                trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])

                                idCol = t_trkDict["trackerIdLabel"]
                                idNumCol = t_trkDict["trackerIdNumberLabel"]
                                jsonTxtPrefix = t_trkDict["trackerJsonFilePrefix"] + t_trkDict["trackerIdPrefix"]
                                schema = t_trkDict["schema"]

                                # get the array type properties in this tracker
                                # when pulling in from tracker, they will have become stringified lists instead of 
                                # true lists and will be incorrectly converted into json if not updated appropriately
                                arrayTypeProps = []
                                for key in schema["properties"]:
                                    if schema["properties"][key]["type"] == "array":
                                        arrayTypeProps.append(key) 

                                # get id nums based on updated tracker
                                # if the tracker is empty, id nums in tracker is empty list
                                if trackerDf.empty:
                                    idNumFromTrackerList = []
                                else:
                                    # make sure the id num is an integer here 
                                    trackerDf[idNumCol] = trackerDf[idNumCol].astype(int)
                                    # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
                                    # to get the latest annotation entry
                                    trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
                                    trackerDf.drop_duplicates(subset=[idNumCol],keep="last",inplace=True)

                                    idNumFromTrackerList = trackerDf[idNumCol].tolist()
                                    print("idNumFromTrackerList: ",idNumFromTrackerList)
                                    
                                # get id nums based on annotation files that already exist
                                existingFileList = [filename for filename in os.listdir(updateDir) if filename.startswith(jsonTxtPrefix)]

                                if existingFileList: # if the list is not empty
                                    existingFileStemList = [Path(filename).stem for filename in existingFileList]
                                    existingFileIdNumList = [int(filename.split(jsonTxtPrefix)[1]) for filename in existingFileStemList]
                                else: 
                                    existingFileIdNumList = []
                                
                                # get the id nums in just annotation file, just tracker, or both (list of json txt annotation files that have and have not already been added to tracker - also check if some annotations added to tracker with no corresponding annotation file)
                                if not idNumFromTrackerList:
                                    if not existingFileIdNumList:
                                        print("NO json txt annotation files, and NO annotations in the tracker - There are no json txt annotation files to update or write")
                                        continue
                                    else:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = []
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = []
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = existingFileIdNumList
                                else:
                                    if not existingFileIdNumList:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = idNumFromTrackerList
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = []
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = []
                                    else:
                                        # in tracker, no json txt annotation file - this shouldn't happen unless someone added to tracker manually or using another tool
                                        inTrackerNotInTxtFileIdNumList = [n for n in idNumFromTrackerList if n not in existingFileIdNumList]
                                        # in tracker, with corresponding json txt annotation file - this should be most common especially if using updated tool
                                        inTrackerInTxtFileIdNumList = [n for n in existingFileIdNumList if n in idNumFromTrackerList]
                                        # NOT in tracker, with a json txt annotation file - this may happen if the using an old version of the tool that does not auto add to tracker OR if the json txt file failed validation during the add to tracker step
                                        notInTrackerInTxtFileIdNumList = [n for n in existingFileIdNumList if n not in idNumFromTrackerList]

                                print("inTrackerNotInTxtFileIdNumList: ",inTrackerNotInTxtFileIdNumList)
                                print("inTrackerInTxtFileIdNumList: ",inTrackerInTxtFileIdNumList)
                                print("notInTrackerInTxtFileIdNumList: ",notInTrackerInTxtFileIdNumList)

                                writeFromTrackerToTxtFileIdNumList = inTrackerNotInTxtFileIdNumList + inTrackerInTxtFileIdNumList
                                
                                if writeFromTrackerToTxtFileIdNumList:
                                    writeFromTrackerToTxtFileDf = trackerDf[trackerDf[idNumCol].isin(writeFromTrackerToTxtFileIdNumList)]
                                              
                                    if arrayTypeProps:
                                        for a in arrayTypeProps:
                                            writeFromTrackerToTxtFileDf[a] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(x) for x in writeFromTrackerToTxtFileDf[a]]
                                        
                                    writeFromTrackerToTxtFileDfToJson = writeFromTrackerToTxtFileDf.to_json(orient="records")
                                    writeFromTrackerToTxtFileDfToJsonParsed = json.loads(writeFromTrackerToTxtFileDfToJson)
                                    
                                    messageText = "<br>It was used to successfully update the following json txt annotation files:<br>"

                                    #for n,p in zip(writeFromTrackerToTxtFileIdNumList,writeFromTrackerToTxtFileFnameList):
                                    for j in writeFromTrackerToTxtFileDfToJsonParsed:
                                        fname = jsonTxtPrefix + str(int(j[idNumCol])) + '.txt'
                                        fpath = os.path.join(updateDir,fname)
                                        jFinal = json.dumps(j, indent=4)
                                        with open(fpath, "w") as outfile:
                                            outfile.write(jFinal)
                                        
                                        messageText = messageText + fpath + "<br>"  
                                    
                                    saveFormat = '<span style="color:green;">{}</span>'
                                    self.userMessageBox.append(saveFormat.format(messageText))


                                if notInTrackerInTxtFileIdNumList:
                                    notInTrackerInTxtFileIdNumStringList = [str(idNum) for idNum in notInTrackerInTxtFileIdNumList]
                                    notInTrackerInTxtFileFnameList = [jsonTxtPrefix + idNumString + ".txt" for idNumString in notInTrackerInTxtFileIdNumStringList]
                                    notInTrackerInTxtFileFpathList = [os.path.join(updateDir,fname) for fname in notInTrackerInTxtFileFnameList]

                                    # 1) add content from each of the json txt annotation files to a df
                                    # 2) write the df to file as a temporary tracker
                                    # 3) run update tracker function on that temp tracker file
                                    # 4) write updated json txt annotation files to file (overwriting old json txt annotation files)
                                    # 5) read in content from each of updated json txt annotation files, and check if valid against schema
                                    # 6) if valid add to appropriate tracker(s)

                                    # 1) add content from each of the json txt annotation files to a df
                                    # initialize an empty dataframe to collect data from each file in ifileName
                                    # one row will be added to collect_df for each valid file in ifileName
                                    collect_df = pd.DataFrame([])
                                    # load data from json txt annotation file and convert to python object
                                    for p1 in notInTrackerInTxtFileFpathList:
                                    
                                        data = json.loads(Path(p1).read_text())
                                        # convert json to pd df
                                        df = pd.json_normalize(data) # df is a one row dataframe
                                        #print(df)
                                        # add this file's data to the dataframe that will collect data across all json txt annotation data files
                                        collect_df = pd.concat([collect_df,df], axis=0) 
                                        #print("collect_df rows: ", collect_df.shape[0])

                                    # 2) write the df to file as a temporary tracker
                                    tempTrkPath = os.path.join(updateDir,"temp-tracker.csv")
                                    collect_df.to_csv(tempTrkPath, mode='w', header=True, index=False)
                                    
                                    # 3) run update tracker function on that temp tracker file
                                    tempTrkUpdateStatus = version_update_tracker.version_update_tracker(getTrk=tempTrkPath,trkDict=t_trkDict)
                                    
                                    # 4) write updated json txt annotation files to file (overwriting old json txt annotation files)
                                    if tempTrkUpdateStatus:
                                        trackerDf = pd.read_csv(tempTrkPath)
                                        trackerDf.fillna("", inplace = True)
                                        trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])

                                        # idCol = t_trkDict["trackerIdLabel"]
                                        # idNumCol = t_trkDict["trackerIdNumberLabel"]
                                        # jsonTxtPrefix = t_trkDict["trackerJsonFilePrefix"] + t_trkDict["trackerIdPrefix"]
                                        # schema = t_trkDict["schema"]

                                        # get the array type properties in this tracker
                                        # when pulling in from tracker, they will have become stringified lists instead of 
                                        # true lists and will be incorrectly converted into json if not updated appropriately
                                        arrayTypeProps = []
                                        for key in schema["properties"]:
                                            if schema["properties"][key]["type"] == "array":
                                                arrayTypeProps.append(key) 

                                        writeFromTrackerToTxtFileDf = trackerDf
                                        if arrayTypeProps:
                                            for a in arrayTypeProps:
                                                writeFromTrackerToTxtFileDf[a] = [dsc_pkg_utils.convertStringifiedArrayOfStringsToList(x) for x in writeFromTrackerToTxtFileDf[a]]

                                        writeFromTrackerToTxtFileDfToJson = writeFromTrackerToTxtFileDf.to_json(orient="records")
                                        writeFromTrackerToTxtFileDfToJsonParsed = json.loads(writeFromTrackerToTxtFileDfToJson)
                                        
                                        messageText = "<br>A temporary " + t + " was used to successfully update the following json txt annotation files:<br>"

                                        #for n,p in zip(writeFromTrackerToTxtFileIdNumList,writeFromTrackerToTxtFileFnameList):
                                        for j in writeFromTrackerToTxtFileDfToJsonParsed:
                                            fname = jsonTxtPrefix + str(int(j[idNumCol])) + '.txt'
                                            fpath = os.path.join(updateDir,fname)
                                            jFinal = json.dumps(j, indent=4)
                                            with open(fpath, "w") as outfile:
                                                outfile.write(jFinal)
                                            
                                            messageText = messageText + fpath + "<br>"  
                                        
                                        saveFormat = '<span style="color:green;">{}</span>'
                                        self.userMessageBox.append(saveFormat.format(messageText))

                                        # 5) read in content from each of updated json txt annotation files, and check if valid against schema - 
                                        # if valid collect into a df
                                        
                                        # initialize lists to collect valid and invalid files
                                        validFiles = []
                                        invalidFiles = []
                                        # initialize an empty dataframe to collect data from each file in ifileName
                                        # one row will be added to collect_df for each valid file in ifileName
                                        collect_df = pd.DataFrame([])
                                        # load data from json txt annotation file and convert to python object
                                        for p2 in notInTrackerInTxtFileFpathList:
                                        
                                            data = json.loads(Path(p2).read_text())
                                            # get schema
                                            #TODO: check if schema has custom schema key customDynamicEnums and implement if there
                                            #schema = dsc_pkg_utils.getTrackerValidationSchema(trackerType=t, workingDataPkgDir=updateDir)
                                            
                                            # validate json txt annotation file content against schema
                                            # for results and resource tracker, this should be the dynamically created schema with experimentNameBelongsTo enum populated with experiment names from experiment tracker
                                            out = schema_utils.validate_against_jsonschema(data, schema) 
                                            if not out["valid"]:
                                                # add file to list of invalid files
                                                invalidFiles.append(p2)
                                                continue
                                            else: 
                                                # add file to list of valid files
                                                validFiles.append(p2) 
                                                # convert json to pd df
                                                df = pd.json_normalize(data) # df is a one row dataframe
                                                #print(df)
                                                # add this file's data to the dataframe that will collect data across all json txt annotation data files
                                                collect_df = pd.concat([collect_df,df], axis=0) 
                                                #print("collect_df rows: ", collect_df.shape[0])
                                        
                                        # 6) if valid add to appropriate tracker(s)

                                        if validFiles: 
                                            # open appropriate tracker, append collect_df, save
                                            print("add these valid files to tracker")
                                            trackerDf = pd.read_csv(p)
                                            trackerDf.fillna("", inplace = True)
                                            trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])
                                            
                                            collect_df["annotationModTimeStamp"] = pd.to_datetime(collect_df["annotationModTimeStamp"])
                                            
                                            trackerDf = pd.concat([trackerDf,collect_df],axis=0)
                                            trackerDf = trackerDf.sort_values([idNumCol, "annotationModTimeStamp"], ascending=[True, True])
                                            trackerDf = trackerDf[-(trackerDf.astype('string').duplicated())]
                                            trackerDf.to_csv(p, header=True, index=False)

                                    messageText = "<br>The following json txt annotation files had not previously been added to the appropriate tracker:<br>" + "<br>".join(notInTrackerInTxtFileFpathList) + "<br>"
                                    if not invalidFiles:
                                        messageText = messageText + "<br>All of these json txt annotation files were added to the appropriate tracker during the update.<br>"
                                        saveFormat = '<span style="color:green;">{}</span>'                                    
                                    else:
                                        if not validFiles:
                                            messageText = messageText + "<br>None of these json txt annotation files were added to the appropriate tracker during the update. This is likely because they did not pass validation against the schema. Please check these json txt annotation files for validity, fix any violations, and try again!<br>"
                                            saveFormat = '<span style="color:red;">{}</span>'
                                        else: 
                                            messageText = messageText + "<br>The following json txt annotation files were added to the appropriate tracker during the update:<br>" + "<br>".join(validFiles) + "<br>"
                                            messageText = messageText + "<br>The following json txt annotation files were NOT added to the appropriate tracker during the update:<br>" + "<br>".join(invalidFiles) + "<br>This is likely because they did not pass validation against the schema. Please check these json txt annotation files for validity, fix any violations, and try again!<br>"
                                            saveFormat = '<span style="color:blue;">{}</span>'

                                    self.userMessageBox.append(saveFormat.format(messageText))
                            else:
                                messageText = "<br>The following " + t + " was NOT successfully updated:<br>" + p + "<br>"
                                saveFormat = '<span style="color:red;">{}</span>'
                                self.userMessageBox.append(saveFormat.format(messageText))
                            QtWidgets.QApplication.processEvents() # print accumulated user status messages 

                        # if all trackers of a specific type are successfully updated, 
                        # update the schema version operational txt file
                        trkUpdateStatusDf = pd.DataFrame({"trackerType":trkTypeCamelCaseList,"file":trkPathList,"updateStatus":trkUpdateStatusList}) 
                        for t in trkUpdateStatusDf["trackerType"].unique().tolist():
                            filterDf = trkUpdateStatusDf[trkUpdateStatusDf["trackerType"] == t]
                            t_trkDict = [i for i in self.trackersToAddToTool if i["trackerNameCamelCase"] == t]
                            t_trkDict = t_trkDict[0]
                            if filterDf["updateStatus"].all():
                                trackerTypeHyphen = t_trkDict["trackerName"]
                                versionTxtFileName = "schema-version-" + trackerTypeHyphen + ".txt"
                                versionTxtFilePath = os.path.join(updateDir,"no-user-access",versionTxtFileName)
                                versionText = t_trkDict["schemaVersionMap"]["latestVersion"]

                                if os.path.isfile(versionTxtFilePath):
                                    with open(versionTxtFilePath, "r+") as text_file:
                                        # opening in r+ means pointer is initially at start of file
                                        text = text_file.read()
                                        # after reading pointer will be at end of file, so writing will result in append
                                        if not text.endswith('\n'):
                                            text_file.write('\n')
                                        text_file.write(versionText)
                                else:
                                    with open(versionTxtFilePath, "w") as text_file:
                                        text_file.write(versionText)
                    
                    else: # at least one tracker needs to be updated but none can be updated
                        messageText = "<br>None of the csv trackers that need to be updated can be updated. This is likely because schema version mapping files for these trackers are not up to date."
                        self.userMessageBox.append(messageText)
                         


                else: # all trackers are up to date
                    messageText = "<br>All csv trackers are up to date - json txt file updates coming soon<br>"
                    saveFormat = '<span style="color:orange;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    
                    origDir = workingDataPkgDir
                    os.rename(origDir,origDir + "-archive")
                    os.rename(updateDir,origDir)
                    
                    messageText = "<br>Your original working Data Package Directory has been archived as the original directory name plus \"-archive\".<br>"
                    saveFormat = '<span style="color:green;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                    return
            
            else: # no trackers in update dir
                messageText = "<br>No csv trackers were detected - json txt file updates coming soon<br>"
                saveFormat = '<span style="color:orange;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                
                origDir = workingDataPkgDir
                os.rename(origDir,origDir + "-archive")
                os.rename(updateDir,origDir)
                
                messageText = "<br>Your original working Data Package Directory has been archived as the original directory name plus \"-archive\".<br>"
                saveFormat = '<span style="color:green;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
                return

            
            origDir = workingDataPkgDir
            os.rename(origDir,origDir + "-archive")
            #os.rename(updateDir,origDir)
            dsc_pkg_utils.robustRename(src=updateDir,dst=origDir)
            
            messageText = "<br>Your original working Data Package Directory has been archived as the original directory name plus \"-archive\".<br>"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        
        else: # all files are up to date

            messageText = "<br>All dsc files are up to date - no updates needed!<br>"
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
            return

    