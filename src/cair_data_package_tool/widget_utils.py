import os

def get_items_list2(self):
    
    if self.programmaticListUpdate2:
        self.programmaticListUpdate2 = False
        return

    lw = self.lstbox_view2
    
    oldLength = None
    if self.items2:
        oldLength = len(self.items2)
        oldItems = self.items2

    self.items2 = [lw.item(x).text() for x in range(lw.count())]
    print(self.items2)

    refactorItems = []
    for i in self.items2:
        print(i)
        if os.path.isdir(i):
            #self.programmaticListUpdate = True
            myFiles = [os.path.join(i,f) for f in os.listdir(i) if os.path.isfile(os.path.join(i,f))]
            print(myFiles)
            refactorItems.extend(myFiles)
        else:
            refactorItems.append(i)

    if self.items2 != refactorItems:
        self.programmaticListUpdate2 = True

        self.items2 = refactorItems
        self.lstbox_view2.clear()
        self.lstbox_view2.addItems(self.items2)

    newLength = len(self.items2)
    print(self.items2)  
    #print(type(self.items)) 
    print(len(self.items2))

    if self.items2:
        #updatePath = self.items2[0]
        updateAssocFileMultiDepend = self.items2
    else:
        #updatePath = ""
        updateAssocFileMultiDepend = []

    self.form.widget.state = {
        #"path": updatePath,
        "associatedFileDependsOn": updateAssocFileMultiDepend
    } 

    

    if oldLength:
        if ((oldLength > 0) and (newLength == 0)):
            print("hide")
            
            self.labelAddMultiDepend.hide()
            self.lstbox_view2.hide()
            
def toggle_add_file_box_visibility(self,property,button,label,add_files_box):

    if ((label.isHidden()) and (add_files_box.isHidden())):
        label.show()
        add_files_box.show()
    else:
        label.hide()
        add_files_box.hide()