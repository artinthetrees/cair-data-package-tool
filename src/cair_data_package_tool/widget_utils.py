import os

def update_add_files_list(self,property):   
         
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
        print(i)
        if os.path.isdir(i):
            myFiles = [os.path.join(i,f) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
            print(myFiles)
            refactored_items_list.extend(myFiles)
        else:
            refactored_items_list.append(i)

    if updated_items_list != refactored_items_list:
        self.dynamic_customBulkAddFilePaths["property"]["add_files_items_programmatic_update"] = True

        self.dynamic_customBulkAddFilePaths["property"]["add_files_items"] = refactored_items_list
        self.dynamic_customBulkAddFilePaths["property"]["add_files_box"].clear()
        self.dynamic_customBulkAddFilePaths["property"]["add_files_box"].addItems(refactored_items_list)

    newLength = len(refactored_items_list)
    print(refactored_items_list)  
    print(len(refactored_items_list))

    if refactored_items_list:
        updateAssocFileMultiDepend = refactored_items_list
    else:
        updateAssocFileMultiDepend = []

    self.form.widget.state[property] = updateAssocFileMultiDepend
    # self.form.widget.state = {
    #     "associatedFileDependsOn": updateAssocFileMultiDepend
    # } 

    if oldLength:
        if ((oldLength > 0) and (newLength == 0)):
            print("hide")
            
            self.dynamic_customBulkAddFilePaths[property]["lbl"].hide()
            self.dynamic_customBulkAddFilePaths[property]["add_files_box"].hide()
            
def toggle_add_file_box_visibility(self,property,label,add_files_box):

    if ((label.isHidden()) and (add_files_box.isHidden())):
        label.show()
        add_files_box.show()
    else:
        label.hide()
        add_files_box.hide()