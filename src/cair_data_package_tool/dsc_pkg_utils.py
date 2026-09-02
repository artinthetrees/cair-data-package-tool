import pandas as pd
import json # base python, no pip install needed

import os # base python, no pip install needed
import shutil # base python, no pip install needed

import pathlib
from jsonschema import validate
import re
from copy import deepcopy
from pathlib import Path
import errno
import time
from packaging import version

from healdata_utils.schemas import healcsvschema
from healdata_utils.transforms.frictionless import conversion

import cair_data_package_tool.back_door_edit as back_door_edit



# trkDict = {
        
#     "termTracker":{
#         "id": "termId",
#         "schema": schema_term_tracker.schema,
#         "updateSchemaMap": versions_term_tracker.fieldNameMap,
#         "oneOrMulti":"one",
#         "trackerName":"term-tracker.csv",
#         "trackerTypeHyphen":"term-tracker",
#         "trackerTypeMessageString":"Term Tracker",
#         "jsonTxtPrefix": "term-trk-term-",
#         "idPrefix": "term-"
#     },
#     "experimentTracker":{
#         "id": "experimentId",
#         "schema": schema_experiment_tracker.schema_experiment_tracker,
#         "updateSchemaMap": versions_experiment_tracker.fieldNameMap,
#         "oneOrMulti":"one",
#         "trackerName":"heal-csv-experiment-tracker.csv",
#         "trackerTypeHyphen":"experiment-tracker",
#         "trackerTypeMessageString":"Experiment Tracker",
#         "jsonTxtPrefix": "exp-trk-exp-",
#         "idPrefix": "exp-"
#     },
#     "resourceTracker":{
#         "id": "resourceId",
#         "schema": schema_resource_tracker.schema_resource_tracker,
#         "updateSchemaMap": versions_resource_tracker.fieldNameMap,
#         "oneOrMulti": "one",
#         "trackerName":"heal-csv-resource-tracker.csv",
#         "trackerTypeHyphen":"resource-tracker",
#         "trackerTypeMessageString":"Resource Tracker",
#         "jsonTxtPrefix": "resource-trk-resource-",
#         "idPrefix": "resource-"
#     },
#     "resultsTracker":{
#         "id": "resultId",
#         "schema": schema_results_tracker.schema_results_tracker,
#         "updateSchemaMap": versions_results_tracker.fieldNameMap,
#         "oneOrMulti": "multi",
#         "trackerName":"heal-csv-results-tracker-",
#         "trackerTypeHyphen":"results-tracker",
#         "trackerTypeMessageString":"Results Tracker",
#         "jsonTxtPrefix": "result-trk-result-",
#         "idPrefix": "result-"
#     }
    
# }

def relPathResultsDependOn(resultsDependOnListOfDicts, relToPath, pathKey="resultIdDependsOn"):
    # convert absolute paths in associatedFilesResultsDependOn field in resource tracker
    # res = [dict([key, os.path.relpath(p,workingDataPkgDir)] 
    #    for key, value in dicts.items()) 
    #    for dicts in resultsDependOnListOfDicts]
    print("resultsDependOnListOfDicts - before: ", resultsDependOnListOfDicts)
    for dict in resultsDependOnListOfDicts:
        print("dictBefore: ",dict)
        for key in dict:
            if key == pathKey:
                if dict[key]:
                    pathList = dict[key]
                    print(pathList)
                    print(isinstance(pathList,list))
                    #relPathList = [convertStringifiedArrayOfStringsToList(p) for p in pathList]
                    relPathList = [os.path.relpath(p,relToPath) if p else p for p in pathList] # if the rel path list contains empty string(s) leave then as empty strings; don't try to calc relative path bc will fail with no path specified error
                    relPathList = [i for i in relPathList if i] # remove any empty string(s) in rel path list
                    print(relPathList)
                    dict[key] = relPathList
        print("dictAfter: ",dict)
    print("resultsDependOnListOfDicts - before: ", resultsDependOnListOfDicts)  
    return resultsDependOnListOfDicts               
                

def robustRename(src, dst):
    # https://github.com/conan-io/conan/issues/6560
    """os.rename(src, dst) wrapper with support for long paths on Windows.

    Availability: Unix, Windows."""
    #if isWindows():
    if os.name == "nt":
    # On Windows, rename fails if destination exists, see
    # https://docs.python.org/2/library/os.html#os.rename
        try:
            os.rename(src, dst)
        except OSError as e:
            # if e.errno == errno.EEXIST:
            #     os.remove(dst)
            #     os.rename(src, dst)
            #elif e.errno == errno.EACCES:
            if e.errno == errno.EACCES:
                # Workaround for the sporadic problem on Windows:
                # PermissionError: [WinError 5] Access denied
                # Retry 3 times to rename with sleeping 500 ms in between
                retry = 5
                while retry:
                    #print("*** Retry: " + str(4 - retry))
                    time.sleep(0.5)
                    try:
                        os.rename(src, dst)
                        retry = 0
                    except OSError as e:
                        if retry and e.errno == errno.EACCES:
                            retry = retry - 1
                        else:
                            raise
            else:
                raise
    else:
        os.rename(src, dst)

# def getTrackerValidationSchema(trackerType, workingDataPkgDir=None):
#     t=trackerType
#     schema = trkDict[t]["schema"]

#     if t in ["resourceTracker","resultsTracker"]:
#         if not workingDataPkgDir:
#             print("i need the working data pkg dir to update experiment name belongs to enum values")
#             return
#         experimentNameList = []
#         experimentNameList, _ = get_exp_names(self=None, workingDataPkgDir=workingDataPkgDir, perResource=False) # gets self.experimentNameList

#         #print("self.experimentNameList: ",self.experimentNameList)
        
#         if experimentNameList:
#             #self.schema = self.add_exp_names_to_schema() # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList
#             schema = add_exp_names_to_schema(self=None,schema=schema,experimentNameList=experimentNameList) # uses self.experimentNameList and self.schema to update schema property experimentNameBelongs to be an enum with values equal to experimentNameList

#     return schema

# def writeJsonTxtAnnotationFromTracker(trackerPath,trackerType):
#     p=trackerPath
#     t=trackerType

#     workingDataPkgDir = Path(p).parent
    
#     print("reading in tracker")
    
#     trackerDf = pd.read_csv(p)
#     trackerDf.fillna("", inplace = True)
#     trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])
#     #print(trackerDf)
    
#     idCol = trkDict[t]["id"]
#     idNumCol = trkDict[t]["id"] + "Number"
#     jsonTxtPrefix = trkDict[t]["jsonTxtPrefix"]
#     schema = getTrackerValidationSchema(trackerType=t, workingDataPkgDir=workingDataPkgDir)

#     # get the array type properties in this tracker
#     # when pulling in from tracker, they will have become stringified lists instead of 
#     # true lists and will be incorrectly converted into json if not updated appropriately
#     arrayTypeProps = []
#     for key in schema["properties"]:
#         if schema["properties"][key]["type"] == "array":
#             arrayTypeProps.append(key) 

#     # get id nums based on updated tracker
#     # if the tracker is empty, id nums in tracker is empty list
#     if trackerDf.empty:
#         idNumFromTrackerList = []
#         print("no json txt files to write")
#         messageText = "no json txt files to write from this tracker"
#         return
#     else:
#         # make sure the id num is an integer here 
#         trackerDf[idNumCol] = trackerDf[idNumCol].astype(int)
#         # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
#         # to get the latest annotation entry
#         trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
#         trackerDf.drop_duplicates(subset=[idNumCol],keep="last",inplace=True)

#     writeFromTrackerToTxtFileDf = trackerDf
#     if arrayTypeProps:
#         for a in arrayTypeProps:
#             writeFromTrackerToTxtFileDf[a] = [convertStringifiedArrayOfStringsToList(x) for x in writeFromTrackerToTxtFileDf[a]]
        
#     writeFromTrackerToTxtFileDfToJson = writeFromTrackerToTxtFileDf.to_json(orient="records")
#     writeFromTrackerToTxtFileDfToJsonParsed = json.loads(writeFromTrackerToTxtFileDfToJson)
    
#     messageText = "<br>"+ t + ": "+ p +"<br>The " + t + " was used to successfully update the following json txt annotation files:<br>"

#     #for n,p in zip(writeFromTrackerToTxtFileIdNumList,writeFromTrackerToTxtFileFnameList):
#     for j in writeFromTrackerToTxtFileDfToJsonParsed:
#         fname = jsonTxtPrefix + str(int(j[idNumCol])) + '.txt'
#         fpath = os.path.join(workingDataPkgDir,fname)
#         jFinal = json.dumps(j, indent=4)
#         with open(fpath, "w") as outfile:
#             outfile.write(jFinal)
        
#         messageText = messageText + fpath + "<br>"  
    
#     return messageText

def process_json_schema_validation_result(validate_against_jsonschema_result,self=None):
    out = validate_against_jsonschema_result

    # if not valid, print validation errors and exit 
    if not out["valid"]:
        
        # get validation errors to print
        printErrListSingle = []
        # initialize the final full validation error message for this file to start with the filename
        printErrListAll = []
    
        for e in out["errors"]:
            printErrListSingle.append(str(''.join(e["absolute_path"])))
            printErrListSingle.append(str(e["validator"]))
            printErrListSingle.append(str(e["validator_value"]))
            printErrListSingle.append(str(e["message"]))

            printErrSingle = '\n'.join(printErrListSingle)
            printErrListAll.append(printErrSingle)
        
        printErrAll = '\n\n'.join(printErrListAll)
    
        messageText = "The form data is NOT valid and will not be saved until validation errors are fixed." + "\n\n" + "Validation errors are as follows: " + "\n\n" + printErrAll + "\n\n"

        if self: 
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        else:
            print(messageText)
        return False
    else:
        return True

# def validateFormData(formData,schema,self):
#     if self:
#         schema=self.schema
#     # validate tracker form json content against tracker json schema
#     out = validate_against_jsonschema(formData, schema)
    
#     # if not valid, print validation errors and exit 
#     if not out["valid"]:
        
#         # get validation errors to print
#         printErrListSingle = []
#         # initialize the final full validation error message for this file to start with the filename
#         #printErrListAll = [ifileNameStem]
#         printErrListAll = []
    
#         for e in out["errors"]:
#             printErrListSingle.append(''.join(e["absolute_path"]))
#             printErrListSingle.append(e["validator"])
#             printErrListSingle.append(e["validator_value"])
#             printErrListSingle.append(e["message"])

#             print(printErrListSingle)
#             printErrSingle = '\n'.join(printErrListSingle)
#             printErrListAll.append(printErrSingle)

#             # printErrListSingle = []
#             # printErrSingle = ""
        
#         printErrAll = '\n\n'.join(printErrListAll)
    
#         #messageText = "The following resource file is NOT valid and will not be added to your Resource Tracker file: " + ifileName + "\n\n\n" + "Validation errors are as follows: " + "\n\n\n" + ', '.join(out["errors"]) + "\n\n\n" + "Exiting \"Add Resource\" function now."
#         messageText = "The form data is NOT valid and will not be saved until validation errors are fixed." + "\n\n" + "Validation errors are as follows: " + "\n\n" + printErrAll + "\n\n"
#         #self.userMessageBox.append(messageText)

#         if self: 
#             saveFormat = '<span style="color:red;">{}</span>'
#             self.userMessageBox.append(saveFormat.format(messageText))
#         else:
#             print(messageText)
#         return False
#     else:
#         return True

def getDataPkgDirStem(workingDataPkgDir):
    getDir = workingDataPkgDir
    getDirPath = pathlib.Path(getDir)

    # get the stem/name of the working data package dir so that can reproduce it (e.g. may be dsc-pkg-my-study instead of just dsc-pkg, or dsc-pkg name may change over time)
    getDirName = getDirPath.stem

    return getDirName

def getDataPkgDirParent(workingDataPkgDir):
    getDir = workingDataPkgDir
    getDirPath = pathlib.Path(getDir)

    # get the parent dir of the working data package dir path (should be the overall study folder)
    getParentOfDirPath = getDirPath.parent

    return getParentOfDirPath

def getDataPkgDirToUpdate(workingDataPkgDir):
    getDir = workingDataPkgDir
    #getDirPath = pathlib.Path(getDir)

    # get the stem/name of the working data package dir so that can reproduce it (e.g. may be dsc-pkg-my-study instead of just dsc-pkg, or dsc-pkg name may change over time)
    #getDirName = getDirPath.stem
    getDirName = getDataPkgDirStem(workingDataPkgDir=getDir)

    # get the parent dir of the working data package dir path (should be the overall study folder)
    #getParentOfDirPath = getDirPath.parent
    getParentOfDirPath = getDataPkgDirParent(workingDataPkgDir=getDir)

    # in the overall study folder copy the working data pkg dir contents to an update in progress version of the working data pkg dir
    getUpdateDirName = getDirName + "-update-in-progress" 
    getUpdateDirPath = os.path.join(getParentOfDirPath,getUpdateDirName)

    return getUpdateDirPath

def copyDataPkgDirToUpdate(workingDataPkgDir):
    getDir = workingDataPkgDir
    
    getUpdateDirPath = getDataPkgDirToUpdate(workingDataPkgDir=getDir)

    # path to source directory
    src_dir = getDir
    # path to destination directory
    dest_dir = getUpdateDirPath

    if os.path.isdir(dest_dir):
        return False
    else:
        # copy all contents of src to dest
        shutil.copytree(src_dir, dest_dir)
        return True


def checkTrackerCreatedSchemaVersionAgainstCurrent(trackerDict=None,workingDataPkgDir=None,self=None):
    
    """ check current schema version for a tracker type against the version under which tracker in specified workingDataPkgDir was created; use to determine if the workingDataPkgDir needs to be updated to newer schema version
    
    Arguments:
    
    trackerDict -- dictionary; required if self not provided; output from getTrackerVars fx, which itself takes as input trackerDict from py file that defines schema and trackerDict for the tracker this annotation belongs to (i.e. if this is a term annotation, then the term tracker which has schema and trackerDict defined in schema_term_tracker.py)
    workingDataPkgDir -- string; required if self not provided; full file path to folder in which annotation files and tracker are saved
    
    self -- instance of layout_general_scrollannotate_widget

    """
    if self:
        trackerDict = self.trackerDict
        workingDataPkgDir = self.workingDataPkgDir
    else:
        trackerDict = trackerDict
        workingDataPkgDir = workingDataPkgDir

    trackerTypeFileNameString = trackerDict["trackerName"]
    trackerTypeMessageString = trackerDict["trackerTitle"]
    schemaVersion = trackerDict["schemaVersion"]

    # check self.schemaVersion against version in operational schema version file 
    # if no operational schema version file exists OR 
    # if version in operational schema version file is less than self.schemaVersion 
    # return with message that update of tracker version is needed before new annotations can be added
    operationalFileSubDir = os.path.join(workingDataPkgDir,back_door_edit.operationalFileSubdirName)
    fname = "schema-version-" + trackerTypeFileNameString + ".txt"
    trackerCreatedSchemaVersionFile = os.path.join(operationalFileSubDir,fname)
    if os.path.isdir(operationalFileSubDir):
        print("oper dir exists")
        if os.path.isfile(trackerCreatedSchemaVersionFile):
            print("version file exists")
            trackerCreatedSchemaVersion = read_last_line_txt_file(trackerCreatedSchemaVersionFile)
        else:
            print("version file does not exist")
            trackerCreatedSchemaVersion = "0.0.0" # not necessarily accurate, just indicating that it's not up to date
    else: 
        print("oper dir does not exist")
        trackerCreatedSchemaVersion = "0.0.0" # not necessarily accurate, just indicating that it's not up to date

    trackerCreatedSchemaVersionParse = version.parse(trackerCreatedSchemaVersion)
    currentTrackerVersionParse = version.parse(schemaVersion)

    print("trackerCreatedSchemaVersionParse: ",trackerCreatedSchemaVersionParse)
    print("currentTrackerVersionParse: ",currentTrackerVersionParse)

    if trackerCreatedSchemaVersionParse != currentTrackerVersionParse:
        if trackerCreatedSchemaVersionParse < currentTrackerVersionParse:
            messageText = "<br>The " + trackerTypeMessageString + " file in your working Data Package Directory was created under an outdated schema version. Update of tracker version is needed before new annotations can be added or existing annotations can be edited. Head to the \"Data Package\" tab >> \"Audit & Update\" sub-tab to update, then come back and try again. <br>"
            if self:
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            else:
                print(messageText)   
        else:
            messageText = "<br>It appears that the " + trackerTypeMessageString + " file in your working Data Package Directory was created under a schema version that is later than the current schema version. Something is not right. Please reach out to the DSC team for help. <br>"
            if self:
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            else:
                print(messageText)
        return False
    else:
        messageText = "<br>The " + trackerTypeMessageString + " file in your working Data Package Directory was created under the current schema version. You may proceed with adding new items.<br>"
        if self:
            saveFormat = '<span style="color:green;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
        else:
            print(messageText)
        return True

def read_last_line_txt_file(txtFile):
    #import os
    #https://www.logilax.com/python-read-last-line-of-file/
    with open(txtFile, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()
    
    return last_line
    
def renameDictKeys(myDictionary,keyRenameDictionary):
    print("myDictionary: ",myDictionary)
    for k, v in list(myDictionary.items()):
        myDictionary[keyRenameDictionary.get(k, k)] = myDictionary.pop(k)

def renameListOfDictKeys(myDictionaryList,keyRenameDictionary):
    print("myDictionaryList: ",myDictionaryList)
    if myDictionaryList == '[]':
        print("value is an empty list")
        return []  
    else: 
        myDictionaryList = list(eval(myDictionaryList))
        for d in myDictionaryList:
            print("value is not an empty list:", d)
            for k, v in list(d.items()):
                d[keyRenameDictionary.get(k, k)] = d.pop(k)

        return myDictionaryList

def convertStringifiedArrayOfStringsToList(myStringifiedArrayOfStrings):
    
    if isinstance(myStringifiedArrayOfStrings, list):
        return myStringifiedArrayOfStrings

    if myStringifiedArrayOfStrings == '[]':
        return []  
    else:
        myStringifiedArrayOfStrings = myStringifiedArrayOfStrings.replace("'","\"")
                
        # replacing single quote will also replace apostrophe - here revert apostrophe replacement
        #apostrophe_regex_string = "(?<=[A-Za-z])\"(?=[A-Za-z])"
        myStringifiedArrayOfStrings = re.sub(r"(?<=[A-Za-z])\"(?=[A-Za-z])","'",myStringifiedArrayOfStrings)
        myStringifiedArrayOfStrings = json.loads(myStringifiedArrayOfStrings)
                
        return myStringifiedArrayOfStrings

def mapArrayOfStrings(myStringArray,stringMapDictionary):
    if myStringArray == '[]':
        return []  
    else: 
        myStringArray = myStringArray.replace("'","\"")
        myStringArray = json.loads(myStringArray)
        myStringArray = [stringMapDictionary.get(i,i) for i in myStringArray]
        return myStringArray

def deleteEmptyStringInArrayOfStrings(myStringArray):
    if myStringArray:
        if myStringArray == '[]':
            return []  
        else: 
            if not isinstance(myStringArray, list):
                myStringArray = myStringArray.replace("'","\"") # shouldn't be harmful to run this even if no single quotes
                myStringArray = json.loads(myStringArray)
            else: 
                pass
            
            myStringArray = [i for i in myStringArray if i]
            return myStringArray
    else: 
        return []

def getPositionOfWidgetInLayout(layout,getWidget):
    if layout is not None:
        for i in range(layout.count()):
            print(i)
            row, column, rowSpan, colSpan = layout.getItemPosition(i)
            item = layout.itemAt(i)
            widget = item.widget()
            if widget is not None:
                if widget == getWidget:
                    #print(i)
                    # print(widget)
                    # print(widget.text())
                    # print("row: ",row,"; column: ", column)
                    return [row,column]

def deleteItemsOfLayout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                deleteItemsOfLayout(item.layout())

def layoutInLayoutDelete(containerLayout,layoutInLayout):
    for i in range(containerLayout.count()):
        layout_item = containerLayout.itemAt(i)
        if layout_item.layout() == layoutInLayout:
            deleteItemsOfLayout(layout_item.layout())
            containerLayout.removeItem(layout_item)
            break

# def layoutInLayoutDelete(self,containerLayout,layoutInLayout):
#     for i in range(self.containerLayout.count()):
#         layout_item = self.containerLayout.itemAt(i)
#         if layout_item.layout() == layoutInLayout:
#             dsc_pkg_utils.deleteItemsOfLayout(layout_item.layout())
#             self.containerLayout.removeItem(layout_item)
#             break

def get_added_resource_paths(self, latestEntryOnly=False, includeRemovedEntry=True):
#def get_added_resource_paths():
    
    getDir = self.workingDataPkgDir
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getResourceTrk = os.path.join(getDir,"heal-csv-resource-tracker.csv")
    #getResourcesToAdd = os.path.join(getDir,"resources-to-add.csv")

    if os.path.isfile(getResourceTrk):
        resourceTrackerDf = pd.read_csv(getResourceTrk)
        resourceTrackerDf.fillna("", inplace = True)

        print(resourceTrackerDf)
        print(resourceTrackerDf.columns)

        if "path" in resourceTrackerDf.columns:

            resourceTrackerDf["annotationModDateTime"] = pd.to_datetime(resourceTrackerDf["annotationModDateTime"])
            
            # sort by date-time (ascending), then drop duplicates of, keeping the last/latest instance of each path's occurrence
            # to get the latest annotation entry
            resourceTrackerDf.sort_values(by=["annotationModDateTime"],ascending=True,inplace=True)

            if latestEntryOnly:
                resourceTrackerDf.drop_duplicates(subset=["resourceId"],keep="last",inplace=True)

            if not includeRemovedEntry:
                if "removed" in resourceTrackerDf.columns:
                    resourceTrackerDf = resourceTrackerDf[resourceTrackerDf["removed"] == 0]

            #experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
            resourcePathSeries = resourceTrackerDf["path"].astype(str)
            print(resourcePathSeries,type(resourcePathSeries))
            resourcePathList = resourcePathSeries.tolist()
            print(resourcePathList,type(resourcePathList))
            resourcePathList = [x for x in resourcePathList if x] # remove empty strings
            print(resourcePathList,type(resourcePathList))
            resourcePathList = list(dict.fromkeys(resourcePathList)) # deduplicate list
            print(resourcePathList,type(resourcePathList))

        else: 
            resourcePathList = []

    else:
        resourcePathList = []

    return resourcePathList

def get_tracker_entries(workingDataPkgDir=None, trackerDf = pd.DataFrame(), trackerType="resource-tracker", latestEntryOnly=False, includeRemovedEntry=True, excludeIdList=[], includeIdList=[]):
#def get_added_resource_paths():

    trackerTypeSub = trackerType.split("-tracker")[0]
    trackerIdString = trackerTypeSub + "Id"
    trackerIdNumString = trackerTypeSub + "IdNumber"

    if trackerDf.empty:
        fileName = trackerType + ".csv"
        
        getDir = workingDataPkgDir
        getTrk = os.path.join(getDir,fileName)
        
        if os.path.isfile(getTrk):
            trackerDf = pd.read_csv(getTrk)
        else:
            return False

    # at this point, should have trackerDf either provided as an input param or loaded from file; otherwise should have exited fx
    trackerDf.fillna("", inplace = True)
    trackerDf["annotationModDateTime"] = pd.to_datetime(trackerDf["annotationModDateTime"])
    # sort by date-time (ascending), then drop duplicates of, keeping the last/latest instance of each path's occurrence
    # to get the latest annotation entry
    trackerDf.sort_values(by=["annotationModDateTime"],ascending=True,inplace=True)

    if latestEntryOnly:
        trackerDf.drop_duplicates(subset=[trackerIdString],keep="last",inplace=True)

    if not includeRemovedEntry:
        if "removed" in trackerDf.columns:
            trackerDf = trackerDf[trackerDf["removed"] == 0]

    if excludeIdList:
        trackerDf = trackerDf[~trackerDf[trackerIdString].isin(excludeIdList)]
           
    if includeIdList:
        trackerDf = trackerDf[trackerDf[trackerIdString].isin(includeIdList)]
        
    # convert annotationModDateTime back to string
    trackerDf["annotationModDateTime"] = trackerDf["annotationModDateTime"].dt.strftime('%Y-%m-%d, %H:%M:%S')
    
    print(trackerIdNumString)
   
    trackerDf[trackerIdNumString] = trackerDf[trackerIdNumString].astype(int)
    trackerDf.sort_values(by=[trackerIdNumString],ascending=True,inplace=True)
    trackerDf[trackerIdNumString] = trackerDf[trackerIdNumString].astype(str)

    return trackerDf

def get_resources_to_add(self):
#def get_resources_to_add():
    print("hiiii; getting resource to add file")
    
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getResourcesToAdd = os.path.join(getDir,"resources-to-add.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getResourcesToAdd):
        resourcesToAddDf = pd.read_csv(getResourcesToAdd)
        resourcesToAddDf.fillna("", inplace = True)
        resourcesToAddDf = resourcesToAddDf[resourcesToAddDf["path"] != ""]
        resourcesToAddDf["date-time"] = pd.to_datetime(resourcesToAddDf["date-time"])

        print(resourcesToAddDf)
        print(resourcesToAddDf.columns)
        print(resourcesToAddDf.shape)

        resourcesToAddDf = resourcesToAddDf[resourcesToAddDf["date-time"] == (resourcesToAddDf.groupby("parent-resource-id")["date-time"].transform("max"))]
        #df[df['date'] < (df.groupby('id')['date'].transform('max') - pd.Timedelta(3, unit='M'))]

        print(resourcesToAddDf)
        print(resourcesToAddDf.columns)
        print(resourcesToAddDf.shape)

    else:
        resourcesToAddDf = None

    return resourcesToAddDf

def get_resources_share_status(self):
    
    #getDir = self.workingDataPkgDir
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getShareStatus = os.path.join(getDir,"share-status.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getShareStatus):
        shareStatusDf = pd.read_csv(getShareStatus)
        shareStatusDf.fillna("", inplace = True)
        shareStatusDf["date-time"] = pd.to_datetime(shareStatusDf["date-time"])
        
        print(shareStatusDf)
        print(shareStatusDf.columns)
        print(shareStatusDf.shape)

        # sort by date-time (ascending), then drop duplicates of, keeping the last/latest instance of each path's occurrence
        # to get the latest share status
        shareStatusDf.sort_values(by=["date-time"],ascending=True,inplace=True)
        shareStatusDf.drop_duplicates(subset=["path"],keep="last",inplace=True)
        print("drop duplicates of resource keeping the last/latest instance of each path's occurrence to get the latest share status:")
        print(shareStatusDf.shape)
        
    else:
        shareStatusDf = []

    return shareStatusDf

def get_resources_annotation_mode_status(self):
#def get_resources_annotation_mode_status():
    
    #getDir = self.workingDataPkgDir
    getDir = os.path.join(self.workingDataPkgDir,"no-user-access")
    #getDir = "P:/3652/Common/HEAL/y3-task-b-data-sharing-consult/repositories/vivli-submission-from-data-pkg/vivli-test-study/dsc-pkg"
    getAnnotationModeStatus = os.path.join(getDir,"annotation-mode-status.csv")
    
    # prob need to change to os.path.exists
    if os.path.isfile(getAnnotationModeStatus):
        annotationModeStatusDf = pd.read_csv(getAnnotationModeStatus)
        annotationModeStatusDf.fillna("", inplace = True)
        
        print(annotationModeStatusDf)
        print(annotationModeStatusDf.columns)
        print(annotationModeStatusDf.shape)

        # sort by date-time (descending) so that latest annotation mode status value is in first row of df
        annotationModeStatusDf.sort_values(by=["date-time"],ascending=False,inplace=True)
        # get the latest annotation mode status from first row of df as a string
        annotationModeStatus = annotationModeStatusDf["annotation-mode-status"].iloc[0]

    else:
        annotationModeStatus = ""

    return annotationModeStatus

def get_id(filePrefix, folderPath, firstIdNum=1, fileExt=".txt", self=None):

    if not folderPath:
        print("must provide folderPath")
        return False
    
    if not filePrefix:
        print("must provide filePrefix")
        return False

    # get the max id num used for existing files and add 1; if no files yet, set id num to firstIdNum

    fileList = [filename for filename in os.listdir(folderPath) if filename.startswith(filePrefix)]

    if fileList: # if the list is not empty
        fileStemList = [Path(filename).stem for filename in fileList]
        idNumList = [int(filename.rsplit('-',1)[1]) for filename in fileStemList]
        idNum = max(idNumList) + 1
    else:
        idNum = firstIdNum

    if self:
        self.annotationIdNumber = idNum
        self.annotationId = self.trackerIdPrefix + str(self.annotationIdNumber)
        self.annotationSaveFileName = self.trackerJsonFilePrefix + self.annotationId + fileExt
        self.annotationSaveFilePath = os.path.join(self.saveFolderPath,self.annotationSaveFileName)
        # self.form.widget.state[self.trackerIdNumberLabel] = self.annotationIdNumber
        # self.form.widget.state[self.trackerIdLabel] = self.annotationId

        self.form.widget.state = {
            self.trackerIdNumberLabel: self.annotationIdNumber,
            self.trackerIdLabel: self.annotationId
        }
           
        self.set_read_only_widget_by_name(name=self.trackerIdLabel)

        messageText = "<br>Based on other " + self.trackerType + "(s/es) already saved in your working DSC Data Package directory, your new " + self.trackerType + " will be saved with the unique ID: " + self.annotationId + "<br>" + self.trackerType.title() + " ID has been added to the " + self.trackerType + " form."
        messageText = messageText + "<br><br>Your new " + self.trackerType + " annotation file will be saved in your working DSC Data Package directory as: " + self.annotationSaveFilePath + "<br><br>"
        self.userMessageBox.append(messageText)

    return idNum
        

def get_exp_names(self=None, workingDataPkgDir=None, perResource=False):

    if self:    
        getDir = self.workingDataPkgDir
    elif workingDataPkgDir:
        getDir = workingDataPkgDir
    else:
        print("I need a working data pkg dir path")
        return
    
    print(getDir)
    getExpTrk = os.path.join(getDir,"heal-csv-experiment-tracker.csv")

    if os.path.isfile(getExpTrk):
        experimentTrackerDf = pd.read_csv(getExpTrk)
        #experimentTrackerDf.replace(np.nan, "")
        experimentTrackerDf.fillna("", inplace = True)

        # get only the experiment names that are associated with the latest annotation entry for each experiment
        # and only if latest entry for that experiment is NOT removed - removed property not yet implemented for 
        # experiment tracker, but this will work currently AND future proof for when removed property is added
        experimentTrackerDf["annotationModTimeStamp"] = pd.to_datetime(experimentTrackerDf["annotationModTimeStamp"])
        # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
        # to get the latest annotation entry
        experimentTrackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
        experimentTrackerDf.drop_duplicates(subset=["experimentIdNumber"],keep="last",inplace=True)

        if "removed" in experimentTrackerDf.columns:
            experimentTrackerDf = experimentTrackerDf[experimentTrackerDf["removed"] == 0]

        print(experimentTrackerDf)
        print(experimentTrackerDf.columns)

        if "experimentName" in experimentTrackerDf.columns:

            #experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
            experimentNameSeries = experimentTrackerDf["experimentName"].astype(str)
            print(experimentNameSeries,type(experimentNameSeries))
            
            experimentNameDefaultSeries = pd.Series(["default-experiment-name"])
            
            # add default value to list so that default value is always part of the enum for results and resource tracker experimentNameBelongsTo fields - this allows 
            # default value to be set as the default on drop down for this field 
            experimentNameSeries = pd.concat([experimentNameDefaultSeries,experimentNameSeries], ignore_index=True)
            print(experimentNameSeries,type(experimentNameSeries))
            
            #experimentNameList = experimentTrackerDf["experimentName"].unique().tolist()
            experimentNameList = experimentNameSeries.unique().tolist()
            print(experimentNameList,type(experimentNameList))
            
            experimentNameList[:] = [x for x in experimentNameList if x] # get rid of emtpy strings as empty strings are not wanted and mess up the sort() function
            print(experimentNameList,type(experimentNameList))

            #sortedlist = sorted(list, lambda x: x.rsplit('-', 1)[-1])
            experimentNameList = sorted(experimentNameList, key = lambda x: x.split('-', 1)[0]) # using lambda function to split so can sort on first part of string before a hyphen if a hyphen exists - can't sort on raw strings that include hyphens

            #experimentName = sorted(experimentNameList, lamda x: x.split('-'))
            print(experimentNameList,type(experimentNameList))

            # if ((len(experimentNameList) == 1) and (experimentNameList[0] == "default-experiment-name")):
            #     experimentNameList = []
            #experimentNameList.remove("default-experiment-name")
            #print(experimentNameList,type(experimentNameList))
            
            if perResource:  

                experimentTrackerDf["experimentName"] = experimentTrackerDf["experimentName"].astype(str)
                experimentTrackerDf["experimentId"] = experimentTrackerDf["experimentId"].astype(str)
                
                experimentNameDf = experimentTrackerDf[["experimentId","experimentName"]]
                print(experimentNameDf,type(experimentNameDf))
                
                experimentNameDf.drop_duplicates(inplace=True) 
                experimentNameDf = experimentNameDf[experimentNameDf["experimentName"].str.len() > 0]  

                
            else: 
                experimentNameDf = []


        else:
            print("no experimentName column in experiment tracker")
            experimentNameList = []
            experimentNameDf = []
    else:
        print("no experiment tracker in working data pkg dir")
        # messageText = "<br>Your working Data Package Directory does not contain a properly formatted Experiment Tracker from which to populate unique experiment names for experiments you've already documented. <br><br> The field in this form <b>Experiment Result \"Belongs\" To</b> pulls from this list of experiment names to provide options of study experiments to which you can link your results. Because we cannot populate this list without your experiment tracker, your only option for this field will be the default experiment name: \"default-experiment-name\"." 
        # errorFormat = '<span style="color:red;">{}</span>'
        # self.userMessageBox.append(errorFormat.format(messageText)) 
        experimentNameList = []
        experimentNameDf = []

    print("experimentNameList: ", experimentNameList)
    return experimentNameList, experimentNameDf

# def get_names(self=None, workingDataPkgDir=None, perResource=False, nameType=None):

#     if not nameType:
#         print("I need a name type")
#         return
    
#     if self:    
#         getDir = self.workingDataPkgDir
#     elif workingDataPkgDir:
#         getDir = workingDataPkgDir
#     else:
#         print("I need a working data pkg dir path")
#         return
    
#     print(getDir)

#     tracker_fname = nameType + "-tracker.csv"
#     tracker_idnumlabel = nameType + "IdNumber"
#     tracker_idlabel = nameType + "Id"
#     tracker_namelabel = nameType + "Name"
#     tracker_namedefault = "default-" + nameType + "-name"

#     #getTrk = os.path.join(getDir,"term-tracker.csv")
#     getTrk = os.path.join(getDir,tracker_fname)

#     if os.path.isfile(getTrk):
#         trackerDf = pd.read_csv(getTrk)
#         trackerDf.fillna("", inplace = True)

#         # get only the experiment names that are associated with the latest annotation entry for each experiment
#         # and only if latest entry for that experiment is NOT removed - removed property not yet implemented for 
#         # experiment tracker, but this will work currently AND future proof for when removed property is added
#         trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])
#         # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
#         # to get the latest annotation entry
#         trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
#         trackerDf.drop_duplicates(subset=[tracker_idnumlabel],keep="last",inplace=True)

#         if "removed" in trackerDf.columns:
#             trackerDf = trackerDf[trackerDf["removed"] == 0]

#         print(trackerDf)
#         print(trackerDf.columns)

#         if tracker_namelabel in trackerDf.columns:

#             nameSeries = trackerDf[tracker_namelabel].astype(str)
#             print(nameSeries,type(nameSeries))
            
#             nameDefaultSeries = pd.Series([tracker_namedefault])
            
#             # add default value to list so that default value is always part of the enum for results and resource tracker experimentNameBelongsTo fields - this allows 
#             # default value to be set as the default on drop down for this field 
#             nameSeries = pd.concat([nameDefaultSeries,nameSeries], ignore_index=True)
#             print(nameSeries,type(nameSeries))
            
#             #experimentNameList = experimentTrackerDf["experimentName"].unique().tolist()
#             nameList = nameSeries.unique().tolist()
#             print(nameList,type(nameList))
            
#             nameList[:] = [x for x in nameList if x] # get rid of emtpy strings as empty strings are not wanted and mess up the sort() function
#             print(nameList,type(nameList))

#             #sortedlist = sorted(list, lambda x: x.rsplit('-', 1)[-1])
#             nameList = sorted(nameList, key = lambda x: x.split('-', 1)[0]) # using lambda function to split so can sort on first part of string before a hyphen if a hyphen exists - can't sort on raw strings that include hyphens

#             #experimentName = sorted(experimentNameList, lamda x: x.split('-'))
#             print(nameList,type(nameList))

#             # if ((len(experimentNameList) == 1) and (experimentNameList[0] == "default-experiment-name")):
#             #     experimentNameList = []
#             #experimentNameList.remove("default-experiment-name")
#             #print(experimentNameList,type(experimentNameList))
            
#             if perResource:  

#                 trackerDf[tracker_namelabel] = trackerDf[tracker_namelabel].astype(str)
#                 trackerDf[tracker_idlabel] = trackerDf[tracker_idlabel].astype(str)
                
#                 nameDf = trackerDf[[tracker_idlabel,tracker_namelabel]]
#                 print(nameDf,type(nameDf))
                
#                 nameDf.drop_duplicates(inplace=True) 
#                 nameDf = nameDf[nameDf[tracker_namelabel].str.len() > 0]  

                
#             else: 
#                 nameDf = []


#         else:
#             print("no name column in tracker")
#             nameList = []
#             nameDf = []
#     else:
#         print("no tracker in working data pkg dir")
#         # messageText = "<br>Your working Data Package Directory does not contain a properly formatted Experiment Tracker from which to populate unique experiment names for experiments you've already documented. <br><br> The field in this form <b>Experiment Result \"Belongs\" To</b> pulls from this list of experiment names to provide options of study experiments to which you can link your results. Because we cannot populate this list without your experiment tracker, your only option for this field will be the default experiment name: \"default-experiment-name\"." 
#         # errorFormat = '<span style="color:red;">{}</span>'
#         # self.userMessageBox.append(errorFormat.format(messageText)) 
#         nameList = []
#         nameDf = []

#     print("nameList: ", nameList)
#     return nameList, nameDf

def dynamic_add_enums_to_schema_property(propertyToUpdate,schema,enumList=[]):
    
    schemaUpdated = deepcopy(schema)
    enumListOrig = schemaUpdated["properties"][propertyToUpdate]["enum"]
    enumListUpdated = enumList

    schemaUpdated["properties"][propertyToUpdate]["enum"] = enumListUpdated

    return schemaUpdated

def add_exp_names_to_schema(self=None,schema=None,experimentNameList=None):

    if self:
        if ((hasattr(self,"schema")) and (hasattr(self,"experimentNameList"))):
            schemaOrig = self.schema
            experimentNameList = self.experimentNameList
        else:
            messageText = "You've provided an object but the object does not have one or both of the required schema and experimentNameList properties."
            return
    else:
        if not schema:
            print("i need a base schema")
            return
        if not experimentNameList:
            print("i need a list of experiment names")
            return
        schemaOrig = schema
        experimentNameList = experimentNameList
    
    schemaUpdated = deepcopy(schemaOrig)
    enumListOrig = schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"]
    print("enumListOrig: ", enumListOrig)
    #enumListUpdated = enumListOrig.extend(experimentNameList)
    enumListUpdated = experimentNameList
    print("enumListUpdated: ", enumListUpdated)

    schemaUpdated["properties"]["experimentNameBelongsTo"]["enum"] = enumListUpdated
    print("schemaOrig: ",schemaOrig)
    print("schemaUpdated: ", schemaUpdated)

    return schemaUpdated

def getWorkingDataPkgDir(self):

    testPath = self.workingDataPkgDirDisplay.toPlainText()
    print("testPath: ",testPath)

    if not os.path.exists(testPath):
        messageText = "<br>You must set a valid working Data Package Directory to proceed. Navigate to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to either: <br><br>1. <b>Create New Data Package</b>: Create a new Data Package Directory and set it as the working Data Package Directory, or <br>2. <b>Continue Existing Data Package</b>: Set an existing Data Package Directory as the working Data Package Directory."
        errorFormat = '<span style="color:red;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        return None
    else:
        workingDataPkgDir = testPath  
        return workingDataPkgDir


def heal_metadata_json_schema(metadataType,schema=None):

    if metadataType == "data-dictionary":
        schema = conversion.convert_frictionless_to_jsonschema(healcsvschema)
    else:
        if schema:
            schema = schema
        else:
            print("must provide a schema if metadataType is not data-dictionary")
            return 
    
    return schema

def heal_metadata_json_schema_properties(metadataType,schema=None):

    if metadataType == "data-dictionary":
        intJson = conversion.convert_frictionless_to_jsonschema(healcsvschema)
        props = intJson["items"]["properties"]
        
    else:
        if schema:
            props = schema["properties"]
        else:
            print("must provide a schema if metadataType is not data-dictionary")
            return
    
    return props

def empty_df_from_json_schema_properties(jsonSchemaProperties):
    all_fields = []

    for key, value in jsonSchemaProperties.items():
        p_fullname_list = []
        try:
            p_block = jsonSchemaProperties[key]["properties"]
            p_list = list(p_block.keys())
            p_fullname_list = [key + "." + p for p in p_list]
            print(p_fullname_list)
        except KeyError:
            pass

        if p_fullname_list:
            all_fields.extend(p_fullname_list)
        else:
            all_fields.append(key)

    df = pd.DataFrame(columns = all_fields)    
    return df

def everything_after(df, cols):
    # convenience function to bring one or more cols in a dataframe to the front, while leaving all others in same order following
    # replicates functionality of dplyr 'everything' function - by: https://stackoverflow.com/users/2901002/jezrael
    # cols is a list of col names (list of strings)
    another = df.columns.difference(cols, sort=False).tolist()
    return df[cols + another]

def new_pkg(trackersToAddToTool,pkg_parent_dir_path,pkg_dir_name='dsc-pkg'):
    
    pkg_path = os.path.join(pkg_parent_dir_path,pkg_dir_name)
            
    # create the new package directory    
    try:
        os.makedirs(pkg_path, exist_ok = False)
        print("Directory '%s' created successfully" %pkg_dir_name)
        #os.mkdir(pkg_resources_path) # make the subdir for resources
    except OSError as error:
        print("Directory '%s' can not be created - check to see if the directory already exists")
        return

    # create a no user access subdir in working data pkg dir for operational files
    operationalFileSubDir = os.path.join(pkg_path,"no-user-access")
    os.mkdir(os.path.join(operationalFileSubDir))
        
    metadataTypeList = [i["trackerName"] for i in trackersToAddToTool]
    metadataSchemaVersionList = [i["schemaVersion"] for i in trackersToAddToTool]
    metadataTrackerFileNameList = [i["trackerFileName"] for i in trackersToAddToTool]
    metadataSchemaList = [i["schema"] for i in trackersToAddToTool]
    
    for metadataType, metadataSchemaVersion, metadataTrackerFileName, metadataSchema in zip(metadataTypeList,metadataSchemaVersionList,metadataTrackerFileNameList,metadataSchemaList):

        versionTxtFileName = "schema-version-" + metadataType + ".txt"
        with open(os.path.join(operationalFileSubDir,versionTxtFileName), "w") as text_file:
            text_file.write(metadataSchemaVersion)

        props = heal_metadata_json_schema_properties(metadataType=metadataType,schema=metadataSchema)
        df = empty_df_from_json_schema_properties(jsonSchemaProperties=props)

        fName = metadataTrackerFileName
        
        df.to_csv(os.path.join(pkg_path, fName), index = False) 

    return pkg_path

# def new_results_trk():
    
#     metadataType = "results-tracker"

#     props = heal_metadata_json_schema_properties(metadataType=metadataType)
#     df = empty_df_from_json_schema_properties(jsonSchemaProperties=props)

#     fName = "heal-csv-" + metadataType + "-(multi-result file to which this result tracker applies).csv"
#     #df.to_csv(os.path.join(pkg_path, fName), index = False) 

#     return df, fName


# def qt_object_properties(qt_object: object) -> dict:
#     """
#     source: https://stackoverflow.com/questions/50556216/pyqt5-get-list-of-all-properties-in-an-object-qpushbutton
#     Create a dictionary of property names and values from a QObject.

#     :param qt_object: The QObject to retrieve properties from.
#     :type qt_object: object
#     :return: Dictionary with format
#         {'name': property_name, 'value': property_value}
#     :rtype: dict
#     """
#     properties: list = []

#     # Returns a list of QByteArray.
#     button_properties: list = qt_object.dynamicPropertyNames()

#     for prop in button_properties:
#         # Decode the QByteArray into a string.
#         name: str = str(prop, 'utf-8')

#         # Get the property value from the button.
#         value: str = qt_object.property(name)

#         properties.append({'name': name, 'value': value})

#     return properties

# def validateJson(jsonData,jsonSchema):
#     # source: https://pynative.com/python-json-validation/
#     try:
#         validate(instance=jsonData, schema=jsonSchema)
#     except jsonschema.exceptions.ValidationError as err:
#         return False
#     return True
    
def get_multi_like_file_descriptions(nameConvention,fileStemList):
    
    allFilesDescribeList = [] 
    messagesOut = []

    nameConventionExplanatoryList = re.findall('{(.+?)}', nameConvention) # list of items enclosed in curly braces
    print(nameConventionExplanatoryList)

    if nameConventionExplanatoryList: # check if user added any naming convention explanatory values in the correct format (between curly braces); if yes, continue, if no, print informative message and return

        nameConventionAllList = re.split('[/{/}]', nameConvention)
        nameConventionAllList = [l for l in nameConventionAllList if l] # list of items delimited by curly braces (either direction)
        print(nameConventionAllList)

        nameOnlyOneExplanatory = False # set default value as false
        # check for delimiters between naming convention explanatory variables - need these to parse filenames to descriptions
        # if length of two lists is same then no delimiters between explanatory values exist, but if list is length one this is handle-able  
        if len(nameConventionAllList) == len(nameConventionExplanatoryList):
            if len(nameConventionAllList) == 1:
                nameOnlyOneExplanatory = True
            else:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                messageText = "Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                #errorFormat = '<span style="color:red;">{}</span>'
                #self.userMessageBox.append(errorFormat.format(messageText))
                messagesOut.append(messageText)
                return allFilesDescribeList, messagesOut

        if not nameOnlyOneExplanatory:
            noDelim = 0
            for idx, l in enumerate(nameConventionAllList):
                beforeVal = None
                afterVal = None
                if l in nameConventionExplanatoryList:
                    if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                        afterVal = nameConventionAllList[idx + 1]
                    if idx != 0: # if not first element, get element before current element  
                        beforeVal = nameConventionAllList[idx - 1]
            
                    if afterVal:
                        if afterVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                            messageText = l," and ",afterVal," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))
                    if beforeVal:
                        if beforeVal in nameConventionExplanatoryList:
                            noDelim += 1
                            print(beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                            messageText = beforeVal," and ",l," naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))

            if noDelim > 0:
                print("Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon.")
                messageText = "Naming convention explanatory values are not separated by a delimiter in your file name convention. Please add delimiters between file naming convention explanatory values in your filenames. Snake case as a delimiter is not currently supported but will be soon."
                messagesOut.append(messageText)
                #errorFormat = '<span style="color:red;">{}</span>'
                #self.userMessageBox.append(errorFormat.format(messageText))
                return allFilesDescribeList, messagesOut


        allFilesDescribeList = [] 
        
        for i in fileStemList:
            print(i)
        
            oneFileDescribeList = []  

            if nameOnlyOneExplanatory:
                oneFileDescribe = nameConventionAllList[0] + ": " + i
            else: 
                beforeValSave = None
                for idx, l in enumerate(nameConventionAllList):
                    print("idx: ",idx,", l: ",l)
                    beforeVal = None
                    beforeValSplit = None
                    afterVal = None
                    afterValSplit = None
                    if l in nameConventionExplanatoryList:
                        if idx != len(nameConventionAllList) - 1: # if not last element, get element after current element  
                            afterVal = nameConventionAllList[idx + 1]
                            print("afterVal: ",afterVal)
                        if idx != 0: # if not first element, get element first current element  
                            if beforeValSave:
                                beforeVal = beforeValSave + nameConventionAllList[idx - 1]
                                print("YES beforeValSave")
                                print("beforeValSave: ", beforeValSave)
                            else:
                                beforeVal = nameConventionAllList[idx - 1]
                                print("NO beforeValSave")
                            print("beforeVal: ",beforeVal)
                            
            
                        if afterVal:
                            if afterVal in i:
                                afterValSplit = i.split(afterVal)
                                print("afterValSplit: ", afterValSplit)
                        
                            else:
                                #print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention.")
                                messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",afterVal," as specified by the applied naming convention."
                                messagesOut.append(messageText)
                                #errorFormat = '<span style="color:red;">{}</span>'
                                #self.userMessageBox.append(errorFormat.format(messageText))
                                continue

                        if beforeVal:
                            if beforeVal in i:
                                beforeValSplit = i.split(beforeVal)
                                print("beforeValSplit: ", beforeValSplit)
                        
                            else:
                                #print("the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention.")
                                messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain the string ",beforeVal," as specified by the applied naming convention."
                                messagesOut.append(messageText)
                                #errorFormat = '<span style="color:red;">{}</span>'
                                #self.userMessageBox.append(errorFormat.format(messageText))
                                continue

                        if ((not afterValSplit) and (not beforeValSplit)):
                            #print("the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file.")
                            messageText = "the file named ", i, " does not conform to the specified naming convention. It does not contain string(s) specified by the applied naming convention. Exiting check of this file."
                            messagesOut.append(messageText)
                            #errorFormat = '<span style="color:red;">{}</span>'
                            #self.userMessageBox.append(errorFormat.format(messageText))
                            break

                        if ((afterValSplit) and (not beforeValSplit)):
                            myVal = afterValSplit[0]
                            print("afterValSplit ONLY; myVal: ", myVal)

                        if ((not afterValSplit) and (beforeValSplit)):
                            myVal = beforeValSplit[1]
                            print("beforeValSplit ONLY; myVal: ", myVal)
                    
                        if ((afterValSplit) and (beforeValSplit)):
                            #myVal = afterValSplit[0]
                            #print("afterValSplit and beforeValSplit; myVal: ", myVal)
                            #myVal = myVal.split(beforeVal)[1]

                            myVal = beforeValSplit[1]
                            print("afterValSplit and beforeValSplit; myVal 1: ", myVal)
                            myVal = myVal.split(afterVal)[0]
                            print("afterValSplit and beforeValSplit; myVal 2: ", myVal)

                            beforeValSave = beforeVal + myVal
                            print("save beforeValSave: ",beforeValSave)
                    
                        myDescribe = l + ": " + myVal
                        oneFileDescribeList.append(myDescribe)   
            
                oneFileDescribe = ', '.join(oneFileDescribeList)
                print(oneFileDescribe)    
            
            allFilesDescribeList.append(oneFileDescribe) 
            print(allFilesDescribeList) 
    
    return allFilesDescribeList, messagesOut  

import re

def camel_to_title_case(camel_case_string):
    """
    Converts a camel case string to title case.
    e.g., "myCamelCaseString" becomes "My Camel Case String"
    """
    # Insert a space before each uppercase letter that is not the first character
    # and is not preceded by another uppercase letter (to handle acronyms correctly)
    spaced_string = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', camel_case_string)
    
    # Apply title case to the resulting string
    title_cased_string = spaced_string.title()
    
    return title_cased_string   

def add_to_val(val: int,add_val:int):
    return val + add_val

