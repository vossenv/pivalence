import base64
import json
import time

import requests
from PyQt5.QtCore import QThread, pyqtSlot, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy


class PiCamGenerator(QThread):
    updateList = pyqtSignal(object)
    updateCameras = pyqtSignal(object)

    def __init__(self, parent=None):
        super(PiCamGenerator, self).__init__(parent)
        self.sleep = .1

    def getCameraList(self):
        cams = requests.get("http://192.168.50.139:9001/camlist").content
        return json.loads(cams)

    def update(self):
        img = requests.get("http://192.168.50.139:9001/cameras/next")
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)

    def run(self):
        self.updateList.emit(self.getCameraList())
        while True:
            self.update()
            time.sleep(self.sleep)


class Camera(QLabel):
    def __init__(self, source=None, size=300, name="default", scaled=False, parent=None):
        super(Camera, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.px = None
        self.name = name
        self.size = size
        self.setScaledContents(scaled)
        source.updateCameras.connect(self.setImage)

    @pyqtSlot(object, name="size")
    def setFrameSize(self, size):
        if self.px:
            self.setPixmap(self.px.scaled(size, size))
            self.size = size

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        if self.name in camData:
            img = self.getImage(camData[self.name]['image'])
            self.px = QPixmap()
            self.px.loadFromData(img)
            self.setFrameSize(self.size)

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)
