

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUiType
from os import path
import sys
import os 
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import gui_app.config as cf
import config as cf
from addPan import *
from editPan import *
from home import *
import subprocess as cmd

FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),"configure.ui"))

   
def getname(lista):
    row = lista.currentRow()
    if row >=0:
        name = lista.currentItem().text()
        return name
    return None



class configure(QtWidgets.QWidget,FORM_CLASS):
    def __init__(self,parent=None):
        super(configure,self).__init__(parent)
        self.setupUi(self)
        self.setLayout(self.layout)
        self.users = self.getUsers(cf.dataset)
        self.lista.addItems(self.users)
        self.delete_2.clicked.connect(self.supprimer)
        self.edit.clicked.connect(lambda:self.switch_to_edit(getname(self.lista)))
        self.add_usr.clicked.connect(self.switch_to_add_user)

    def switch_to_train(self):
        parent = self.parent().parent()
        parent.switch_widget(home(), parent.home_button, [parent.configure_switch, parent.train_switch,parent.door])
    
    def switch_to_add_user(self):
        parent = self.parent().parent()
        parent.switch_widget(addPan(),parent.configure_switch,[parent.home_button, parent.train_switch,parent.door])
        
    
    def switch_to_edit(self,nam):
        if nam is not None:
            parent = self.parent().parent()
            parent.switch_widget(editPan(nam),parent.configure_switch,[parent.home_button, parent.train_switch,parent.door])
            

    def getUsers(self,chemin):
        return os.listdir(chemin)

    def supprimer(self):
        row = self.lista.currentRow()
        if row >=0:
            name = self.lista.currentItem().text()
            print(f"{cf.dataset}/{name}")
            process = cmd.Popen([f"rm -r {cf.dataset}/{name}"],stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
            self.lista.takeItem(row)
            
            

