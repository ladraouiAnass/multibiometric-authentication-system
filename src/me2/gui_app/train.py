import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUiType
from os import path
import subprocess
import os
current_dir = os.path.dirname(__file__)
config_dir = os.path.join(current_dir, '../')
sys.path.append(config_dir)
import config as cf

FORM_CLASS, _ = loadUiType(path.join(path.dirname(__file__), "train.ui"))

class Worker(QThread):
    update_output = pyqtSignal(str)
    i = 0

    def run(self):
        process = subprocess.Popen(["python3" ,f"{cf.train_modele}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            output = process.stdout.readline().decode().strip()
            print(output)
            if not output:
                break
            self.update_output.emit(output)
        

class train(QWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(train, self).__init__(parent)
        self.setupUi(self)
        self.setLayout(self.layout)
        self.train_2.clicked.connect(self.start_task)
        self.stop.clicked.connect(self.interrupt_task)
        self.clear.clicked.connect(self.clearterminal)
        self.worker = Worker()
        self.worker.update_output.connect(self.updateTask)

    def clearterminal(self):
        self.terminal.setPlainText("")

    def updateTask(self, output):
        self.terminal.appendPlainText(output)

    def start_task(self):
        self.train_2.setEnabled(False)
        self.stop.setEnabled(True)
        self.clear.setEnabled(False)
        self.terminal.appendPlainText("training started.\nin progress...")
        self.worker.start()
        self.parent().parent().configure_switch.setEnabled(False)
        self.parent().parent().home_button.setEnabled(False)
        self.parent().parent().door.setEnabled(False)

    def interrupt_task(self):
        self.worker.terminate()
        self.task_finished()

    def task_finished(self):
        self.train_2.setEnabled(True)
        self.stop.setEnabled(False)
        self.clear.setEnabled(True)
        self.parent().parent().configure_switch.setEnabled(True)
        self.parent().parent().home_button.setEnabled(True)
        self.parent().parent().door.setEnabled(True)
        print("Task finished")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = train()
    window.show()
    sys.exit(app.exec_())
