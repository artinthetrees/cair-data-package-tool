import sys
import os

import json
import copy

#from PyQt5 import QtWidgets, QtCore, QtGui
from qtpy import QtWidgets, QtCore, QtGui

#from qt_jsonschema_form import WidgetBuilder
from pyqtschema.builder import WidgetBuilder

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils
import cair_data_package_tool.back_door_edit as back_door_edit

from layout_csvviewwidget import CSVViewWindow


class ScrollAnnotateWindow(QtWidgets.QMainWindow):
    def __init__(
            self, 
            workingDataPkgDirDisplay,
            workingDataPkgDir,
            trackerDict,
            trackersToAddToTool, 
            filesCheckList = [], 
            mode = "add"):
        super().__init__()
        self.w2 = None  # No external window yet.
        self.loadingFormDataFromFile = False

        # inherited vars
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.workingDataPkgDir = workingDataPkgDir
        self.trackerDict = trackerDict
        self.trackersToAddToTool = trackersToAddToTool
        self.filesCheckList = filesCheckList
        self.mode = mode

        # pull out of trackerDict inherited var for immediate use
        self.trackerType = self.trackerDict["trackerType"]
        self.schema = self.trackerDict["schema"]

        if self.schema.get("customDynamicEnum"):
            print("customDynamicEnum")
            for i in self.schema.get("customDynamicEnum"):
                prop = i["prop"]
                print(prop)
                fromTrackerType = i["fromTrackerType"]
                print(fromTrackerType)
                fromProp = i["fromProp"]
                print(fromProp)
                includeLatestOnly = i["includeLatestOnly"]
                includeRemoved = i["includeRemoved"]
                fromTrackerDict = [d for d in self.trackersToAddToTool if d["trackerType"] == fromTrackerType]
                #print(fromTrackerDict)
                
                if fromTrackerDict:
                    print(1)
                    fromTrackerDict = fromTrackerDict[0]
                    fromTrackerSchema = fromTrackerDict["schema"]
                    if fromProp in fromTrackerSchema["properties"]:
                        print(2)
                        if fromTrackerSchema["properties"][fromProp]["type"] == "string":
                            print(3)
                            if fromProp == fromTrackerDict["trackerNameLabel"]:
                                print(4)
                                valueList, valueDf = back_door_edit.get_names(trackerDict=fromTrackerDict,saveFolderPath=self.workingDataPkgDir)
                            else:
                                valueList, valueDf = back_door_edit.get_unique_prop_vals(trackerProperty=fromProp,trackerDict=fromTrackerDict,saveFolderPath=self.workingDataPkgDir,propertyDefaultValue=[],includeLatestOnly=True,includeRemoved=False)
                
                            if valueList:
                                print(valueList)
                                self.schema = dsc_pkg_utils.dynamic_add_enums_to_schema_property(propertyToUpdate=prop,schema=self.schema,enumList=valueList)

        self.schemaVersion = self.trackerDict["schemaVersion"] 
    
        self.trackerTitle = self.trackerDict["trackerTitle"] 
        self.trackerName = self.trackerDict["trackerName"] 
        
        self.trackerFileBaseName = self.trackerDict["trackerFileBaseName"] 
        self.trackerFileName = self.trackerDict["trackerFileName"] 
        
        self.trackerJsonFilePrefix = self.trackerDict["trackerJsonFilePrefix"] 
        
        self.trackerIdLabel = self.trackerDict["trackerIdLabel"] 
        self.trackerIdNumberLabel = self.trackerDict["trackerIdNumberLabel"] 
        self.trackerNameLabel = self.trackerDict["trackerNameLabel"] 
        self.trackerDescriptionLabel = self.trackerDict["trackerDescriptionLabel"] 
        
        self.trackerFirstId = self.trackerDict["trackerFirstId"] 
        self.trackerDefaultName = self.trackerDict["trackerDefaultName"] 
        self.trackerIdPrefix = self.trackerDict["trackerIdPrefix"] 
        
        self.initUI()

    def initUI(self):
        self.scroll = QtWidgets.QScrollArea()             # Scroll Area which contains the widgets, set as the centralWidget
        self.widget = QtWidgets.QWidget()                 # Widget that contains the collection of Vertical Box
        self.vbox = QtWidgets.QVBoxLayout()               # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.mfilehbox = QtWidgets.QHBoxLayout()
        
        self.saveFolderPath = self.workingDataPkgDir
        self.trackerFilePath = os.path.join(self.saveFolderPath,self.trackerFileName)

        self.annotationId = None
        self.annotationIdNumber = None
        self.annotationSaveFileName = None
        self.annotationSaveFilePath = None
        
        self.priorityContentList = None

        ################################## Create component widgets - form, save button, status message box
        
        # create the form widget 
        self.ui_schema = {}

        # parse custom/optional "ui" key for each property that allows use of non-default widget for each property
        # currently using to, for example, use qtextedit instead of qlineedit for string props that are expected to be 
        # long strings 
        for k,v in self.schema["properties"].items():
            if v.get("ui"):
                self.ui_schema[k] = {
                    "ui:widget": v["ui"]
                }
        
        self.builder = WidgetBuilder(self.schema)
        self.form = self.builder.create_form(self.ui_schema)

        self.formDefaultState = {
            "schemaVersion": self.schemaVersion
        }
        self.formDefaultState[self.trackerIdLabel] = self.trackerFirstId
        if self.trackerNameLabel in self.formDefaultState:
            self.formDefaultState[self.trackerNameLabel] = self.trackerDefaultName

        if self.schema.get("customDefaults"):
            for i in self.schema["customDefaults"]:
                self.formDefaultState[i["prop"]] = i["propValue"]

        self.form.widget.state = copy.deepcopy(self.formDefaultState)
        
        # create save button
        self.buttonSave = QtWidgets.QPushButton(text="Save " + self.trackerType,parent=self)
        # self.buttonSave.clicked.connect(self.save_annotation)
        #self.buttonSave.clicked.connect(functools.partial(back_door_edit.save_annotation,self))
        #.on_changed.connect(lambda saveStatus: self.check_name_unique("check"))
        self.buttonSave.clicked.connect(lambda : back_door_edit.save_annotation(self=self))
        
        self.buttonSave.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonSave.setStyleSheet("QPushButton{background-color:rgba(10,105,33,100);} QPushButton:hover{background-color:rgba(0,125,0,50);}");
        

         # create clear form button
        self.buttonClearForm = QtWidgets.QPushButton(text="Clear form",parent=self)
        self.buttonClearForm.clicked.connect(self.clear_form)

        self.buttonClearForm.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding
        )
        self.buttonClearForm.setStyleSheet("QPushButton{background-color:rgba(196,77,86,100);} QPushButton:hover{background-color:rgba(196,30,58,50);}");
        
        # create status message box
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        self.messageText = ""
        self.userMessageBox.setText(self.messageText)

        self.labelUserMessageBox = QtWidgets.QLabel(text = "User Status Message Box:", parent=self)
       
        ################################## Apply some initializing and maintenance functions

        # initialize tool tip for each form field based on the description text for the corresponding schema property
        self.add_tooltip()
        self.add_priority_highlight_and_hide()
        if self.mode == "add":
            dsc_pkg_utils.get_id(filePrefix=self.trackerJsonFilePrefix,folderPath=self.saveFolderPath,firstIdNum=1,fileExt=".txt",self=self)
            self.conditional_fields_on_init()

        # check for empty tooltip content whenever form changes and replace empty tooltip with original tooltip content
        # (only relevant for fields with in situ validation - i.e. string must conform to a pattern - as pyqtschema will replace the 
        # tooltip content with some error content, then replace the content with empty string once the error is cleared - this check will
        # restore the original tooltip content - for efficiency, may want to only run this when a widget that can have validation 
        # errors changes - #TODO)
        self.form.widget.on_changed.connect(self.check_tooltip)
        
        if self.schema.get("customCheckFormChange"):
            for i in self.schema["customCheckFormChange"]:
                self.formWidgetList[self.formWidgetNameList.index(i)].on_changed.connect(self.conditional_fields)

        if self.trackerNameLabel in self.formDefaultState:
            self.formWidgetList[self.formWidgetNameList.index(self.trackerNameLabel)].on_changed.connect(lambda saveStatus: back_door_edit.check_name_unique(saveStatus=False,self=self))
        #self.formWidgetList[self.formWidgetNameList.index(self.trackerNameLabel)].on_changed.connect(lambda saveStatus: self.check_name_unique("check"))
        #self.formWidgetList[self.formWidgetNameList.index(self.trackerIdLabel)].on_changed.connect(self.sync_id_and_id_number)

        ################################## Finished creating component widgets
        

        self.vbox.addWidget(self.buttonSave)
        #self.vbox.addWidget(self.buttonClearForm)
        self.vbox.addWidget(self.labelUserMessageBox)
        self.vbox.addWidget(self.userMessageBox)
        self.vbox.addWidget(self.form)
        
        self.widget.setLayout(self.vbox)

        #Scroll Area Properties
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)

        self.setCentralWidget(self.scroll)

        self.setGeometry(600, 100, 1000, 900)
        if self.mode == "add":
            self.setWindowTitle("Annotate " + self.trackerType.title())
        elif self.mode == "edit":
            self.setWindowTitle("Edit " + self.trackerType.title())
        elif self.mode == "add-based-on":
            self.setWindowTitle("Annotate New " + self.trackerType.title() + " based on existing " + self.trackerType.title())

        return
        
    def scrollScrollArea (self, topOrBottom, minVal=None, maxVal=None):
        # Additional params 'minVal' and 'maxVal' are declared because
        # rangeChanged signal sends them, but we set it to optional
        # because we may need to call it separately (if you need).

        if topOrBottom == "bottom":
    
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()
            )

        if topOrBottom == "top":
    
            self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().minimum()
            )

    def add_tooltip(self):
        
        self.toolTipContentList = []
        self.formWidgetNameList =  []
        self.formWidgetList = []

        
        for key, value in self.form.widget.widgets.items():
            name = key
            widget = value

            #print(name)
            #print(widget)

            toolTipContent = self.schema["properties"][name]["description"] 
            #print("tool tip content: ",toolTipContent)
            
            widget.setToolTip(toolTipContent)
            self.toolTipContentList.append(toolTipContent)
            
            self.formWidgetNameList.append(name)
            self.formWidgetList.append(widget)
    
    def add_priority_highlight_and_hide(self):

        self.formLabelWidgetList = []
        self.formLabelWidgetTextList = []
        self.formLabelWidgetTypeList = []
        
        l = self.form.widget.layout() # get form widget layout (it's a qgridlayout)
        
        wList = (l.itemAt(i).widget() for i in range(l.count())) # get a list of the widgets in the layout
        for idx, w in enumerate(wList): # collect all the qlabel widgets in the layout (for array widgets you have to collect the title instead)
            
            if isinstance(w, QtWidgets.QLabel):
                self.formLabelWidgetList.append(w)
                self.formLabelWidgetTextList.append(w.text())
                self.formLabelWidgetTypeList.append("label")
            
            if isinstance(w, QtWidgets.QGroupBox):
                self.formLabelWidgetList.append(w)
                self.formLabelWidgetTextList.append(w.title())
                self.formLabelWidgetTypeList.append("groupbox")

        newList = None

        if not self.priorityContentList:
            newList = True
            self.priorityContentList = []  

        for key, value in self.form.widget.widgets.items():
            fColor = None
            name = key
            widget = value
            
            titleContent = self.schema["properties"][name]["title"] 
            priorityContent = self.schema["properties"][name]["priority"]
            
            if newList:
                self.priorityContentList.append(priorityContent)
            
            if titleContent in self.formLabelWidgetTextList:
                labelWidgetIdx = self.formLabelWidgetTextList.index(titleContent)
                labelWidget = self.formLabelWidgetList[labelWidgetIdx]
                labelWidgetType = self.formLabelWidgetTypeList[labelWidgetIdx]

           
                if ", high" in priorityContent:
                    fColor = "green"
                    if ", auto" in priorityContent:
                        fColor = "blue"
                
                if fColor: 
                    if (labelWidgetType == "label"):
                        labelWidget.setText('<font color = ' + fColor + '>' + labelWidget.text() + '</font>')
                    if (labelWidgetType == "groupbox"):
                        #labelWidget.setTitle('<font color = ' + fColor + '>' + labelWidget.title() + '</font>')
                        labelWidget.setStyleSheet('QGroupBox  {color: ' + fColor + ';}')

                labelWidget.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

                if not priorityContent.startswith("all, "):
                    labelWidget.hide()
                    widget.hide()

   
    def check_tooltip(self):
        i = 0
        for key, value in self.form.widget.widgets.items():
            name = key
            widget = value

            toolTipContent = widget.toolTip() # get current tool tip content
            if not toolTipContent: # check if the tool tip string is empty (this will occur if a validation error happened and error message was displayed and then the error was resolved as tooltip will be set to empty by pyqtschema pkg upon clearing the error)
                widget.setToolTip(self.toolTipContentList[i]) # if empty then set it to the tooltip content from schema description that was stored on initialization

            i+=1 # increment

    def sync_id_and_id_number(self):
        newId = self.form.widget.state[self.trackerIdLabel]
        newIdNumber = int(newId.rsplit("-",1)[1])
        self.form.widget.state[self.trackerIdNumberLabel] = newIdNumber

    def toggle_widgets(self, keyText, desiredToggleState, deleteIfHidden=True):
        #print("troubleshoot toggle_widgets...")
        #print("keyText: ",keyText)
        #print([x for x in self.schema["properties"]])
        #print([list(map(str.strip, x.split(','))) for x in self.priorityContentList])
        #indices = [i for i, x in enumerate(self.priorityContentList) if keyText in x.split(", ")]
        indices = [i for i, x in enumerate(self.priorityContentList) if keyText in list(map(str.strip, x.split(',')))]
        #print("indices: ",indices)
        #print("desiredToggleState: ",desiredToggleState)

        for i in indices:
            labelW = self.formLabelWidgetList[i]
            labelWType = self.formLabelWidgetTypeList[i]
            labelWText = self.formLabelWidgetTextList[i]
            fieldW = self.formWidgetList[i]
            fieldWName = self.formWidgetNameList[i]

            #print("label widget: ")
            #print(labelW)
            #print(labelWType)
            #print(labelWText)
            #print("field widget: ")
            #print(fieldW)
            #print(fieldWName)

            if desiredToggleState == "show":
                labelW.show()
                fieldW.show()
            
            if desiredToggleState == "hide":
                labelW.hide()
                fieldW.hide()
                if deleteIfHidden:
                    # if theres a default value for the field use it
                    if fieldWName in self.formDefaultState:
                        self.form.widget.state[fieldWName] = self.formDefaultState[fieldWName]
                        return

                    # otherwise use widget type specific clear method 
                    if self.schema["properties"][fieldWName]["type"] == "string":
                        # fieldW.clear()
                        self.form.widget.state[fieldWName] = ""
                        if "enum" in self.schema["properties"][fieldWName]:
                            fieldW.setCurrentIndex(0)
                    elif self.schema["properties"][fieldWName]["type"] == "array":
                        # for row in fieldW.rows:
                        #     fieldW._remove_item(row)

                        # fieldW.on_changed.emit(fieldW.state)
                        self.form.widget.state[fieldWName] = []
    
    def toggle_widget_by_name(self, name, desiredToggleState, deleteIfHidden=True):

        fieldW = self.formWidgetList[self.formWidgetNameList.index(name)]
        labelW = self.formLabelWidgetList[self.formWidgetNameList.index(name)]

        if desiredToggleState == "show":
            labelW.show()
            fieldW.show()
        
        if desiredToggleState == "hide":
            labelW.hide()
            fieldW.hide()
            if deleteIfHidden:
                fieldW.clear()

    def set_read_only_widget_by_name(self, name):

        fieldW = self.formWidgetList[self.formWidgetNameList.index(name)]
        labelW = self.formLabelWidgetList[self.formWidgetNameList.index(name)]

        fieldW.setReadOnly(True)

    def set_disabled_widget_by_name(self, name=None, allNames=False):

        if allNames:
            names = [k for k in self.schema["properties"]]
        else:
            names = [name]
        
        for name in names:
            fieldW = self.formWidgetList[self.formWidgetNameList.index(name)]
            labelW = self.formLabelWidgetList[self.formWidgetNameList.index(name)]

            fieldW.setEnabled(False)

    def conditional_fields_on_init(self):

        if self.schema.get("customConditionalHideOnInit"):
            for i in self.schema["customConditionalHideOnInit"]:
                if i["propValueRelation"] == "equal":
                    if self.form.widget.state[i["propToCheck"]] == i["propValue"]:
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
                    else:
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"])   

                if i["propValueRelation"] == "startsWith":
                    if self.form.widget.state[i["propToCheck"]].startswith(i["propValue"]):
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
                    else:
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"]) 

                if i["propValueRelation"] == "valueInProp":
                    if i["propValue"] in self.form.widget.state[i["propToCheck"]]:
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
                    else:
                        self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"])  

    def conditional_fields(self, changedFieldName):

        def parseCustomConditionalValueUnit(unit):
            if unit["propValueRelation"] == "equal":
                if self.form.widget.state[unit["propToCheck"]] == unit["propValue"]:
                    if isinstance(unit["ifValue"],str):
                        #self.form.widget.state[unit["impactedProp"]] == unit["ifValue"]
                        self.form.widget.state = {
                            unit["impactedProp"]: unit["ifValue"]
                        }

                    else:
                        parseCustomConditionalValueUnit(unit=unit["ifValue"])
                else:
                    if isinstance(unit["elseValue"],str):
                        #self.form.widget.state[i["impactedProp"]] == i["elseValue"]
                        self.form.widget.state = {
                            unit["impactedProp"]: unit["elseValue"]
                        }
                    else:
                        parseCustomConditionalValueUnit(unit=unit["ifValue"])            


        if self.schema.get("customConditionalValue"):
            for i in self.schema["customConditionalValue"]:
                parseCustomConditionalValueUnit(unit=i)

        ##########################################################

        def subParseCustomConditionalHide(self,unit,ifOrElse,userMessageBox):
            actionVar = ifOrElse + "Action"
            messageTextVar = ifOrElse + "MessageText"
            messageTextTypeVar = ifOrElse + "MessageTextType"

            print("unit: ",unit)

            if (messageTextVar in unit) and (unit.get(messageTextVar)):
                messageText = unit.get(messageTextVar)
                print("messageText: ",messageText)
                if userMessageBox:
                    if (messageTextTypeVar in unit) and (unit.get(messageTextTypeVar)):
                        messageTextType = unit.get(messageTextTypeVar)
                        print("messageTextType: ",messageTextType)
                        if messageTextType == "notify":
                            saveFormat = '<span style="color:blue;">{}</span>'
                        elif messageTextType == "warn":
                            saveFormat = '<span style="color:red;">{}</span>'
                        elif messageTextType == "proceed":
                            saveFormat = '<span style="color:green;">{}</span>'
                    userMessageBox.append(saveFormat.format(messageText))
                    # set text color back to default after appending 
                    saveFormat = '<span style="color:black;">{}</span>'
                else:
                    print(messageText)


            if not unit[actionVar]: 
                return 

            if isinstance(unit["impactedPropKeyText"],list):
                impactedPropKeyTextList = unit["impactedPropKeyText"]
            else:
                impactedPropKeyTextList = None

            if isinstance(unit[actionVar],str):
                # TODO: catch if actionVar is not hide or show
                if not impactedPropKeyTextList:
                    self.toggle_widgets(keyText = unit["impactedPropKeyText"], desiredToggleState = unit[actionVar])
                else:
                    [self.toggle_widgets(keyText = currentImpactedPropKeyText, desiredToggleState = unit[actionVar]) for currentImpactedPropKeyText in impactedPropKeyTextList] 
            else:
                parseCustomConditionalHide(self,unit=unit[actionVar],userMessageBox=userMessageBox)
                return 


        def parseCustomConditionalHide(self,unit,userMessageBox):
            availablePropValueRelations = ["equal","startsWith","endsWith","valueInProp"]
            if unit["propValueRelation"] not in availablePropValueRelations:
                print("propValueRelation can only be one of the following values for now: ", ", ".join(availablePropValueRelations))

            if unit["propValueRelation"] == "equal":
                if self.form.widget.state[unit["propToCheck"]] == unit["propValue"]:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="if",userMessageBox=userMessageBox) 
                else:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="else",userMessageBox=userMessageBox) 

            if unit["propValueRelation"] == "startsWith":
                if self.form.widget.state[unit["propToCheck"]].startswith(unit["propValue"]):
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="if",userMessageBox=userMessageBox) 
                else:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

            if unit["propValueRelation"] == "endsWith":
                if self.form.widget.state[unit["propToCheck"]].endswith(unit["propValue"]):
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="if",userMessageBox=userMessageBox) 
                else:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

            if unit["propValueRelation"] == "valueInProp":
                if unit["propValue"] in self.form.widget.state[unit["propToCheck"]]:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="if",userMessageBox=userMessageBox) 
                else:
                    subParseCustomConditionalHide(self,unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

        if self.schema.get("customConditionalHide"):
            for i in self.schema["customConditionalHide"]:
                parseCustomConditionalHide(self,unit=i,userMessageBox=self.userMessageBox)
                
        ##########################################################

        # if self.schema.get("customConditionalHide"):
        #     for i in self.schema["customConditionalHide"]:
        #         if i["propValueRelation"] == "equal":
        #             if self.form.widget.state[i["propToCheck"]] == i["propValue"]:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
        #             else:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"])   

        #         if i["propValueRelation"] == "startsWith":
        #             if self.form.widget.state[i["propToCheck"]].startswith(i["propValue"]):
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
        #             else:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"]) 

        #         if i["propValueRelation"] == "endsWith":
        #             if self.form.widget.state[i["propToCheck"]].endswith(i["propValue"]):
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
        #             else:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"])
                        
        #         if i["propValueRelation"] == "valueInProp":
        #             if i["propValue"] in self.form.widget.state[i["propToCheck"]]:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["ifAction"]) 
        #             else:
        #                 self.toggle_widgets(keyText = i["impactedPropKeyText"], desiredToggleState = i["elseAction"])  
    
    def clear_form(self):

        clearState = copy.deepcopy(self.form.widget.state)
        
        for key, value in clearState.items():
            if type(value) is str:
                clearState[key] = ""
            if type(value) is list:
                clearState[key] = []

        for key, value in clearState.items():
            if key in self.formDefaultState.keys():
                clearState[key] = self.formDefaultState[key]
        
        for key, value in self.form.widget.state.items():

            self.form.widget.state = {
                key: clearState[key]
            } 

        messageText = "<br>Your form was successfully cleared and you can start annotating a new term"
        saveFormat = '<span style="color:green;">{}</span>'
        self.userMessageBox.append(saveFormat.format(messageText))
        self.userMessageBox.moveCursor(QtGui.QTextCursor.End)

        dsc_pkg_utils.get_id(filePrefix=self.trackerJsonFilePrefix,folderPath=self.saveFolderPath,firstIdNum=1,fileExt=".txt",self=self)
        self.conditional_fields_on_init()

        self.userMessageBox.moveCursor(QtGui.QTextCursor.End)           

    def select_load_file(self):

        tracker_file_name = os.path.join(self.workingDataPkgDir,self.trackerFileName)
        
        if self.mode == "edit":
            viewerMode = "select to edit"
        elif self.mode == "add-based-on":
            viewerMode = "select to add based on"
        
        if self.w2 is None:
            self.w2 = CSVViewWindow(fileName=tracker_file_name,fileStartsWith="",fileTypeTitle=self.trackerTitle,viewerMode=viewerMode)
            self.w2result = self.w2.exec_()
            self.parse_load_file()
        else:
            self.w2.close()  # Close window.
            self.w2 = None  # Discard reference.
            self.w2 = CSVViewWindow(fileName=tracker_file_name,fileStartsWith="",fileTypeTitle=self.trackerTitle,viewerMode=viewerMode)
            self.w2result = self.w2.exec_()
            self.parse_load_file()     

    def parse_load_file(self):
        #self.filesCheckList = [pathlib.Path(p) for p in self.filesCheckList]
        self.loadingFormDataFromFile = True

        if self.mode == "edit":
            textBit = "edit"
            textButton = "\"Edit an existing " + self.trackerType + "\""
        elif self.mode == "add-based-on":
            textBit = "base a new " + self.trackerType + " upon"
            textButton = "\"Add a new " + self.trackerType + " based on an existing " + self.trackerType + "\""
    
        if not self.w2.selected_row_data_col_names: 
            messageText = "<br>You have not selected a file to " + textBit + ". Close this form now. If you still want to " + textBit + " an existing term, Navigate to the \"" + self.trackerTitle + "\" tab >> \"Add " + self.trackerType.title() + "\" sub-tab and click the " + textButton + " push-button."
            saveFormat = '<span style="color:red;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText)) 
            self.set_disabled_widget_by_name(allNames=True)
            self.buttonSave.setEnabled(False)
            return

        selected_id_index = self.w2.selected_row_data_col_names.index(self.trackerIdLabel) 
        selected_id = self.w2.selected_row_data[selected_id_index] 
        selected_id_base_filename = self.trackerJsonFilePrefix + selected_id + ".txt" 
        selected_id_full_path_filename = os.path.join(self.workingDataPkgDir,selected_id_base_filename)
        self.load_file(path=selected_id_full_path_filename)

    def load_file(self,path):
    
        ifileName = path

        with open(ifileName, 'r',encoding='utf-8') as stream:
            data = json.load(stream)

        if self.mode == "add-based-on":
            based_on_annotation_id = data[self.trackerIdLabel]
            #######################################
            # for add based on (not edit) mode
            # do the following
            #######################################

            if self.schema.get("customAddBasedOnDefaults"):
                for i in self.schema["customAddBasedOnDefaults"]:
                    data[i["prop"]] = i["propValue"]

        if self.mode == "edit":         
    
            #######################################
            # for editing terms (not add based on)
            # do the following
            #######################################

            ########################
            # start utility fxs
            # TODO: move to module
            ########################
            
            def warnWidget(warnUnit,userMessageBox):
                next_options =["Yes","No"]
                chosen_option, chosen_done = QtWidgets.QInputDialog.getItem(
                    self, 
                    warnUnit["warnWindowTitle"], 
                    warnUnit["warnWindowText"], 
                    next_options)

                if chosen_done:
                    chosen_option=str(chosen_option)
                    if chosen_option == "No":
                        # do not proceed with loading file to edit
                        messageText = warnUnit["chooseNoProceedText"]
                        if userMessageBox:
                            saveFormat = '<span style="color:red;">{}</span>'
                            userMessageBox.append(saveFormat.format(messageText))
                        else:
                            print(messageText)
                        return False
                    else:
                        # proceed with loading file to edit
                        messageText = warnUnit["chooseProceedText"]
                        if userMessageBox:
                            saveFormat = '<span style="color:red;">{}</span>'
                            userMessageBox.append(saveFormat.format(messageText))
                        else:
                            print(messageText)
                        return True

                else:
                    # do not proceed with loading file to edit
                    messageText = warnUnit["chooseNoProceedText"]
                    if userMessageBox:
                        saveFormat = '<span style="color:red;">{}</span>'
                        userMessageBox.append(saveFormat.format(messageText))
                    else:
                        print(messageText)
                    return False 

            def subParseCustomConditionalEditWarning(unit,ifOrElse,userMessageBox):
                actionVar = ifOrElse + "Action"
                warnWindowTitleVar = ifOrElse + "WarnWindowTitle"
                warnWindowTextVar = ifOrElse + "WarnWindowText"
                chooseProceedTextVar = ifOrElse + "ChooseProceedText"
                chooseNoProceedTextVar = ifOrElse + "ChooseNoProceedText"

                if not unit[actionVar]: #
                    return True
                
                if isinstance(unit[actionVar],str):
                    if unit[actionVar] == "warn":
                        warnUnit = copy.deepcopy(unit)
                        warnUnit["warnWindowTitle"] = warnUnit[warnWindowTitleVar]
                        warnUnit["warnWindowText"] = warnUnit[warnWindowTextVar]
                        warnUnit["chooseProceedText"] = warnUnit[chooseProceedTextVar]
                        warnUnit["chooseNoProceedText"] = warnUnit[chooseNoProceedTextVar]
                        proceedDespiteWarn = warnWidget(warnUnit=warnUnit,userMessageBox=userMessageBox)
                        return proceedDespiteWarn
                    else: 
                        print("something is wrong, the only accepted string value for " + actionVar + " is: warn")
                        return False
                else:
                    proceedDespiteWarn = parseCustomConditionalEditWarning(unit=unit[actionVar],userMessageBox=userMessageBox)
                    return proceedDespiteWarn


            def parseCustomConditionalEditWarning(unit,userMessageBox):
                if unit["propValueRelation"] not in ["equal","notEqual","startsWith"]:
                    print("propValue relation can only be one of the following values for now: equal, notEqual, startsWith")
                    proceedDespiteWarn = False
                
                if unit["propValueRelation"] == "equal":
                    if data[unit["propToCheck"]] == unit["propValue"]:
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="if",userMessageBox=userMessageBox)
                    else:
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

                if unit["propValueRelation"] == "notEqual":
                    if data[unit["propToCheck"]] != unit["propValue"]:
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="if",userMessageBox=userMessageBox)
                    else:
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

                if unit["propValueRelation"] == "startsWith":
                    if data[unit["propToCheck"]].startswith(unit["propValue"]):
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="if",userMessageBox=userMessageBox)
                    else:
                        proceedDespiteWarn = subParseCustomConditionalEditWarning(unit=unit,ifOrElse="else",userMessageBox=userMessageBox)

                return proceedDespiteWarn

            ###########################

            def applyDefault(defaultUnit,data):
                if isinstance(defaultUnit["propValue"],dict):
                    if defaultUnit["propValue"].get("propValueFromData"):
                        data[defaultUnit["prop"]] = data[defaultUnit["propValue"]["propValueFromDataVar"]]
                    elif defaultUnit["propValue"].get("propValueFromDataPlusTransform"): 
                        tr_func_str = defaultUnit["propValue"].get("propValueFromDataTransformFx")
                        tr_func = getattr(dsc_pkg_utils,tr_func_str)

                        tr_func_param_dict = {}
                        params_from_data_var = defaultUnit["propValue"].get("propValueFromDataTransformFxParamsFromDataVar")
                        other_params = defaultUnit["propValue"].get("propValueFromDataTransformFxParamsOther")
                        
                        if params_from_data_var:
                            for k,v in params_from_data_var.items():
                                tr_func_param_dict[k] = data[v]

                        if other_params:
                            for k,v in other_params.items():
                                tr_func_param_dict[k] = v

                        data[defaultUnit["prop"]] = tr_func(**tr_func_param_dict)

                    else:
                        data[defaultUnit["prop"]] = defaultUnit["propValue"]  
                else: 
                    data[defaultUnit["prop"]] = defaultUnit["propValue"]

                return data
                

            def subParseCustomConditionalEditDefaults(unit,ifOrElse,data):
                actionVar = ifOrElse + "Action"
                defaultsVar = ifOrElse + "Defaults"

                if not unit[actionVar]: #
                    return data
                
                if isinstance(unit[actionVar],str):
                    if unit[actionVar] == "addDefaults":
                        for d in unit[defaultsVar]:
                            data = applyDefault(defaultUnit=d,data=data)
                        return data
                    else: 
                        print("something is wrong, the only accepted string value for " + actionVar + " is: addDefaults")
                        return False
                else:
                    data = parseCustomConditionalEditDefaults(unit=unit[actionVar])
                    return data


            def parseCustomConditionalEditDefaults(unit,data):
                if unit["propValueRelation"] not in ["equal","notEqual","startsWith"]:
                    print("propValue relation can only be one of the following values for now: equal, notEqual, startsWith")
                    return False
                
                if unit["propValueRelation"] == "equal":
                    if data[unit["propToCheck"]] == unit["propValue"]:
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="if",data=data)
                    else:
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="else",data=data)

                if unit["propValueRelation"] == "notEqual":
                    if data[unit["propToCheck"]] != unit["propValue"]:
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="if",data=data)
                    else:
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="else",data=data)

                if unit["propValueRelation"] == "startsWith":
                    if data[unit["propToCheck"]].startswith(unit["propValue"]):
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="if",data=data)
                    else:
                        data = subParseCustomConditionalEditDefaults(unit=unit,ifOrElse="else",data=data)

                return data

            ########################
            # end utility fxs
            # TODO: move to module
            ########################

            if self.schema.get("customConditionalEditWarning"):
                for i in self.schema["customConditionalEditWarning"]:
                    proceedDespiteWarn = parseCustomConditionalEditWarning(unit=i,userMessageBox=self.userMessageBox)
                    if not proceedDespiteWarn:
                        self.set_disabled_widget_by_name(allNames=True)
                        return
            
            if self.schema.get("customConditionalEditDefaults"):
                for i in self.schema["customConditionalEditDefaults"]:
                    data = parseCustomConditionalEditDefaults(unit=i,data=data)
                    if not data:
                        self.set_disabled_widget_by_name(allNames=True)
                        return
        
        self.form.widget.state = data
        
        if self.mode == "edit":
            self.conditional_fields_on_init() # this generalizes the customization - does it work?
            self.set_read_only_widget_by_name(name=self.trackerIdLabel)
                
        if self.mode == "add-based-on":
            dsc_pkg_utils.get_id(filePrefix=self.trackerJsonFilePrefix,folderPath=self.saveFolderPath,firstIdNum=1,fileExt=".txt",self=self)
            self.conditional_fields_on_init()
            messageText = "<br>Your new " + self.trackerType + " has been initialized based on information you entered for " + based_on_annotation_id + "<br><br>"
            saveFormat = '<span style="color:blue;">{}</span>'
            self.userMessageBox.append(saveFormat.format(messageText))

        self.loadingFormDataFromFile = False

            
          

        

if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    window = ScrollAnnotateWindow()
    window.show()
    sys.exit(app.exec_())