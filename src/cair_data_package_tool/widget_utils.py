import os
from pathlib import Path

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