#https://realpython.com/python-pyqt-layout/#:~:text=addTab()%20%2C%20then%20that%20icon,layout%20containing%20the%20required%20widgets.

import sys

from qtpy import QtWidgets

from layout_general_add_widget import AddWindow
from layout_csvviewpushtoloadwidget import CSVViewPushToLoadWindow
from layout_infotextwidget import InfoTextWindow

class TabsWindow(QtWidgets.QWidget):
    def __init__(self, workingDataPkgDirDisplay,trackerDict,trackersToAddToTool):
        super().__init__()

        # inherited vars
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.trackerDict = trackerDict
        self.trackersToAddToTool = trackersToAddToTool

        # pull out of trackerDict inherited var for immediate use
        self.trackerType = self.trackerDict["trackerType"]

        self.setWindowTitle(self.trackerDict["trackerTitle"])
                
        # Create a top-level layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Create the tab widget with two tabs
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(InfoTextWindow(self.trackerDict["infoText"]), "Info")
        tabs.addTab(AddWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,trackerDict=self.trackerDict,trackersToAddToTool=self.trackersToAddToTool), "Add " + self.trackerType.title())
        tabs.addTab(CSVViewPushToLoadWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,fileBaseName=self.trackerDict["trackerFileBaseName"],fileStartsWith=self.trackerDict["trackerFileNamePrefix"], fileTypeTitle=self.trackerDict["trackerTitle"],viewerMode="view"), "View Tracker")
                        
        layout.addWidget(tabs)

    


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TabsWindow()
    window.show()
    sys.exit(app.exec_())



