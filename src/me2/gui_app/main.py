from PyQt5 import *
from PyQt5.QtWidgets import QApplication , QWidget,QLabel
import sys
from window import *

app = QApplication(sys.argv)
if __name__=='__main__':    
    win = window()
    win.show()
    sys.exit(app.exec_())
    