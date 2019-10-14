import base64
import json
import random
import time

import requests
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from piveilance.generator.camera import Camera
from piveilance.generator.generator import Generator
from piveilance.util import ImageManip


class PiCamGenerator(Generator):

    def __init__(self, config, parent=None):
        super(PiCamGenerator, self).__init__(config, PiCamera, parent)
        self.data_url = config.get('data_url')

    def update(self):
        img = requests.get(self.data_url)
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)


class PiCamera(Camera):
    def __init__(self, name="default", options=None, parent=None):
        super(PiCamera, self).__init__(name, options, parent)

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
            self.pixmap = QPixmap().fromImage(img)
            self.setFrameSize()

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)
