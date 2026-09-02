import os # base python, no pip install needed
import sys # base python, no pip install needed
import subprocess
import shlex

from qtpy import QtGui, QtWidgets 
#from PyQt5 import QtGui, QtWidgets

import cair_data_package_tool.back_door_edit as back_door_edit

from layout_pkgtabswidget import PkgTabsWindow
from layout_general_tabs_widget import TabsWindow

# this will prevent windows from setting the app icon to python automatically based on .py suffix
try:
    from ctypes import windll # only exists on windows, base python, no pip install needed
    myappid = 'mycompany.myproduct.subproduct.version' # somewhat arbitrary string, can set this to the recommendation but not really necessary
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

basedir = os.path.dirname(__file__)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,trackersToAddToTool,packagedForAddToToolTitle):
        super().__init__()

        baseTitle =  " - Data Packaging & Metadata Interaction Tool - alpha - "
        
        # get latest git tag to add to title
        tagProcessOut = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], stdout=subprocess.PIPE)
        tagTextOut = tagProcessOut.stdout.decode().strip()
        tagTextLines = tagTextOut.split('\n')
        tagTextFinalOut = tagTextLines[0].strip()
        
        finalBaseTitle = packagedForAddToToolTitle + baseTitle + tagTextFinalOut
        self.setWindowTitle(finalBaseTitle)

        self.main_widget = QtWidgets.QWidget(self)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        
        # Create a top-level layout
        self.layout = QtWidgets.QVBoxLayout(self.main_widget)
        
        self.workingDataPkgDirDisplayDefaultText = "Set a working data package directory! <br><br> Navigate to the \"Data Package\" tab >> \"Create or Continue Data Package\" sub-tab to either: <br><br>1. <b>Create New Data Package</b>: Create a new Data Package Directory and set it as the working Data Package Directory, or <br>2. <b>Continue Existing Data Package</b>: Set an existing Data Package Directory as the working Data Package Directory."
        self.workingDataPkgDirLabel = QtWidgets.QLabel("Working Data Package Directory:", self)
        self.workingDataPkgDirDisplay = QtWidgets.QTextEdit(parent=self)
        self.workingDataPkgDirDisplay.setReadOnly(True)
        self.workingDataPkgDirDisplay.setText(self.workingDataPkgDirDisplayDefaultText)
        
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabPosition(QtWidgets.QTabWidget.West)
        self.tabs.setMovable(True)

        self.trackersToAddToTool = trackersToAddToTool

        self.tabs.addTab(PkgTabsWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,trackersToAddToTool=self.trackersToAddToTool), "Data Package")
        for i in self.trackersToAddToTool:
            self.tabs.addTab(TabsWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,trackerDict=i,trackersToAddToTool=self.trackersToAddToTool), i["trackerTitle"])        
        
        self.layout.addWidget(self.workingDataPkgDirLabel)
        self.layout.addWidget(self.workingDataPkgDirDisplay)
        self.layout.addWidget(self.tabs)

        self.showMaximized()
        self.workingDataPkgDirLabel.setMinimumSize(1,40)
        self.setMinimumSize(1,1)
    
    def closeEvent(self, event):
        checked_out_working_data_pkg_dir = self.workingDataPkgDirDisplay.toPlainText()
        if checked_out_working_data_pkg_dir == self.workingDataPkgDirDisplayDefaultText:
            print("no data package directory set - do not have to work on removing in-use file from currently set data package directory")
            return
        else: 
            if not os.path.isdir(checked_out_working_data_pkg_dir):
                print("no data package directory set - do not have to work on removing in-use file from currently set data package directory")
                return
            else:
                print("data package directory is set - working on removing in-use file from currently set data package directory")
                if os.path.exists(os.path.join(checked_out_working_data_pkg_dir,back_door_edit.metadataDirLockFileName)):
                    os.remove(os.path.join(checked_out_working_data_pkg_dir,back_door_edit.metadataDirLockFileName))
                    print("in-use file was removed from currently set data package directory to indidate that it is no longer in use")
                else:
                    print("something went wrong - a data package directory was set but no in-use file was found in the directory")

def main(trackersToAddToTool,packagedForAddToToolTitle):
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(basedir,'tree.ico')))
    app.setQuitOnLastWindowClosed(True) 
   
    w = MainWindow(trackersToAddToTool=trackersToAddToTool,packagedForAddToToolTitle=packagedForAddToToolTitle)
    w.show()
 
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(
        trackersToAddToTool=sys.argv[1],
        packagedForAddToToolTitle=sys.argv[2]
        )

    