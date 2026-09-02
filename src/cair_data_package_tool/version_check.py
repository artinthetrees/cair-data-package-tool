from packaging import version
import pandas as pd
import os
import json

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils
import cair_data_package_tool.back_door_edit as back_door_edit

def version_check(workingDataPkgDir: str,trackersImplemented: list,operationalFilesList = ["resources-to-add.csv","annotation-mode-status.csv","share-status.csv"],writeVersionCheckToFile=True):

    # you're going to save this in the no user access folder since this is essentially an operational file
    operationalFileSubDir = os.path.join(workingDataPkgDir,back_door_edit.operationalFileSubdirName)

    # add a little check to make sure the operational file no user access folder exists and if not, create it
    # these operational files and the folder to store them were a later addition
    if os.path.isdir(operationalFileSubDir):
        pass
    else:
        os.mkdir(operationalFileSubDir)

    # add a little check to make sure all the operational files are in the operational file no user access folder
    # since these were saved outside in the working data pkg dir for a short while
    if operationalFilesList:
        for f in operationalFilesList:
            if f in os.listdir(workingDataPkgDir):
                os.rename(os.path.join(workingDataPkgDir,f), os.path.join(operationalFileSubDir,f))

    cols = ["trackerType","fileType","schemaVersion","schemaMapVersion","file","fileSchemaVersion","upToDate","canBeUpdated","canBeUpdatedFully","message"]
    collectDf = pd.DataFrame([],columns=cols)

    for i in trackersImplemented:
        trackerNameCamelCase = i["trackerNameCamelCase"]
        print("processing: ",trackerNameCamelCase)
                
        # get the latest/current schema version
        schema = i["schema"]
        schemaVersion = schema["version"]
        schemaVersionParse = version.parse(schemaVersion)
        
        # get the latest schema map version (this could be behind the latest schema version if 
        # there's not yet a map to the latest version available)
        updateSchemaMap = i["schemaVersionMap"]
        schemaMapVersion = updateSchemaMap["latestVersion"]
        schemaMapVersionParse = version.parse(schemaMapVersion)

        if schemaMapVersionParse == schemaVersionParse:
            print("mapping file for ",trackerNameCamelCase," is up to date, and can be used to update to latest schema version: ",schemaVersion)
        elif schemaMapVersionParse < schemaVersionParse:
            print("mapping file for ",trackerNameCamelCase," is NOT up to date - it can NOT be used to update to latest schema version: ",schemaVersion, "\n however it can be used to update to schema version: ",schemaMapVersion)
        
        if i["oneOrMulti"] == "one":
            trkPathList = [os.path.join(workingDataPkgDir,i["trackerFileName"])]
        elif i["oneOrMulti"] == "multi":
            trkPathList = [os.path.join(workingDataPkgDir,f) for f in os.listdir(workingDataPkgDir) if f.startswith(i["trackerFileName"])]

        if trkPathList:
            trkTypeList = ["tracker"] * len(trkPathList)
        
        jsonTxtPathList = [os.path.join(workingDataPkgDir,f) for f in os.listdir(workingDataPkgDir) if f.startswith(i["trackerJsonFilePrefix"])]

        if jsonTxtPathList:
            jsonTxtTypeList = ["json txt"] * len(jsonTxtPathList)

        if ((trkPathList) and (jsonTxtPathList)):
            pathList = trkPathList + jsonTxtPathList
            typeList = trkTypeList + jsonTxtTypeList
        else:
            if trkPathList:
                pathList = trkPathList
                typeList = trkTypeList
            elif jsonTxtPathList:
                pathList = jsonTxtPathList
                typeList = jsonTxtTypeList
            else:
                print("no files for ",trackerNameCamelCase,"; moving on to next file type")
                continue

        for p,t in zip(pathList,typeList):  
            
            if t == "tracker":
                trkDf = pd.read_csv(p)
                if "schemaVersion" not in trkDf.columns:
                    fileVersion = "0.0.0" # not necessarily accurate, just indicating that it's not up to date
                else:
                    if trkDf.empty:

                        refSchemaVersionFileName = "schema-version-" + i["trackerName"] + ".txt"
                        refSchemaVersionFilePath = os.path.join(operationalFileSubDir,refSchemaVersionFileName)

                        if os.path.isfile(refSchemaVersionFilePath):
                            fileVersion = dsc_pkg_utils.read_last_line_txt_file(refSchemaVersionFilePath)
                        else:
                            fileVersion = "0.0.0" # not necessarily accurate, just indicating that it's not up to date
                    else:
                        fileVersion = trkDf["schemaVersion"][0]
            elif t == "json txt":
                with open(p, 'r', encoding='utf-8') as file:
                    # Load JSON data from file
                    data = json.load(file)
                if "schemaVersion" not in list(data.keys()):
                    fileVersion = "0.0.0" # not necessarily accurate, just indicating that it's not up to date
                else:
                    fileVersion = data["schemaVersion"]


            fileVersionParse = version.parse(fileVersion)

            if fileVersionParse == schemaVersionParse:
                upToDate = "Yes"
                canBeUpdated = "Not Applicable"
                canBeUpdatedFully = "Not Applicable"
                message = "File is up to date"
            elif fileVersionParse < schemaVersionParse:
                upToDate = "No"
                if fileVersionParse == schemaMapVersionParse:
                    canBeUpdated = "No"
                    canBeUpdatedFully = "Not Applicable"
                    message = "File is NOT up to date, but it cannot be updated at this time because the current schema mapping file does not allow updating beyond the file's current schema version"
                elif fileVersionParse < schemaMapVersionParse:
                    canBeUpdated = "Yes"
                    if schemaMapVersionParse == schemaVersionParse:
                        canBeUpdatedFully = "Yes"
                        message = "File is NOT up to date, and it can be fully updated at this time - Updating will update this file to the latest schema version"
                
                    elif schemaMapVersionParse < schemaVersionParse:
                        canBeUpdatedFully = "No"
                        message = "File is NOT up to date - It can be updated, but it cannot be FULLY updated at this time because the current mapping file does allow updating beyond the file's current version but does NOT allow updating to the latest schema version - Updating will update this file to the latest schema version for which the schema mapping file has been completed"

                    
            addDf = pd.DataFrame([[trackerNameCamelCase,t,schemaVersionParse,schemaMapVersionParse,p,fileVersionParse,upToDate,canBeUpdated,canBeUpdatedFully,message]], columns=cols)
            collectDf = pd.concat([collectDf,addDf],axis=0)
            
        
    collectDf['updateCheckDateTime'] = pd.Timestamp("now")
    strTimeStamp = str(pd.Timestamp("now")).replace(" ","-").replace(":","-").replace(".","-")
    outFilename = "update-check-" + strTimeStamp + ".csv"
    if writeVersionCheckToFile:
        collectDf.to_csv(os.path.join(operationalFileSubDir,outFilename), index = False)  
        
    message = ""

    if "No" in collectDf["upToDate"].values:

        allUpToDate = False

        messageDf1 = collectDf[collectDf["upToDate"] == "No"]
        message = message + "<br><b>WARNING:</b>At least one dsc-pkg file in your working Data Package Directory is NOT up to date - Please head to the \"Data Package\" tab >> \"Audit and Update\" sub-tab to update these dsc-pkg files before proceeding. Some details are provided below:<br><br>1. Out of " + str(collectDf.shape[0]) + " total dsc-pkg files, " + str(messageDf1.shape[0]) + " files are NOT up to date."
        
        if "Yes" in messageDf1["canBeUpdated"].values:
            messageDf2 = messageDf1[messageDf1["canBeUpdated"] == "Yes"]
            message = message + "<br>2. Out of " + str(messageDf1.shape[0]) + " total dsc-pkg files that are NOT up to date, " + str(messageDf2.shape[0]) + " files can be updated based on available version mapping files."
        
            if "Yes" in messageDf2["canBeUpdatedFully"].values:
                messageDf3 = messageDf2[messageDf2["canBeUpdatedFully"] == "Yes"]
                message = message + "<br>3. Out of " + str(messageDf2.shape[0]) + " total dsc-pkg files that are NOT up to date and can be updated, " + str(messageDf3.shape[0]) + " files can be fully updated based on available version mapping files - Updating will update these files to the latest/current schema version."

            else: 
                message = message + "<br>3. Out of " + str(messageDf2.shape[0]) + " total dsc-pkg files that are NOT up to date and can be updated, 0 files can be fully updated based on available version mapping files - Updating these files to latest/current schema version will require that version mapping files be updated to reflect mapping to latest/current schema versions."

            message = message + "<br><br>You can head to the \"Data Package\" tab >> \"Update Data Package\" sub-tab to update Standard Data Package Metadata files in your working Data Package Directory!<br>"
            
        else:
            message = message + "<br>2. Out of " + str(messageDf1.shape[0]) + " total dsc-pkg files that are NOT up to date, 0 files can be updated based on available version mapping files."
            
    else: 
        allUpToDate = True
        message = message + "All dsc-pkg files are up to date"        

    return [allUpToDate, message, collectDf]
    