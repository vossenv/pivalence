import base64
import json
import time

import requests
from copy import deepcopy
from PyQt5.QtCore import QThread, pyqtSlot, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QSizePolicy

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


class Camera(QLabel):
    def __init__(self,
                 config,
                 source=None,
                 size=300,
                 name="default",
                 scaled=False,
                 parent=None):

        super(Camera, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.setScaledContents(scaled)
        self.px = None
        self.name = name
        self.size = size
        self.options = deepcopy(config)
        #
        # overrides = self.camConfig.get('overrides')
        # if overrides:
        #     self.camConfig['overrides'] = {str(k): v for k, v in overrides.items()}

        overrides = self.options.get_dict('overrides')
        if self.name in overrides:
           self.options.update(overrides[self.name])

        crop_key = "alarm_ratio" if name in ["2048", "2049"] else "crop_ratio"
        self.crop_ratio = config.get_float(crop_key, 1)
        if self.crop_ratio < 0 or self.crop_ratio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        source.updateCameras.connect(self.setImage)

    @pyqtSlot(object, name="size")
    def setFrameSize(self, size):
        if self.px:
            self.setPixmap(self.px.scaled(size, size))
            self.size = size

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        if self.name in camData:
            data = self.getImage(camData[self.name]['image'])

            img = QImage()
            img.loadFromData(data)

            # Take from right - preserving text
            if img.width() > img.height():
                crop = (img.width() - img.height()) * self.crop_ratio
                img = ImageManip.crop(img, 0, 0, 0, crop)



            self.px = QPixmap().fromImage(img)
            self.setFrameSize(self.size)

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)
