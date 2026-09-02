import sys

from qtpy import QtWidgets
#from PyQt5 import QtWidgets

from layout_infotextbrowsewidget import InfoTextBrowserWindow

from layout_pkgcreatewidget import PkgCreateWindow
from layout_pkgauditwidget import PkgAuditWindow
from layout_pkgshareablewidget import PkgShareableWindow


class PkgTabsWindow(QtWidgets.QWidget):
    def __init__(self, workingDataPkgDirDisplay,trackersToAddToTool):
        super().__init__()
        self.setWindowTitle("Data Package")
        self.workingDataPkgDirDisplay = workingDataPkgDirDisplay
        self.trackersToAddToTool = trackersToAddToTool
        #self.resize(270, 110)
        
        # Create a top-level layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.infoText = "Start your data packaging and submission journey by creating a DSC Data Package directory!" + "<br><br>" + "By creating your DSC Data Package directory and following the recommendations and process flow for data packaging set forth in the <a href=\"https://norc-heal.github.io/heal-data-pkg-guide/\"> HEAL Data Packaging </a> guidance website, you'll memorialize what each data and non-data/supporting file in your study data package is/represents, how these files related to each other, and how to drill down into these component data and non-data/supporting files to recreate specific published results. This will facilitate continuity and passed-down knowledge within study groups, and discovery, sharing, and re-use of the data and knowledge produced by the study outside of the original study group." + "<br><br>" + "1. <b>Start your Data Package:</b> <u>The first time you use this tool</u>, navigate to the \"Create or Continue Data Package\" tab to start your data package by creating a new data package directory in your study folder. This will automatically set your new data package directory as your working data package directory." + "<br><br>" + "2. <b>Continue your Data Package:</b> <u>Anytime you return to this tool to work on your data package</u>, navigate to the \"Create or Continue Data Package\" tab to continue your data package work by selecting your existing data package directory folder. This will set your existing data package directory as your working data package directory folder."
        
        self.pkgCreateWindow = PkgCreateWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,trackersToAddToTool=self.trackersToAddToTool)
        self.pkgAuditWindow = PkgAuditWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay,trackersToAddToTool=self.trackersToAddToTool)
        self.pkgShareableWindow = PkgShareableWindow(workingDataPkgDirDisplay=self.workingDataPkgDirDisplay)
        #self.pkgPath = self.pkgCreateWindow.pkgPath

        # if self.pkgPath:
        #     self.infoText = self.pkgPath + self.infoText
        
        # Create the tab widget 
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(InfoTextBrowserWindow(infoText=self.infoText), "Info")
        tabs.addTab(self.pkgCreateWindow, "Create or Continue Data Package")
        #tabs.addTab(CSVPushToLoadWindow(), "View/Edit")
        tabs.addTab(self.pkgAuditWindow,"Update Data Package")
        tabs.addTab(self.pkgShareableWindow,"Prepare Data Package for Submission")
        
        layout.addWidget(tabs)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PkgTabsWindow()
    window.show()
    sys.exit(app.exec_())



