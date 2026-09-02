import os
import copy
import datetime
import json
import pandas as pd
import pathlib

from qtpy import QtWidgets, QtGui

import cair_data_package_tool.schema_utils as schema_utils
import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils
import cair_data_package_tool.version_check as version_check


metadataDirLockFileName = "in-use.txt"
operationalFileSubdirName = "no-user-access"
archiveFileSubdirName = "archive"

def getLatestAnnotationJsonTxtFiles(trkDict,metadataDirPath):
    jsonTxtPrefix = trkDict["trackerJsonFilePrefix"] + trkDict["trackerIdPrefix"]
    # get id nums based on annotation files that already exist
    latestAnnotationJsonTxtFileNameList = [filename for filename in os.listdir(metadataDirPath) if filename.startswith(jsonTxtPrefix)]
    if latestAnnotationJsonTxtFileNameList: # if the list is not empty
        latestAnnotationJsonTxtFilePathList = [os.path.join(metadataDirPath,filename) for filename in latestAnnotationJsonTxtFileNameList]
        latestAnnotationJsonTxtFileStemList = [pathlib.Path(filename).stem for filename in latestAnnotationJsonTxtFileNameList]
        latestAnnotationJsonTxtFileIdNumList = [int(filename.split(jsonTxtPrefix)[1]) for filename in latestAnnotationJsonTxtFileStemList]
    else: 
        latestAnnotationJsonTxtFilePathList = []
        latestAnnotationJsonTxtFileStemList = []
        latestAnnotationJsonTxtFileIdNumList = []
    return latestAnnotationJsonTxtFilePathList, latestAnnotationJsonTxtFileNameList, latestAnnotationJsonTxtFileStemList, latestAnnotationJsonTxtFileIdNumList

def getNowDateTime():
    """ get now timestamp, datetime, and datetime string in specific string format used in tracker metadata
    
    Args:
        None
    
    Returns: 
        ::Dict: 
            now_timestamp: float
            now_datetime: datetime
            now_datetime_str: str

    """
    # get now timestamp and datetime to add create and mod time first time creating annotation and to update mod time every subsequent edit
    now_timestamp = datetime.datetime.now().timestamp()
    now_datetime = datetime.datetime.fromtimestamp(now_timestamp)
    now_datetime_str = now_datetime.strftime("%Y-%m-%d, %H:%M:%S")
    
    return {"now_timestamp":now_timestamp,"now_datetime":now_datetime,"now_datetime_str":now_datetime_str}

def writeMetadataDirLockFile(metadataDirPath, metadataDirLockFileName=metadataDirLockFileName, lockFileMode="manual"):
    dtDict = getNowDateTime()

    # create an in-use file to "check out" the dsc-pkg and prevent modification of this local copy by more than one person at a time  
    with open(os.path.join(metadataDirPath,metadataDirLockFileName),'w') as lockFile:
        lockFile.write(lockFileMode + "-update-lock " + dtDict["now_datetime_str"])

def destroyMetadataDirLockFile(metadataDirPath, metadataDirLockFileName=metadataDirLockFileName):
    lockFilePath = os.path.join(metadataDirPath,metadataDirLockFileName)
    if os.path.exists(lockFilePath):
        os.remove(lockFilePath)
        print("in-use file was removed from data package directory to indidate that it is no longer in use")
    else:
        print("something went wrong - no in-use file was found")

def checkMetadataDirLockFile(metadataDirPath, metadataDirLockFileName=metadataDirLockFileName, self=None):
    # set default values
    lockFileExists = False
    lockFileContentParseable = False
    lockFileMode = None
    lockFileDateTime = None

    # check if this data package dir is in use by another user, 
    # if it is, don't allow the current user to select this data package to work on
    # if it is not, allow the current user to select this data package to work on AND write a file that "checks out" this data package dir so that if another user tries to use it at the same time it will not allow it
    lockFilePath = os.path.join(metadataDirPath,metadataDirLockFileName)
    if os.path.exists(lockFilePath):
        lockFileExists = True
        with open(lockFilePath, 'r') as file:
            # Read the content of the file
            lockFileContent = file.read()
            if lockFileContent != "":
                try:
                    lockFileContentParse = lockFileContent.split(sep="-update-lock ")
                    lockFileMode = lockFileContentParse[0]
                    lockFileDateTime = lockFileContentParse[1]
                    lockFileContentParseable = True
                except Exception as e:
                    print("lock file content not as expected; can't parse")
            else:
                print("no lock file content; can't parse")
        messageText = "<br>The directory you selected as your existing Data Package Directory appears to be checked out/in use by another user or process.<br>"
        if lockFileContentParseable:
            messageText = messageText + "<br>Lock file mode: " + lockFileMode + "<br>Lock file date time: " + lockFileDateTime + "<br>" 
            if lockFileMode == "manual":
                messageText = messageText + "<br>The directory is checked out/in use by a metadata contributor working on a manual metadata update - Check in with metadata contributors for more information.<br>"
            if lockFileMode == "programmatic":
                messageText = messageText + "<br>The directory is checked out/in use by a process working on a programmatic metadata update - Check in with your metadata administrator for more information.<br>"
        else:
            messageText = "<br>" + "Lock file content is not parseable so there is no additional information - Check in with metadata contributors and/or your metadata administrator for more information." 
        
        if self:
            self.userMessageBox.append(messageText)
        else:
            print(messageText)

    return {"lockFileExists":lockFileExists,"lockFileContentParseable":lockFileContentParseable,"lockFileMode":lockFileMode,"lockFileDateTime":lockFileDateTime}    

def getTrackerVars(initialTrackerDict):
    trackerType = initialTrackerDict["trackerType"]
    trackerFileNamePrefix = initialTrackerDict["trackerFileNamePrefix"]
    schema = initialTrackerDict["schema"]
    if initialTrackerDict.get("trackerDescriptionLabel"):
        trackerDescriptionLabel = initialTrackerDict["trackerDescriptionLabel"]
    else:
        trackerDescriptionLabel = None
    
    trackerOneOrMulti = "one"
    if initialTrackerDict.get("oneOrMulti"):
        trackerOneOrMulti = initialTrackerDict["oneOrMulti"]
    
    # created vars
    
    ##### schema related
    schemaVersion = schema["version"]
    
    ##### referring to tracker 
    trackerTitle = trackerType.title() + " Tracker"
    trackerName = trackerType + "-tracker"
    trackerNameCamelCase = trackerType + "Tracker"
    
    ##### csv tracker file name
    if trackerOneOrMulti == "one":
        trackerFileBaseName = trackerType + "-tracker.csv"
    else: 
        trackerFileBaseName = trackerType + "-tracker-"
    
    if trackerFileNamePrefix:
        trackerFileName = trackerFileNamePrefix + trackerFileBaseName
    else:
        trackerFileName = trackerFileBaseName
    
    ##### annotation json txt file name
    trackerJsonFilePrefix = trackerType + "-trk-" 
    
    ##### universal tracker schema properties
    trackerIdLabel = trackerType + "Id"
    trackerIdNumberLabel = trackerType + "IdNumber"
    trackerNameLabel = trackerType + "Name"
    if trackerDescriptionLabel:
        pass
    else:
        trackerDescriptionLabel = trackerType + "Description"
    
    ##### values for universal tracker schema properties    
    trackerFirstId = trackerType + "-1"
    trackerDefaultName = "default-" + trackerType + "-name"
    trackerIdPrefix = trackerType + "-"

    ############################## 
    # add new vars to trackerDict
    ##############################   
    initialTrackerDict["schemaVersion"] = schemaVersion
    
    initialTrackerDict["trackerTitle"] = trackerTitle
    initialTrackerDict["trackerName"] = trackerName
    initialTrackerDict["trackerNameCamelCase"] = trackerNameCamelCase
    
    initialTrackerDict["trackerFileBaseName"] = trackerFileBaseName
    initialTrackerDict["trackerFileName"] = trackerFileName
    
    initialTrackerDict["trackerJsonFilePrefix"] = trackerJsonFilePrefix
    
    initialTrackerDict["trackerIdLabel"] = trackerIdLabel
    initialTrackerDict["trackerIdNumberLabel"] = trackerIdNumberLabel
    initialTrackerDict["trackerNameLabel"] = trackerNameLabel
    initialTrackerDict["trackerDescriptionLabel"] = trackerDescriptionLabel

    initialTrackerDict["trackerFirstId"] = trackerFirstId
    initialTrackerDict["trackerDefaultName"] = trackerDefaultName
    initialTrackerDict["trackerIdPrefix"] = trackerIdPrefix

    return initialTrackerDict

def get_unique_prop_vals(trackerProperty, trackerDict, saveFolderPath, propertyDefaultValue = [], includeLatestOnly = True, includeRemoved = False):
    
    """ get list of unique values for a specific property from a specific tracker, across all items in the tracker; get df of these names with associated item id
    
    Args:
        property -- string; required; tracker schema property for which you want to get unique values
        trackerDict -- dictionary; required; tracker dictionary from the tracker you want to get unique values of a property from; output from getTrackerVars fx, which itself takes as input trackerDict from py file that defines schema and trackerDict for the tracker 
        saveFolderPath -- string; required; full file path to folder in which annotation files and tracker are saved

        propertyDefaultValue -- list; optional; default is empty list; list of a string or string(s) that should always be added to the unique values list for this property 
        includeLatestOnly -- bool; optional; default is True; if True get unique property values only for latest tracker entry per item
        includeRemoved -- bool; optional; default is False; if False get unique property values only for tracker entries that are not removed

    Returns: 

    """

    trackerFileName = trackerDict["trackerFileName"]
    trackerFilePath = os.path.join(saveFolderPath,trackerFileName)

    trackerIdLabel = trackerDict["trackerIdLabel"]
    trackerIdNumberLabel = trackerDict["trackerIdNumberLabel"]
  
    if os.path.isfile(trackerFilePath):
        trackerDf = pd.read_csv(trackerFilePath)
        trackerDf.fillna("", inplace = True)

        # get only the values that are associated with the latest annotation entry for each item
        # and only if latest entry for that item is NOT removed 
        # sort by date-time (ascending), then drop duplicates of id, keeping the last/latest instance of each id's occurrence
        # to get the latest annotation entry
        trackerDf["annotationModTimeStamp"] = pd.to_datetime(trackerDf["annotationModTimeStamp"])
        trackerDf.sort_values(by=["annotationModTimeStamp"],ascending=True,inplace=True)
        if includeLatestOnly:
            trackerDf.drop_duplicates(subset=[trackerIdNumberLabel],keep="last",inplace=True)

        if not includeRemoved:
            if "removed" in trackerDf.columns:
                trackerDf = trackerDf[trackerDf["removed"] == 0]

        if trackerProperty in trackerDf.columns:

            #### valueList
            valueSeries = trackerDf[trackerProperty].astype(str)
            if propertyDefaultValue:
                valueDefaultSeries = pd.Series(propertyDefaultValue)
            
                # add default value to list so that default value is always part of the enum for experimentNameBelongsTo fields - this allows 
                # default value to be set as the default on drop down for this field 

                valueSeries = pd.concat([valueDefaultSeries,valueSeries], ignore_index=True)
            valueList = valueSeries.unique().tolist()
            valueList[:] = [x for x in valueList if x] # get rid of emtpy strings as empty strings are not wanted and mess up the sort() function
            valueList = sorted(valueList, key = lambda x: x.split('-', 1)[0]) # using lambda function to split so can sort on first part of string before a hyphen if a hyphen exists - can't sort on raw strings that include hyphens
    
            #### nameDF
            trackerDf[trackerProperty] = trackerDf[trackerProperty].astype(str)
            trackerDf[trackerIdLabel] = trackerDf[trackerIdLabel].astype(str)
            
            valueDf = trackerDf[[trackerIdLabel,trackerProperty]]
            valueDf.drop_duplicates(inplace=True) 
            valueDf = valueDf[valueDf[trackerProperty].str.len() > 0]  
                
        else:
            print("property not found in tracker: ", trackerProperty)
            valueList = []
            valueDf = []
    else:
        print("no tracker in working data pkg dir")
        valueList = []
        valueDf = []

    return valueList, valueDf

def get_names(trackerDict, saveFolderPath):
    
    """ get list of existing/latest entry item names from tracker; get df of these names with associated item id
    
    Args:
        trackerDict -- dictionary; required; tracker dictionary for the tracker you want to get unique names from; output from getTrackerVars fx, which itself takes as input trackerDict from py file that defines schema and trackerDict for the tracker this annotation belongs to (i.e. if this is a term annotation, then the term tracker which has schema and trackerDict defined in schema_term_tracker.py)
        saveFolderPath -- string; required; full file path to folder in which annotation files and tracker are saved
        
    Returns: 

    """

    trackerNameLabel = trackerDict["trackerNameLabel"]
    trackerDefaultName = trackerDict["trackerDefaultName"]

    nameList,nameDf = get_unique_prop_vals(trackerProperty=trackerNameLabel,trackerDict=trackerDict,saveFolderPath=saveFolderPath,propertyDefaultValue=[trackerDefaultName],includeLatestOnly=True,includeRemoved=False)

    return nameList, nameDf

def check_name_unique(currentId=None, currentName=None, trackerDict=None, saveFolderPath=None, checkForName=False, saveStatus=True, self=None):
    
    """
    Args:
        currentId::string
            required if self not provided; id of the item the name of which you want to check is unique
        currentName::string
            required if self not provided; name of the item the name of which you want to check is unique
        trackerDict::dictionary
            required if self not provided; output from getTrackerVars fx, which itself takes as input trackerDict from py file that defines schema and trackerDict for the tracker this annotation belongs to (i.e. if this is a term annotation, then the term tracker which has schema and trackerDict defined in schema_term_tracker.py)
        saveFolderPath::string
            required if self not provided; full file path to folder in which annotation files and tracker are saved
    
        checkForName::boolean
            default is False; if False, allows save with default name or unique name; if True, allows save only with unique name
        saveStatus::boolean
            default is True; if True this is a final check on name being unique prior to annotation save
    
        self::class
            instance of layout_general_scrollannotate_widget

    Returns: 
        ::tuple 
            nameStatus::string
                enum: default,not unique,unique
                    default: name is the default name for this trackerType
                    not unique: name is not the default name for this trackerType AND the name is already in use by another item ID in this tracker
                    unique: name is not the default name for this trackerType AND the name is NOT already in use by another item ID in this tracker
            allowSave::boolean
                True: should allow save given the result of the name check
                False: should NOT allow save given the result of the name check

    """

    if self:
        currentId = self.formWidgetList[self.formWidgetNameList.index(self.trackerIdLabel)].text()
        currentName = self.formWidgetList[self.formWidgetNameList.index(self.trackerNameLabel)].text()
        trackerDict = self.trackerDict
        saveFolderPath = self.saveFolderPath
    else:
        currentId = currentId
        currentName = currentName
        trackerDict = trackerDict
        saveFolderPath = saveFolderPath

    trackerDefaultName = trackerDict["trackerDefaultName"]
    trackerNameLabel = trackerDict["trackerNameLabel"]
    trackerIdLabel = trackerDict["trackerIdLabel"]
    trackerType = trackerDict["trackerType"]
        
    nameList, nameDf = get_names(trackerDict=trackerDict, saveFolderPath=saveFolderPath) # gets nameList

    if currentName == trackerDefaultName:
        nameStatus = "default"
    else:
        if currentName in nameList:
            # if this name has been used before, check to see if it's been used for another entry in the tracker that is for this id
            # this may happen if for example user is editing an existing tracker item
            # if this is the case, do not throw an error

            currentNameDf = nameDf[nameDf[trackerNameLabel] == currentName]
            currentAssociatedId = currentNameDf[trackerIdLabel].tolist()[0]

            if currentId != currentAssociatedId:
                nameStatus = "not unique"
            else: 
                nameStatus = "unique"
        else:
            nameStatus = "unique"     
    
    # if name is default name, warn about it but allow save
    if nameStatus == "default":
        if not saveStatus:
            messageText = "<br>You've re-set the " + trackerType + " name to the default value of \"" + trackerDefaultName + "\". This is the equivalent of NOT naming your " + trackerType + ". You must name your " + trackerType + " - Please enter a unique " + trackerType + " name that is NOT equal to \"" + trackerDefaultName + "\". " + trackerType.title() + " names already in use include: <br><br>" + "<br>".join(nameList)
            errorFormat = '<span style="color:red;">{}</span>'
        else:
            if checkForName:
                messageText = "<br>Your " + trackerType + " cannot be saved because you've re-set the " + trackerType + " name to the default value of \"" + trackerDefaultName + "\". This is the equivalent of NOT naming your " + trackerType + ". You must name your " + trackerType + " - Please enter a unique " + trackerType + " name that is NOT equal to \"" + trackerDefaultName + "\". " + trackerType.title() + " names already in use include: <br><br>" + "<br>".join(nameList)
                errorFormat = '<span style="color:red;">{}</span>'
            else:
                messageText = "<br>Your " + trackerType + " will be saved with the default " + trackerType + " name of \"" + trackerDefaultName + "\". This is the equivalent of NOT assigning a name to your " + trackerType + ". You must name your " + trackerType + " - You can do so by editing your " + trackerType + ": Edit your " + trackerType + " by navigating to the \"" + trackerType.title() + " Tracker\" tab >> \"Add " + trackerType.title() + "\" sub-tab, clicking on the \"Edit existing " + trackerType + "\" push-button, opening the form for this " + trackerType + ", and editing the " + trackerType.title() + " Name form field."
                errorFormat = '<span style="color:red;">{}</span>'
    
    # if name is NOT default name and is NOT unique, warn and don't allow save
    if nameStatus == "not unique":
        if not saveStatus:
            messageText = "<br>You've used this " + trackerType + " name before, and " + trackerType + " name must be unique - Please enter a unique " + trackerType + " name. " + trackerType.title() + " names already in use include: <br><br>" + "<br>".join(nameList)
            errorFormat = '<span style="color:red;">{}</span>'
        else:
            messageText = "<br>Your " + trackerType + " cannot be saved because the " + trackerType + " name you entered in the " + trackerType.title() + " Name form field is not unique. If you want to assign a name to your " + trackerType + " you must choose a unique name and enter it into the " + trackerType.title() + " Name form field, then try saving again. " + trackerType.title() + " names already in use include: <br><br>" + "<br>".join(nameList)
            errorFormat = '<span style="color:red;">{}</span>'   

    if nameStatus == "unique":
        messageText = "<br>Your " + trackerType + " name is unique! <br><br>" 
        errorFormat = '<span style="color:green;">{}</span>' 

    if self:
        self.userMessageBox.append(errorFormat.format(messageText)) 
    else: 
        print(messageText)

    if checkForName:
        if nameStatus == "unique":
            allowSave = True
        else:
            allowSave = False
    else:
        if nameStatus in ["unique","default"]:
            allowSave = True
        else:
            allowSave = False

    return nameStatus, allowSave
           
def save_annotation(data=None,trackerDict=None,saveFolderPath=None,mode=None,annotationFileNameExtension=".txt",checkForDescription=True,checkForName=False,schema=None,self=None):
    
    """
    Arguments:
    data -- dictionary; required if self not provided; annotation data json record; should include all schema properties and data should have all include values that should be in the updated record, including existing,unchanged values for properties where value is not being updated and updated values for properties where value is being updated (the only thing that will be updated in the new annotation file/tracker record that does not need to be updated before inputing to save/add fx is the mod datetime/timestamp which will be updated as part of save/add fx)
    trackerDict -- dictionary; required if self not provided; output from getTrackerVars fx, which itself takes as input trackerDict from py file that defines schema and trackerDict for the tracker this annotation belongs to (i.e. if this is a term annotation, then the term tracker which has schema and trackerDict defined in schema_term_tracker.py)
    saveFolderPath -- string; required if self not provided; full file path to folder in which annotation files and tracker are saved
    mode -- string; required if self not provided; either "edit" or "add" to respectively 1) archive existing annotation file, update existing annotation file to input data, add updated data to tracker as new record, 2) add new annotation file with input data, add new data to tracker as record
    schema -- object; schema against which the data should be validated; if self is provided will be taken from self.schema; if self not provided and schema not provided will be taken from trackerDict.schema; reason for this is that in some limited cases schema may be dynamically updated from the canonical version stored in trackerDict - e.g. in case of experimentBelongsTo property in data package result and resource trackers which has dynamic enums according to unique values of experimentName property provided across all experiments in experiment tracker   

    self -- instance of layout_general_scrollannotate_widget

    """

    if self:
        ###############
        annotation = copy.deepcopy(self.form.widget.state)
        trackerDict = self.trackerDict
        saveFolderPath = self.saveFolderPath
        mode = self.mode
        schema = self.schema
        ###############
        # currentName = self.formWidgetList[self.formWidgetNameList.index(self.trackerNameLabel)].text()
        # currentId = self.formWidgetList[self.formWidgetNameList.index(self.trackerIdLabel)].text()
        ###############
    else:
        ###############
        annotation = data
        trackerDict = trackerDict
        saveFolderPath = saveFolderPath
        mode = mode
        schema = schema
        ###############
        # currentName = annotation[trackerNameLabel]
        # currentId = annotation[trackerIdLabel]
        ###############

    ############### 
    if not schema:   
        schema = trackerDict["schema"]
    trackerFilePath = os.path.join(saveFolderPath,trackerDict["trackerFileName"])
    trackerTitle = trackerDict["trackerTitle"]
    trackerType = trackerDict["trackerType"]
    trackerDescriptionLabel = trackerDict["trackerDescriptionLabel"]
    trackerIdLabel = trackerDict["trackerIdLabel"]
    trackerIdNumberLabel = trackerDict["trackerIdNumberLabel"]
    trackerNameLabel = trackerDict["trackerNameLabel"]
    ###############
    if trackerNameLabel in annotation:
        currentName = annotation[trackerNameLabel]
    currentId = annotation[trackerIdLabel]
    ###############
    annotationSaveFileName = trackerDict["trackerJsonFilePrefix"] + currentId + annotationFileNameExtension
    annotationSaveFilePath = os.path.join(saveFolderPath,annotationSaveFileName)
    ###############

    ######################################################################################################
    # basic checks for tracker file exists and closed
    ###################################################################################################### 

    # check that tracker exists in working data pkg dir, if not, return
    if not os.path.exists(trackerFilePath):
        messageText = "<br>There is no " + trackerTitle + " file in your working Data Package Directory; Your working Data Package Directory must contain a " + trackerTitle + " file to proceed with saving. If you need to change your working Data Package Directory or create a new one, head to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to set a new working Data Package Directory or create a new one. Then return here and try saving again.<br><br>"
        if self: 
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        else:
            print(messageText)
        return False, "tracker file does not exist"
    
    # check that tracker is closed (user doesn't have it open in excel for example) - if open, prevents the automated add to tracker part of the workflow
    try: 
        with open(trackerFilePath,'r+') as f:
            pass
    except PermissionError:
        messageText = "<br>The " + trackerTitle + " file in your working Data Package Directory is open in another application, and must be closed to proceed with saving; You can leave this form window open while you check to see if the " + trackerTitle + " file is open in Excel or similar application. Make sure the file is closed, then return here and try saving again. <br><br>"
        if self:
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        else:
            print(messageText)
        return False, "tracker file is not closed"
    
    ######################################################################################################
    # add/update created and modified date in annotation
    ###################################################################################################### 
    # get now timestamp and datetime to add create and mod time first time creating annotation and to update mod time every subsequent edit
    dtDict = getNowDateTime()

    if not annotation["annotationCreateDateTime"]:
        annotation["annotationCreateDateTime"] = dtDict["now_datetime_str"]
    
    annotation["annotationModDateTime"] = dtDict["now_datetime_str"]
    annotation["annotationModTimeStamp"] = dtDict["now_timestamp"]

    ######################################################################################################
    # clean up annotation content
    ###################################################################################################### 

    # for any array of string items, remove empty strings from array
    for key in schema["properties"]:
        if schema["properties"][key]["type"] == "array":
            if schema["properties"][key]["items"]["type"] == "string":
                annotation[key] = dsc_pkg_utils.deleteEmptyStringInArrayOfStrings(myStringArray=annotation[key])

    # for any array of string items with at least one item in the array, for each item in the array, 
    # replace "smart double quotes" with regular straight double quotes 
    for key in schema["properties"]:
        if schema["properties"][key]["type"] == "array":
            if schema["properties"][key]["items"]["type"] == "string":
                if annotation[key]:
                    annotation[key] = [x.replace(u"\u201c",'"') for x in annotation[key]]
                    annotation[key] = [x.replace(u"\u201d",'"') for x in annotation[key]]

    # for any string item where string is not empty, replace "smart double quotes" with regular straight double quotes 
    for key in schema["properties"]:
        if schema["properties"][key]["type"] == "string":
            if annotation[key]:
                    annotation[key] = annotation[key].replace(u"\u201c",'"')
                    annotation[key] = annotation[key].replace(u"\u201d",'"')
                    annotation[key] = annotation[key].strip()

    ######################################################################################################
    # annotation valid content checks - other than schema validation
    ###################################################################################################### 

    # check that at least a minimal description has been added to the form 
    # if not exit with informative error
    if checkForDescription:
        if not (annotation[trackerDescriptionLabel]):
            messageText = "<br>You must add at least a minimal description of your " + trackerType + " before saving your annotation file. Please add at least a minimal description of your " + trackerType + " in the " + dsc_pkg_utils.camel_to_title_case(trackerDescriptionLabel) + " field in the form. Then try saving again." 
            if self:
                errorFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(errorFormat.format(messageText))
            else:
                print(messageText)
            errormessage = "a value is required but not provided for the annotation item description property: " + annotation[trackerDescriptionLabel]
            return False, errormessage

    # check that name is unique if provided, check that name is provided
    if trackerNameLabel in annotation:
        nameStatus, nameStatusAllowSave = check_name_unique(currentId=currentId,currentName=currentName,trackerDict=trackerDict,saveFolderPath=saveFolderPath,checkForName=checkForName,saveStatus=True,self=self) # this checks if name is unique, if not sets self.uniqueNameOnSave to False, also outputs informative message if name is not unique or if it is left/set at the default value 
    else: 
        nameStatusAllowSave = True
        print("no name check on save enabled for this tracker")

    if not nameStatusAllowSave: # exit save action if result of name check says not to allow save based on name check
        print("name check failed")
        return False, "a value is required but not provided for the annotation item name property"
    else:
        pass
    
    ######################################################################################################
    # annotation valid content checks - schema validation
    ###################################################################################################### 

    # validate against schema
    out = schema_utils.validate_against_jsonschema(json_object=annotation,schema=schema)
    if not dsc_pkg_utils.process_json_schema_validation_result(validate_against_jsonschema_result=out):
        print("schema validation failed")
        return False, "annotation failed schema validation"
    else:
        pass 

    ######################################################################################################
    # start items for edit mode only
    ###################################################################################################### 
    if mode == "edit":
        
        # check that annotation json txt file exists in working data pkg dir, if not, return
        if not os.path.exists(annotationSaveFilePath):
            messageText = "<br>There is no existing annotation file for this " + trackerType + " in your working Data Package Directory at " + annotationSaveFilePath + ", and there must be an existing annotation file for this term in order to edit it. Did you mean to add this term as a new term?"
            if self: 
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            else:
                print(messageText)
            return False, "annotation file should exist for editing, but does not exist"
        
        # check that annotation json txt file is closed (user doesn't have it open in notebook editor for example) - if open, could prevent archiving part of the workflow
        try: 
            with open(annotationSaveFilePath,'r+') as f:
                pass
        except PermissionError:
                messageText = "<br>The current annotation file for this " + trackerType + " (in your working Data Package Directory, at " + annotationSaveFilePath + ")  is open in another application, and must be closed to proceed with saving; You can leave this form window open while you check to see if the annotation file is open in Notebook editor or similar application. Make sure the file is closed, then return here and try saving again. <br><br>"
                if self:
                    saveFormat = '<span style="color:red;">{}</span>'
                    self.userMessageBox.append(saveFormat.format(messageText))
                else:
                    print(messageText)
                return False, "annotation file should be closed for editing, but is not closed"
        
        # get file path at which to archive the existing annotation json txt file
        annotationArchiveFolderName = "archive"
        annotationArchiveFolderPath = os.path.join(saveFolderPath,annotationArchiveFolderName)

        if not os.path.exists(annotationArchiveFolderPath):
            os.mkdir(annotationArchiveFolderPath)

        annotationArchiveFilePrefix = trackerDict["trackerJsonFilePrefix"] + currentId + "-"
        annotationArchiveFileNumber = dsc_pkg_utils.get_id(filePrefix=annotationArchiveFilePrefix,folderPath=annotationArchiveFolderPath)
        
        annotationArchiveFileName = annotationArchiveFilePrefix + str(annotationArchiveFileNumber) + annotationFileNameExtension
        annotationArchiveFilePath = os.path.join(annotationArchiveFolderPath,annotationArchiveFileName) 
        
        # move the existing annotation json txt file to archive 
        os.rename(annotationSaveFilePath,annotationArchiveFilePath)
        messageText = "<br>In preparation for saving your edited " + trackerType + " annotation file, your original " + trackerType + " annotation file has been archived at:<br>" + annotationArchiveFilePath + "<br><br>"
        if self:
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))
        else:
            print(messageText)
    
    ######################################################################################################
    # start items for NOT edit mode only - check that there's not already an item with this item's id
    ######################################################################################################
    
    if mode != "edit":
        
        # check that annotation json txt file does NOT exist in working data pkg dir, if it does, return
        if os.path.exists(annotationSaveFilePath):
            messageText = "<br>There is an existing annotation file for this " + trackerType + " in your working Data Package Directory at " + annotationSaveFilePath + ", and there must NOT be an existing annotation file for this term in order to add it as a new "  + trackerType + ". Did you mean to edit this term?"
            if self: 
                saveFormat = '<span style="color:red;">{}</span>'
                self.userMessageBox.append(saveFormat.format(messageText))
            else:
                print(messageText)
            return False, "annotation file should not already exist if adding a new item, but it does exist"
        
    ######################################################################################################
    # save new/updated annotation to annotation json txt file
    ######################################################################################################

    # save form annotation data to annotation json txt file
    f=open(annotationSaveFilePath,'w')
    print(json.dumps(annotation, indent=4), file=f)
    f.close()
    
    messageText = "<br>Your " + trackerType + " annotation was successfully written at: " + annotationSaveFilePath + "<br><br> Starting to add your " + trackerType + " to the " + trackerType.title() + " Tracker now! See below for updates: <br>"    

    if self: 
        self.set_disabled_widget_by_name(allNames=True)
        self.buttonSave.setEnabled(False)
        
        saveFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText))
        self.userMessageBox.moveCursor(QtGui.QTextCursor.End)
        QtWidgets.QApplication.processEvents() # print accumulated user status messages 
    else:
        print(messageText)

    add_annotation_result = add_annotation(annotationSaveFilePath=annotationSaveFilePath,trackerFilePath=trackerFilePath,trackerIdNumberLabel=trackerIdNumberLabel,trackerType=trackerType,self=self) # add annotation data to csv tracker as new row
    return add_annotation_result, "annotation saved successfully"

def add_annotation(annotationSaveFilePath,trackerFilePath,trackerIdNumberLabel,trackerType,self=None):
    
    # read in data from annotation json txt file
    data = json.loads(pathlib.Path(annotationSaveFilePath).read_text())
    # convert json to df
    df = pd.json_normalize(data) # df is a one row dataframe
                
    # read in tracker df
    all_df = pd.read_csv(trackerFilePath)
    
    # append the pd df data object from the annotation json as a new row in the tracker file
    # this will be a row append with outer join on columns - will help accommodate any changes to fields/schema over time
    all_df = pd.concat([all_df, df], axis=0) 

    all_df.sort_values(by = [trackerIdNumberLabel], inplace=True)
    # drop any exact duplicate rows
    all_df = all_df[-(all_df.astype('string').duplicated())]

    all_df.to_csv(trackerFilePath, mode='w', header=True, index=False)

    messageText = "The contents of the " + trackerType + " annotation file at: <br><br>" + annotationSaveFilePath + "<br><br>was added as a new record to the " + trackerType.title() + " Tracker file: <br><br>" + trackerFilePath
        
    if self:
        errorFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
    else:
        print(messageText)
    return True

def singleAddDefaultToNewlyAddedSchemaKey(data,schemaKey,schemaKeyDefault):
    dataUpdate = False
    noUpdateReason = ""
    
    if ((schemaKey in data) and (not data[schemaKey]) and (data[schemaKey] != schemaKeyDefault)):
        dataUpdate = True
        data[schemaKey] = schemaKeyDefault
    else: 
        if schemaKey not in data:
            noUpdateReason = noUpdateReason + "key not in schema"
        else:
            if data[schemaKey]:
                noUpdateReason = noUpdateReason + "key value has already been set to a value that is not none"
            if data[schemaKey] == schemaKeyDefault:
                if noUpdateReason:
                    noUpdateReason = noUpdateReason + "; key value has already been set to the default value"
                else: 
                    noUpdateReason = noUpdateReason + "key value has already been set to the default value"

    return dataUpdate,noUpdateReason,data

def allAddDefaultToNewlyAddedSchemaKey(metadataDirPath, trkDict, schemaKeyList, schemaKeyDefaultList):
    
    annotationFilePathList, namelist, stemlist, idnumlist = getLatestAnnotationJsonTxtFiles(trkDict=trkDict,metadataDirPath=metadataDirPath)
    
    trackerIdNumberLabel = trkDict["trackerIdNumberLabel"]

    if annotationFilePathList:
        #### lists pertaining to files that are updated
        dataUpdateIdNumberList = []
        dataUpdateList = []
        dataUpdateStatusDetailList = []
        dataUpdateNoUpdateReasonDetailList = []

        #### lists pertaining to files that are NOT updated
        dataNoUpdateIdNumberList = []
        dataNoUpdateStatusDetailList = []
        dataNoUpdateNoUpdateReasonDetailList = []

        for p in annotationFilePathList:
            
            with open(p) as f:
                data = json.load(f)

                currentDataUpdateStatusList = []
                currentDataNoUpdateReasonList = []

                for schemaKey,schemaKeyDefault in zip(schemaKeyList,schemaKeyDefaultList):
                    dataUpdate,noUpdateReason,data = singleAddDefaultToNewlyAddedSchemaKey(data=data,schemaKey=schemaKey,schemaKeyDefault=schemaKeyDefault)
                    currentDataUpdateStatusList.append(dataUpdate)
                    currentDataNoUpdateReasonList.append(noUpdateReason)

                if any(currentDataUpdateStatusList):
                    dataUpdateList.append(data)
                    dataUpdateIdNumberList.append(data[trackerIdNumberLabel])
                    dataUpdateStatusDetailList.append(currentDataUpdateStatusList)
                    dataUpdateNoUpdateReasonDetailList.append(currentDataNoUpdateReasonList)
                else:
                    dataNoUpdateIdNumberList.append(data[trackerIdNumberLabel])
                    dataNoUpdateStatusDetailList.append(currentDataUpdateStatusList)
                    dataNoUpdateNoUpdateReasonDetailList.append(currentDataNoUpdateReasonList)

    return {
        "dataUpdateList": dataUpdateList,
        "dataUpdateIdNumberList": dataUpdateIdNumberList,
        "dataUpdateStatusDetailList": dataUpdateStatusDetailList,
        "dataUpdateNoUpdateReasonDetailList": dataUpdateNoUpdateReasonDetailList,
        "dataNoUpdateIdNumberList": dataNoUpdateIdNumberList,
        "dataNoUpdateStatusDetailList": dataNoUpdateStatusDetailList,
        "dataNoUpdateNoUpdateReasonDetailList": dataNoUpdateNoUpdateReasonDetailList,
        }

def preProgrammaticEdit(metadataDirPath,trkDict,metadataDirLockFileName=metadataDirLockFileName):

    # check if this data package dir is in use by another user, 
    # if it is, don't allow the current user to select this data package to work on
    # if it is not, allow the current user to select this data package to work on AND write a file that "checks out" this data package dir so that if another user tries to use it at the same time it will not allow it
    lockFileExists = checkMetadataDirLockFile(metadataDirPath=metadataDirPath,metadataDirLockFileName=metadataDirLockFileName)["lockFileExists"]           

    # for editing need to check if json txt annotation files are updated - if not updated, will break the form import
    # so do full check for if update is necessary to get update status of trackers and json txt annotation files
    versionCheck = version_check.version_check(workingDataPkgDir=metadataDirPath,trackersImplemented=[trkDict],writeVersionCheckToFile=False)
    versionCheckAllUpToDate = versionCheck[0]
    versionCheckMessage= versionCheck[1]
    versionCheckDf = versionCheck[2]

    if ((lockFileExists) or (not versionCheckAllUpToDate)):
        print("can't proceed, exiting: ")
        if lockFileExists:
            print("metadata dir is checked out")
        if not versionCheckAllUpToDate:
            print("metadata dir requires schema updates")
        return False
    else:
        # create an in-use file to "check out" the dsc-pkg and prevent modification of this local copy by more than one person at a time  
        print("checking out metdata dir to edit")
        writeMetadataDirLockFile(metadataDirPath=metadataDirPath,metadataDirLockFileName=metadataDirLockFileName,lockFileMode="programmatic")
        return True

def programmaticEdit(metadataDirPath,trkDict,dataUpdateList,mode):  

    trackerIdNumberLabel = trkDict["trackerIdNumberLabel"]            

    if dataUpdateList:
        succeedSaveIdNumberList = []
        failSaveIdNumberList = []
        failSaveReasonList = []

        for d in dataUpdateList:
            print(d[trackerIdNumberLabel])

            #TODO: add check here for customConditionalEditWarning, customConditionalEditDefaults
            
            saveStatus, saveStatusMessage = save_annotation(data=d,trackerDict=trkDict,saveFolderPath=metadataDirPath,mode=mode)
            if not saveStatus:
                failSaveIdNumberList.append(d[trackerIdNumberLabel])
                failSaveReasonList.append(saveStatusMessage)
            else:
                succeedSaveIdNumberList.append(d[trackerIdNumberLabel])

    return succeedSaveIdNumberList,failSaveIdNumberList,failSaveReasonList    

def postProgrammaticEdit(metadataDirPath,metadataDirLockFileName=metadataDirLockFileName):
            
    destroyMetadataDirLockFile(metadataDirPath=metadataDirPath,metadataDirLockFileName=metadataDirLockFileName)
        




