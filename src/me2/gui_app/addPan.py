
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.uic import loadUiType
from os import path
import os
import sounddevice as sd
import cv2
import config as cf
import random
import subprocess as cmd
import soundfile as sf
import time


FORM_CLASS,_ = loadUiType(path.join(path.dirname(__file__),"addPan.ui"))

   


class addPan(QtWidgets.QWidget,FORM_CLASS):
    def __init__(self,parent=None):
        super(addPan,self).__init__(parent)
        self.setupUi(self)
        self.setLayout(self.layout)
        self.temp_imgs = {"taken":[],"uploaded":[]}
        self.temp_audios = {"taken":[],"uploaded":[]}
        self.upload_img.clicked.connect(self.chooseImage)
        self.take_img.clicked.connect(self.takeImage)
        self.upload_audio.clicked.connect(self.choseAudio)
        self.take_audio.clicked.connect(self.takeAudio)
        self.save.clicked.connect(self.savechanges)
        self.undo.clicked.connect(self.undochanges)
        self.del_img.clicked.connect(self.delete_image)
        self.del_aud.clicked.connect(self.delete_audio)
        self.todelete = []

    def chooseImage(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path and (".png" in file_path or ".jpeg" in file_path or ".jpg" in file_path):
            self.temp_imgs["uploaded"].append(file_path)
            self.images.addItem(file_path)
    
    def generate_image_name(self):
        upper_case_chars = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        lower_case_chars = [chr(i) for i in range(ord('a'), ord('z')+1)]
        lista = upper_case_chars + lower_case_chars
        name = ""
        for i in range(10):
            name+=random.choice(lista)
        while name in os.listdir(cf.cashcamera):
            name=""
            for i in range(10):
                name+=random.choice(lista)
        return name

    def generate_audio_name(self):
        upper_case_chars = [chr(i) for i in range(ord('A'), ord('Z')+1)]
        lower_case_chars = [chr(i) for i in range(ord('a'), ord('z')+1)]
        lista = upper_case_chars + lower_case_chars
        name = ""
        for i in range(10):
            name+=random.choice(lista)
        while name in os.listdir(cf.cashaudio):
            name=""
            for i in range(10):
                name+=random.choice(lista)
        return name


    def takeImage(self):
        generated = self.generate_image_name()
        cap = cv2.VideoCapture(cf.camurl)
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        chemin = f"{cf.cashcamera}/{generated}.jpg"
        cv2.imwrite(chemin, frame)
        cap.release()
        self.images.addItem(chemin)
        self.temp_imgs["taken"].append(chemin)
    
    def choseAudio(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path and ".wav" in file_path:
            self.temp_audios["uploaded"].append(file_path)
            self.audios.addItem(file_path)
        
    
    def takeAudio(self):
        generated = self.generate_audio_name()
        fs = 44100 
        duree = 3 
        enregistrement = sd.rec(int(duree * fs), samplerate=fs, channels=2)
        sd.wait()
        chemin =f"{cf.cashaudio}/{generated}.wav"
        sf.write(chemin, enregistrement, fs)
        self.temp_audios["taken"].append(chemin)
        self.audios.addItem(chemin)

        
    def savechanges(self):
        from configure import configure
        name = self.name.text()

        if self.name.text()!="" and not self.userexist(self.name.text()):
            for itm in self.todelete:
                cmd.Popen([f"rm {itm}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
                time.sleep(0.06)
            # Your commands
            proc1 = cmd.Popen([f"mkdir {cf.dataset}/{name}"], stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
            time.sleep(0.1)
            proc2 = cmd.Popen([f"mkdir {cf.dataset}/{name}{cf.faces}"], stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
            time.sleep(0.1)
            proc3 = cmd.Popen([f"mkdir {cf.dataset}/{name}{cf.voices}"], stdout=cmd.PIPE, stderr=cmd.PIPE, shell=True)
            time.sleep(0.1)
            for typ,imgs in self.temp_imgs.items():
               if typ=="taken":
                  for im in imgs:
                    if im not in self.todelete:
                        time.sleep(0.08)
                        cmd.Popen([f"cp {im} {cf.dataset}/{name}{cf.faces}/"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
               else:
                  for im in imgs:
                    if im not in self.todelete:
                        time.sleep(0.08)
                        nim = self.generate_image_name()
                        cmd.Popen([f"cp {im} {cf.dataset}/{name}{cf.faces}/{nim}.{im.split('.')[-1]}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
            for typ,auds in self.temp_audios.items():
               if typ=="taken":
                  for aud in auds:
                    if aud not in self.todelete:
                     time.sleep(0.08)
                     cmd.Popen([f"cp {aud} {cf.dataset}/{name+cf.voices}/"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
               else:
                  for aud in auds:
                    if aud not in self.todelete:
                      time.sleep(0.08)
                      naud = self.generate_image_name()
                      cmd.Popen([f"cp {aud} {cf.dataset}/{name+cf.voices}/{naud}.{aud.split('.')[-1]}"],stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)     
            cmd.Popen([f"rm {cf.cashcamera}/*"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
            cmd.Popen([f"rm {cf.cashaudio}/*"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
            self.temp_audios["taken"].clear()
            self.temp_audios['uploaded'].clear()
            self.temp_imgs["taken"].clear()
            self.temp_imgs["uploaded"].clear()
            parent = self.parent().parent()
            parent.switch_widget(configure(),parent.configure_switch,[parent.home_button, parent.train_switch,parent.door])
        else:
            self.infos.setText("user already exist!!")
        time.sleep(0.01)
    
    def undochanges(self):
           from configure import configure
           cmd.Popen([f"rm {cf.cashcamera}/*"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
           cmd.Popen([f"rm {cf.cashaudio}/*"], stdout=cmd.PIPE,stderr=cmd.PIPE,shell=True)
           parent = self.parent().parent()
           self.parent().parent().switch_widget(configure(),parent.configure_switch,[parent.home_button, parent.train_switch,parent.door])
           self.temp_audios["taken"].clear()
           self.temp_audios['uploaded'].clear()
           self.temp_imgs["taken"].clear()
           self.temp_imgs["uploaded"].clear()
           self.todelete.clear()
           time.sleep(0.01)
    
    def userexist(self,nam):
        if nam in os.listdir(cf.dataset):
            return True
        else:
            return False

    def delete_image(self):
        current_row = self.images.currentRow()
        if current_row>=0:
            im = self.images.currentItem().text()
            self.todelete.append(im)
            self.images.takeItem(current_row)

    def delete_audio(self):
        current_row = self.audios.currentRow()
        if current_row>=0:
            aud = self.audios.currentItem().text()
            self.todelete.append(aud)
            self.audios.takeItem(current_row)
