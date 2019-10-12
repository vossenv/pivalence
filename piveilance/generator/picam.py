import base64
import json
import random
import time
from copy import deepcopy

import requests
from PyQt5.QtCore import QThread, pyqtSlot, QSize, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy

from piveilance.config import Parser
from piveilance.util import ImageManip


class PiCamGenerator(QThread):
    updateCameras = pyqtSignal(object)

    def __init__(self, config, parent=None):
        super(PiCamGenerator, self).__init__(parent)
        self.camConfig = config
        self.data_url = config.get('data_url')
        self.sleep = config.get_float('update_interval', 0.1)

    def update(self):
        img = requests.get(self.data_url)
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)

    def run(self):
        while True:
            self.update()
            time.sleep(self.sleep)

    def createCamera(self, name):
        cam = Camera(name, self.camConfig)
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
        self.label = QLabel()
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

        self.position = self.options.get('position', None)
        self.order = self.options.get('order', None)
        self.size = self.options.get_int('size')
        self.showLabel = self.options.get_bool('labels', True)
        self.font_ratio = self.options.get_float('font_ratio', 0.4)
        self.direction = self.options.get_string('direction', 'right', decode=True)
        self.setScaledContents(self.options.get_bool('stretch'))
        self.setFrameSize()
        self.setLabel()

    def setFrameSize(self):
        if self.px:
            self.setPixmap(self.px.scaled(self.size, self.size))

    def setLabel(self):
        self.label.setText(self.name if self.showLabel else "")
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

            time.sleep(0.005 * random.randint(0, 1))
            self.px = QPixmap().fromImage(img)
            self.setFrameSize()

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)
