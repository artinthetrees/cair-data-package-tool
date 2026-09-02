from qtpy import QtWidgets, QtGui 
#from PyQt5 import QtWidgets, QtGui  

class InfoTextBrowserWindow(QtWidgets.QMainWindow):

    def __init__(self, infoText):
        super().__init__()
        self.w = None  # No external window yet.
        self.infoText = infoText
        
        widget = QtWidgets.QWidget()
        
        self.userMessageBox = QtWidgets.QTextBrowser(parent=self)
        self.userMessageBox.setOpenExternalLinks(True)
        self.userMessageBox.setStyleSheet('font-size: 12px;')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        messageText = self.infoText
        self.userMessageBox.moveCursor(QtGui.QTextCursor.Start)
        self.userMessageBox.append(messageText)

    
    