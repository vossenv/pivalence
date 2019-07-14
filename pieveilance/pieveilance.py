import base64
import os
import random
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PiWndow(QMainWindow):

    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        self.appTitle = "Pi Valence"
        self.stylesheetPath = os.path.join(bundle_dir,"resources", "styles.qss")
        self.appIcon = os.path.join(bundle_dir,"resources", "bodomlogo-small.jpg")
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.setGridContent()
        self.setStyleSheet(open(self.stylesheetPath, "r").read())
        self.show()

    def setGridContent(self):
        positions = [(i, j) for i in range(3) for j in range(3)]
        for p in positions:
            label = QLabel()
            s = Thread(self)
            s.changeLabel.connect(label.setText)
            self.grid.addWidget(label, *p)
            s.start()

    def initWindow(self):
        self.resize(1024, 768)
        self.center()
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.grid)
        self.setWindowTitle(self.appTitle)
        self.setWindowIcon(QIcon(self.appIcon))
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Placeholder')

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Thread(QThread):
    changePixmap = pyqtSignal(QPixmap)
    changeLabel = pyqtSignal(str)


    def run(self):
        sleep = random.randint(1, 50) / 150
        while True:
            data = ""
            for i in range(0,5):
                r = str(random.randint(5e12,5e13))
                r = base64.b64encode(r.encode('ascii'))
                data += r.decode()+ "\n"
            self.changeLabel.emit(data + "\nSleep = " + str(sleep))
            time.sleep(sleep)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())
