import base64
import json
import time
from copy import deepcopy

import requests
from PyQt5.QtCore import QThread, pyqtSlot, QSize, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy

from piveilance.config import Parser
from piveilance.util import ImageManip


class PiCamGenerator(QThread):
    updateList = pyqtSignal(object)
    updateCameras = pyqtSignal(object)

    def __init__(self, config, parent=None):
        super(PiCamGenerator, self).__init__(parent)
        self.list_url = config.get('list_url')
        self.data_url = config.get('data_url')
        self.sleep = config.get_float('update_interval', 0.1)
        self.list_refresh = config.get_float('list_refresh', 10)

    def getCameraList(self):
        cams = requests.get(self.list_url).content
        return json.loads(cams)

    def update(self):
        img = requests.get(self.data_url)
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)

    def run(self):
        start = time.time()
        self.updateList.emit(self.getCameraList())
        while True:
            self.update()
            time.sleep(self.sleep)
            if time.time() - start > self.list_refresh:
                self.updateList.emit(self.getCameraList())
                start = time.time()

    def createCamera(self, name, config):
        cam = Camera(name, config)
        self.updateCameras.connect(cam.setImage)
        return cam


class Camera(QLabel):
    def __init__(self,
                 name="default",
                 options=None,
                 parent=None):

        super(Camera, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.label = QLabel(name)
        self.px = None
        self.name = name
        self.setOptions(options)

    @pyqtSlot(object, name="reconfigure")
    def setOptions(self, options):
        self.options = deepcopy(options)
        for o, v in self.options.get_dict('overrides').items():
            if Parser.compare_str(o, self.name):
                self.options.update(v)
                break

        self.crop_ratio = self.options.get_float('crop_ratio')
        if self.crop_ratio < 0 or self.crop_ratio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        self.priority = self.options.get('priority', None)
        self.size = self.options.get_int('size')
        self.font_ratio = self.options.get_float('font_ratio', 0.4)
        self.direction = self.options.get_string('direction', 'right', decode=True)
        self.setScaledContents(self.options.get_bool('stretch'))
        self.setFrameSize()
        self.setLabel()

    def setFrameSize(self):
        if self.px:
            self.setPixmap(self.px.scaled(self.size, self.size))

    def setLabel(self):
        self.label.setFont(QFont("Arial", self.font_ratio * self.size))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setStyleSheet("color: #05FF00;"
                                 "font-weight: bold")

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        if self.name in camData:
            data = self.getImage(camData[self.name]['image'])
            img = QImage()
            img.loadFromData(data)
            if self.crop_ratio != 0:
                crop = max((img.width() - img.height()) * self.crop_ratio, 0)
                img = ImageManip.crop_direction(img, crop, self.direction)

            self.px = QPixmap().fromImage(img)
            self.setFrameSize()

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)
