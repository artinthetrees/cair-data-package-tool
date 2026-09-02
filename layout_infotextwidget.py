
from qtpy import QtWidgets
#from PyQt5 import QtWidgets

class InfoTextWindow(QtWidgets.QMainWindow):

    def __init__(self, infoText):
        super().__init__()
        self.w = None  # No external window yet.
        self.infoText = infoText
        
        widget = QtWidgets.QWidget()
        
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

        #messageText = "You should create a data dictionary for every tabular or tabular-like data file you collect/share as part of your study. This allows you to memorialize what each variable in your dataset is/represents, what values it can take on, etc. This will facilitate continuity and passed-down knowledge within study groups, and sharing and re-use of the data outside of the original study group."
        messageText = self.infoText
        self.userMessageBox.setText(messageText)

    
    