import sys
import os
# current_dir = os.path.dirname(__file__)
# config_dir = os.path.join(current_dir, '.')
# sys.path.append(config_dir)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUiType
from os import path
from iot.iot import *

from deploy.decision import *


FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),"door.ui"))

class door(QWidget,FORM_CLASS):
    def __init__(self,parent=None):
        super(door,self).__init__(parent)
        self.setupUi(self)
        self.status.setText(getStatusofDoor())
        self.setLayout(self.layout)
        if self.status.text()=="closed":
            self.open.setEnabled(True)
            self.close.setEnabled(False)
        else:
            self.open.setEnabled(False)
            self.close.setEnabled(True)
        self.open.clicked.connect(self.openD)
        self.close.clicked.connect(self.closeD)
        self.guest.clicked.connect(self.guest_open)
    
    def guest_open(self):
            self.cause.setText(f"user = admin")
            self.actual.setText("opening the door")
            self.actual.setText("")
            self.status.setText(openDoor())      
            if self.status.text()=="closed":
                self.open.setEnabled(True)
                self.close.setEnabled(False)
            elif self.status.text()=="opened":
                self.open.setEnabled(False)
                self.close.setEnabled(True)    

    def openD(self):
        verification=initializemodeles()
        self.actual.setText("taking image...")
        time.sleep(0.1)
        persons = process_faces()
        time.sleep(0.1)
        if len(persons)>0:
            self.actual.setText("recording audio 6 seconds...")
            allow,speaker = process_voice(verification)
            if allow:
                if speaker!="Unknown" and speaker in persons:
                   self.cause.setText(f"user = {speaker}")
                   self.actual.setText("opening the door")
                   self.actual.setText("")
                   self.status.setText(openDoor())
                else:
                    self.cause.setText(f"face and voice={speaker} not for the same person")
                    self.status.setText("closed")
            else:
                self.cause.setText("you are not a locator")
                self.status.setText("closed")
        else:
           self.cause.setText("you are not a locator")
           self.status.setText("closed")

        if self.status.text()=="closed":
            self.open.setEnabled(True)
            self.close.setEnabled(False)
        elif self.status.text()=="opened":
            self.open.setEnabled(False)
            self.close.setEnabled(True)

    def closeD(self):
        self.status.setText(closeDoor())
        if self.status.text()=="opened":
            self.open.setEnabled(False)
            self.close.setEnabled(True)
        elif self.status.text()=="closed":
            self.open.setEnabled(True)
            self.close.setEnabled(False)
    