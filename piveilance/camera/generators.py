import json
import time
import uuid

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from piveilance.camera.cameras import PiCamera, DummyCamera


class Generator(QThread):
    updateCameras = pyqtSignal(object)

    def __init__(self, config, camClass, parent=None):
        super(Generator, self).__init__(parent)
        self.camConfig = config
        self.camClass = camClass
        self.sleep = config.get_float('update_interval', 0.1)

    def update(self):
        pass

    def run(self):
        while True:
            self.update()
            time.sleep(self.sleep)

    def createCamera(self, name):
        cam = self.camClass(name, self.camConfig)
        self.updateCameras.connect(cam.setImage)
        return cam


class PiCamGenerator(Generator):

    def __init__(self, config, parent=None):
        super(PiCamGenerator, self).__init__(config, PiCamera, parent)
        self.data_url = config.get('data_url')

    def update(self):
        img = requests.get(self.data_url)
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)


class DummyGenerator(Generator):

    def __init__(self, config, parent=None):
        super(DummyGenerator, self).__init__(config, DummyCamera, parent)
        self.numCams = 7

    def update(self):
        # r = requests.get("https://picsum.photos/500").content
        camData = {"Cam " + str(x): uuid.uuid4() for x in range(0, self.numCams)}
        self.updateCameras.emit(camData)
