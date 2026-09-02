 
#from PyQt5 import QtWidgets
from qtpy import QtWidgets

import sys # base python, no pip install needed

from layout_csveditwidget import CSVEditWindow

class CSVPushToLoadWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.w = None  # No external window yet.
        
        widget = QtWidgets.QWidget()
        
        self.buttonEditCsv = QtWidgets.QPushButton(text="View/Edit CSV", parent=self)
        self.buttonEditCsv.clicked.connect(self.view_edit_csv)
        #self.setCentralWidget(self.buttonEditCsv)
        #self.buttonEditCsv.setFixedSize(100,60)

        # maybe switch Line edit to this: https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QPlainTextEdit.html#more
        #self.userMessageBox = QtWidgets.QLineEdit(parent=self)
        self.userMessageBox = QtWidgets.QTextEdit(parent=self)
        self.userMessageBox.setReadOnly(True)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.buttonEditCsv)
        layout.addWidget(self.userMessageBox)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    
    def view_edit_csv(self,checked):
        if self.w is None:
            self.w = CSVEditWindow('')
            self.w.show()

        else:
            self.w.close()  # Close window.
            self.w = None  # Discard reference.

if __name__ == "__main__":
    
    #app = QtWidgets.QApplication(sys.argv)

    #app.exec_()

    app = QtWidgets.QApplication(sys.argv)
    window = CSVPushToLoadWindow()
    window.show()
    sys.exit(app.exec_())