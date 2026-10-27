import os
from pathlib import Path
import re

import cair_data_package_tool.dsc_pkg_utils as dsc_pkg_utils

def update_add_files_list_from_form_field(property,self):

    property = property
    print("property in update items from form field fx: ",property) 
    print("form widget state: ",self.form.widget.state[property])
    print("add_files_items from dict: ",self.dynamic_customBulkAddFilePaths[property]["add_files_items"])

    # if user just added a new spot to add a file (no new file added yet), return
    current_form_widget_state = self.form.widget.state[property]
    current_form_widget_state_remove_empty = [i for i in current_form_widget_state if i]
    if current_form_widget_state != current_form_widget_state_remove_empty:
        return

    # if user added a file or deleted a file via the form field, 
    # 1) update the add_files_items in dict
    # 2) update the items listed in the add_files_box
    
    # 1)
    self.dynamic_customBulkAddFilePaths[property]["add_files_items"] = current_form_widget_state

    # 2) 
    # set to programmatic update
    self.dynamic_customBulkAddFilePaths[property]["add_files_items_programmatic_update"] = True
    
    self.dynamic_customBulkAddFilePaths[property]["add_files_box"].clear()
    self.dynamic_customBulkAddFilePaths[property]["add_files_box"].addItems(current_form_widget_state)

def update_add_files_list_from_box(property,self):
      
    property = property
    print("property in update items from box fx: ",property) 

    # if files in box are being updated programmatically, return         
    if self.dynamic_customBulkAddFilePaths[property]["add_files_items_programmatic_update"]:
        self.dynamic_customBulkAddFilePaths[property]["add_files_items_programmatic_update"] = False
        return

    add_files_box = self.dynamic_customBulkAddFilePaths[property]["add_files_box"]

    # store old items list
    oldLength = None
    if self.dynamic_customBulkAddFilePaths[property]["add_files_items"]:
        oldLength = len(self.dynamic_customBulkAddFilePaths[property]["add_files_items"])
        oldItems = self.dynamic_customBulkAddFilePaths[property]["add_files_items"]

        print(oldItems)
        print(oldLength)

    # update items list with what files/folders are actually in the box now
    updated_items_list = [add_files_box.item(x).text() for x in range(add_files_box.count())]
    
    # if there are any directories in the box now, get the files in the directory and add those to items list, replacing the name of the directory in the items list 
    refactored_items_list = []
    for i in updated_items_list:
        myPath = Path(i).resolve()
        if myPath.is_dir():
            # only unpack one level - i.e. if the dir has subdirs, the files in subdirs will not be unpacked via this method
            myFiles = [str(f) for f in myPath.iterdir() if f.is_file()]
            refactored_items_list.extend(myFiles)
        else:
            refactored_items_list.append(str(myPath))

    # update dictionary items list whether refactor to account for directories was necessary or not
    self.dynamic_customBulkAddFilePaths[property]["add_files_items"] = refactored_items_list
    
    if updated_items_list != refactored_items_list:
        self.dynamic_customBulkAddFilePaths[property]["add_files_items_programmatic_update"] = True

        self.dynamic_customBulkAddFilePaths[property]["add_files_box"].clear()
        self.dynamic_customBulkAddFilePaths[property]["add_files_box"].addItems(refactored_items_list)

    newLength = len(refactored_items_list)
    
    print("refactored_items_list: ",refactored_items_list)
    print("form state before: ", self.form.widget.state[property])
    self.form.widget.state = {
         property: refactored_items_list
    }
    print("form state after: ", self.form.widget.state[property])
    
    if oldLength:
        if ((oldLength > 0) and (newLength == 0)):
            print("hide")
            
            self.dynamic_customBulkAddFilePaths[property]["lbl"].hide()
            self.dynamic_customBulkAddFilePaths[property]["add_files_box"].hide()
            
def toggle_add_file_box_visibility(property,label,add_files_box,self):
    property = property
    print("property in toggle fx: ",property)

    if ((label.isHidden()) and (add_files_box.isHidden())):
        label.show()
        add_files_box.show()
    else:
        label.hide()
        add_files_box.hide()

def get_items_list(self):
    #item = QListWidgetItem(self.lstbox_view.currentItem())
    #print(item.text())
    if self.programmaticListUpdate:
        self.programmaticListUpdate = False
        return

    lw = self.lstbox_view
    
    oldLength = None
    if self.items:
        oldLength = len(self.items)
        oldItems = self.items

    self.items = [os.path.normpath(lw.item(x).text()) for x in range(lw.count())]
    print(self.items)

    refactorItems = []
    for i in self.items:
        print(i)
        if os.path.isdir(i):
            #self.programmaticListUpdate = True
            myFiles = [os.path.normpath(os.path.join(i,f)) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
            print(myFiles)
            refactorItems.extend(myFiles)
        else:
            refactorItems.append(i)

    if self.items != refactorItems:
        self.programmaticListUpdate = True

        self.items = refactorItems
        self.lstbox_view.clear()
        self.lstbox_view.addItems(self.items)

    newLength = len(self.items)
    print(self.items)  
    #print(type(self.items)) 
    print(len(self.items))

    if self.items:
        updatePath = self.items[0]
        updateAssocFileMultiLike = self.items
    else:
        updatePath = ""
        updateAssocFileMultiLike = []

    self.form.widget.state = {
        "path": updatePath,
        "associatedFileMultiLikeFiles": updateAssocFileMultiLike
    } 

    
    if len(self.items) > 1:
        print("show")
        indices = [i for i, x in enumerate(self.priorityContentList) if ("multiple like resource" in x) and ("permanent hide" not in x)]
        print(indices)
        for i in indices:
            labelW = self.formLabelWidgetList[i]
            print(labelW)
            labelWType = self.formLabelWidgetTypeList[i]
            print(labelWType)
            labelWText = self.formLabelWidgetTextList[i]
            print(labelWText)
            fieldW = self.formWidgetList[i]
            print(fieldW)
            fieldWName = self.formWidgetNameList[i]
            print(fieldWName)

            labelW.show()
            fieldW.show()

        self.labelApplyNameConvention.show()
        self.buttonApplyNameConvention.show()

    if oldLength:
        if ((oldLength > 1) and (newLength <= 1)):
            print("hide")
            indices = [i for i, x in enumerate(self.priorityContentList) if "multiple like resource" in x]
            print(indices)
            for i in indices:
                labelW = self.formLabelWidgetList[i]
                print(labelW)
                labelWType = self.formLabelWidgetTypeList[i]
                print(labelWType)
                labelWText = self.formLabelWidgetTextList[i]
                print(labelWText)
                fieldW = self.formWidgetList[i]
                print(fieldW)
                fieldWName = self.formWidgetNameList[i]
                print(fieldWName)

                labelW.hide()
                fieldW.hide()
                # should also probably delete the contents of these folders?

            self.labelApplyNameConvention.hide()
            self.buttonApplyNameConvention.hide()

def apply_name_convention(self):
    print("applying name convention")
    # have to do this after add_tooltip because these items are defined in that function - may want to change that at some point
    # get the name convention widget 
    self.nameConventionWidgetIdx = self.formWidgetNameList.index("descriptionFileNameConvention")
    self.nameConventionWidget = self.formWidgetList[self.nameConventionWidgetIdx] 
    print("my state: ", self.nameConventionWidget.state)
    self.nameConvention = self.nameConventionWidget.state

    try:
        nameConventionExplanatoryList = re.findall('{(.+?)}', self.nameConvention)
        print(nameConventionExplanatoryList)
    except AttributeError:
        # {} not found in the original string
        #nameConventionExplanatoryList = '' # apply your error handling
        print('you have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}')
        messageText = "<br>You have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}"
        errorFormat = '<span style="color:red;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        return

    if not nameConventionExplanatoryList:
        messageText = "<br>You have either not specified a naming convention or have not specified it correctly. please do not include the file extension (e.g. csv, docx, xlsx, etc.) in the naming convention, and specify as: e.g. subject_{subject ID number}_day_{date in YYYY/MM/DD}"
        errorFormat = '<span style="color:red;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        return

    # check if specified name convention includes directory structure (if so should provide full path, including file extension when specifying file name convention)
    s = rf"{self.nameConvention}"
    
    s1 = s.split('/')
    s2 = s.split('\\')
    print("forward slash split: ", s1, "back slash split: ", s2)

    if ((len(s1) > 1) or (len(s2) > 1)):
        keepFullPath = True
        s = os.path.normpath(s)
        messageText = "<br> Because the file name convention you entered contains either forward or back slashes, the file name convention you entered will be applied to the full path of each file in the set of multiple 'like' resources you added to the file drop box. When directory structure is used as part of the file naming convention, please specify the name convention including the full path and the file extension in the file name convention string you provide in the form."  
        self.userMessageBox.append(messageText)
        self.scrollScrollArea(topOrBottom = "top")
    else:
        messageText = "<br> Because the file name convention you entered does not contain either forward or back slashes, the file name convention you entered will be applied to the stem of the full path of each file in the set of multiple 'like' resources you added to the file drop box. When directory structure is NOT used as part of the file naming convention, please specify the name convention including just the filename excluding the file extension in the file name convention string you provide in the form."  
        self.userMessageBox.append(messageText)
        self.scrollScrollArea(topOrBottom = "top")
        keepFullPath = False

    if not keepFullPath:
        # get just file stems from full path, this also removes file extensions
        if self.items:
            self.fileStemList = [Path(p).stem for p in self.items]
        else:
            self.fileStemList = [Path(self.form.widget.state["path"]).stem]
    else:
        if self.items:
            self.fileStemList = [p for p in self.items]
        else:
            self.fileStemList = [self.form.widget.state["path"]]
        

    self.itemsDescriptionList = []
    self.itemsDescriptionMessagesOut = []

    self.itemsDescriptionList, itemsDescriptionMessagesOut = dsc_pkg_utils.get_multi_like_file_descriptions(self.nameConvention, self.fileStemList)

    if self.itemsDescriptionList:
        print("self.itemsDescriptionList: ",self.itemsDescriptionList)
        
        if all(self.itemsDescriptionList):
            self.form.widget.state = {
                "descriptionFile": self.itemsDescriptionList[0]
            } 

            applyConvention = "successful. Please see the Resource File Description field in the form below to see the file description assigned to the first file in your set of multiple 'like' resource files"
            textColor = "green"
        else: 
            applyConvention = "unsuccessful. Examine any errors the attempt produced (red text below), ensure that you are following the required conventions for specifying your naming convention, and come back and try again"
            textColor = "red"
        
        messageText = "<br>Your attempt to apply a name convention for your set of 'like' resource files was " + applyConvention + "."  
        textColorFormat = '<span style="color:' + textColor + ';">{}</span>'
        self.userMessageBox.append(textColorFormat.format(messageText))
        self.scrollScrollArea(topOrBottom = "top")

    if itemsDescriptionMessagesOut:
        print(itemsDescriptionMessagesOut)
        
        itemsDescriptionMessagesOut = [''.join(list(m)) for m in itemsDescriptionMessagesOut]
        print(itemsDescriptionMessagesOut)

        messageText = "<br> Your attempt to apply a name convention for your set of 'like' resource files produced the following errors: <br>" + '\n'.join(itemsDescriptionMessagesOut)  
        errorFormat = '<span style="color:red;">{}</span>'
        self.userMessageBox.append(errorFormat.format(messageText))
        self.scrollScrollArea(topOrBottom = "top")
