import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit
from configure import *
from train import train
from PyQt5.QtCore import Qt
from home import *
from door import *


class window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Desktop Window")
        self.setGeometry(100, 100, 1000, 600)
 
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create layout for central widget
        self.central_layout = QVBoxLayout()
        self.central_widget.setLayout(self.central_layout)

        # Create top buttons
        self.button_layout = QHBoxLayout()
        self.central_layout.addLayout(self.button_layout)

        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(lambda: self.switch_widget(home(),self.home_button,[self.train_switch,self.configure_switch,self.door]))
        self.button_layout.addWidget(self.home_button)

        self.train_switch = QPushButton("training")
        self.train_switch.clicked.connect(lambda: self.switch_widget(train(),self.train_switch,[self.home_button,self.configure_switch,self.door]))
        self.button_layout.addWidget(self.train_switch)

        self.configure_switch = QPushButton("configure")
        self.configure_switch.clicked.connect(lambda: self.switch_widget(configure(),self.configure_switch,[self.home_button,self.train_switch,self.door]))
        self.button_layout.addWidget(self.configure_switch)

        self.door = QPushButton("door manage")
        self.door.clicked.connect(lambda: self.switch_widget(door(),self.door,[self.home_button,self.train_switch,self.configure_switch]))
        self.button_layout.addWidget(self.door)

        # Placeholder for current widget
        self.current_widget = home()
        self.central_layout.addWidget(self.current_widget)

    def switch_widget(self, widget,butt,otherbutt):
        # Remove current widget if exists
            if self.current_widget is not None:
                self.central_layout.removeWidget(self.current_widget)
                self.current_widget.deleteLater()
            # Add new widget to the layout
            self.current_widget = widget
            self.central_layout.addWidget(self.current_widget)
            butt.setEnabled(False)
            for b in otherbutt:
                    if b.isEnabled()==False:
                        b.setEnabled(True)
                    


class DeployWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLineEdit("Deploy Page Content Goes Here")
        self.label.setReadOnly(True)
        self.layout.addWidget(self.label)

        self.button = QPushButton("Deploy Button")
        self.layout.addWidget(self.button)

class TrainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLineEdit("Training Page Content Goes Here")
        self.label.setReadOnly(True)
        self.layout.addWidget(self.label)

        self.button = QPushButton("Train Button")
        self.layout.addWidget(self.button)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())
