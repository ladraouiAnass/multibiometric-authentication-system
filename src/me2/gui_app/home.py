import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType
from os import path

FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),"home.ui"))

class home(QtWidgets.QWidget,FORM_CLASS):
    def __init__(self,parent=None):
        super(home,self).__init__(parent)
        self.setupUi(self)
        self.setLayout(self.layout)
        self.setLayout(self.layout)