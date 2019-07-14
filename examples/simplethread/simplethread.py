

import sys
import time
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
import datetime

class Thread(QThread):
    changePixmap = pyqtSignal(QPixmap)
    changeLabel = pyqtSignal(str)

    def run(self):
        while True:
            now = datetime.datetime.now()
            sec = now.second
            self.changeLabel.emit(str(now))
            print(str(now))
            time.sleep(0.5)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 Video'
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(1800, 1200)
        # create a label
        # create a label
        label = QLabel(self)
        label.move(280, 120)
        label.resize(640, 480)
        label1 = QLabel(self)
        label1.move(580, 620)
        label1.resize(150, 50)
        self.th = Thread(self)
        self.th.changePixmap.connect(label.setPixmap)
        self.th.changeLabel.connect(label1.setText)
        self.show()
        self.th.start()



app = QApplication([])
window = App()
app.exec_()