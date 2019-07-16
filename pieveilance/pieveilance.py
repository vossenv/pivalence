import base64
import os
import random
import sys
import time
import requests
import json
import math

from collections import deque

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pathlib import Path


class PiWndow(QMainWindow):

    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        self.appTitle = "Pi Veilance"
        self.stylesheetPath = os.path.join(bundle_dir, "resources", "styles.qss")
        self.appIcon = os.path.join(bundle_dir, "resources", "bodomlogo-small.jpg")
        self.labels = []
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.setStyleSheet(open(self.stylesheetPath, "r").read())
        self.show()
        self.beginDataFlows()

    # self.setGridContent()

    def beginDataFlows(self):
        self.generator = Generator(self)
        self.setCameraGrid(self.generator.getCameraList())
        # self.generator.initializeContent.connect(self.setCameraGrid)
        self.generator.start()

    def initWindow(self):
        #self.resize(1024, 768)
        self.center()
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
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

    @pyqtSlot(list, name="camgrid")
    def setCameraGrid(self, camlist=None):

        cols = 2
        rows = math.ceil(len(camlist) / cols)
        positions = [(i, j) for i in range(rows) for j in range(cols)]

        for i, c in enumerate(camlist):
            cam = Camera(name=c)
            cam.setScaledContents(True)
            self.generator.updateCameras.connect(cam.setImage)
            self.grid.addWidget(cam, *positions[i])
            self.labels.append(cam)


class Camera(QLabel):
    def __init__(self, parent=None, name="default"):
        super(Camera, self).__init__(parent)
        self.name = name
        self.size = 800

    @pyqtSlot(object, name="camgrid")
    def setImage(self, camData):
        if self.name in camData:
            img = self.getImage(camData[self.name]['image'])

            qi = QImage()
            qi.loadFromData(img)
            z = qi.size()
            g = QRect(QPoint(0,0),z)
            g2 = QRect(g.center(), QSize(200, 200))
            copy = qi.copy(g2)

            qp = QPixmap(copy)
           # qp.loadFromData(img)
           # qp = qp.scaled(self.size, self.size)
           # qp = qp.scaledToHeight(self.size)
            self.setPixmap(qp)

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)


class Generator(QThread):
    updateCameras = pyqtSignal(object)
    initializeContent = pyqtSignal(list)

    def __init__(self, parent=None):
        super(Generator, self).__init__(parent)
        self.sleep = 0.1

    def getCameraList(self):
        cams = requests.get("http://192.168.50.139:9001/camlist").content
        return json.loads(cams)

    def update(self):
        img = requests.get("http://192.168.50.139:9001/cameras/next")
        data = json.loads(img.content)
        camData = {v['source']:v for v in data}
        self.updateCameras.emit(camData)

    def run(self):
        while True:
            self.update()
            time.sleep(self.sleep)




class Thread(QThread):
    changePixmap = pyqtSignal(QPixmap)
    changeLabel = pyqtSignal(str)

    def __init__(self, parent=None, *args, **kwargs):
        super(Thread, self).__init__(parent)

    # path = "E:\\Pics"
    # plist = [f for f in Path(path).glob('**/*.jpg')]
    #
    # def update(self):
    #     qp = QPixmap(str(random.choice(self.plist))).scaled(200, 200)
    #     return qp

    def update(self):
        img = requests.get("https://picsum.photos/500").content

        # img = requests.get("http://192.168.50.139:9001/cameras/front_bottom/next")
        # y =img.content

        # img = requests.get("http://192.168.50.139:9001/cameras/next")
        # x = json.loads(img.content)[1].get('image')
        # x1 = x.encode('utf-8')
        # y = base64.decodebytes(x1)

        qp = QPixmap()
        qp.loadFromData(img)
        return qp

    def run(self):
        self.sleep = 0.025  # random.randint(10, 50)*.07
        while True:
            self.changePixmap.emit(self.update())
            time.sleep(self.sleep)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())

    # def resizeEvent(self, event):
    #     for l in self.labels:
    #
    #         pixmap = l.pixmap()
    #         px = pixmap.scaled(self.width(), self.height())
    #         self.label.setPixmap(self.pixmap)
    #         self.label.resize(self.width(), self.height())
