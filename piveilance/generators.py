import json
import time
import uuid

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from piveilance.cameras import PiCamera, DummyCamera
from piveilance.util import parse_type

class Generator(QThread):
    updateCameras = pyqtSignal(object)

    def __init__(self, id=None, updateInterval=None, getCamera=None, parent=None, **kwargs):
        super(Generator, self).__init__(parent)
        self.id = id
        self.getCamera = getCamera
        self.updateInterval = updateInterval

    def update(self):
        pass

    def run(self):
        while True:
            self.update()
            time.sleep(self.updateInterval)

    def createCamera(self, name):
        cam = self.camClass(name, self.camConfig)
        self.updateCameras.connect(cam.setImage)
        return cam


class PiCamGenerator(Generator):

    def __init__(self, **kwargs):
        super(PiCamGenerator, self).__init__(**kwargs)
        self.dataUrl = parse_type(kwargs.get('dataUrl'), str)
        self.listRefresh = parse_type(kwargs.get('listRefresh', 10), float)

    def update(self):
        img = requests.get(self.dataUrl)
        data = json.loads(img.content)
        camData = {v['source']: v for v in data}
        self.updateCameras.emit(camData)


# class DummyGenerator(Generator):
#
#     def __init__(self, camConfig, parent=None):
#         super(DummyGenerator, self).__init__(camConfig, DummyCamera, parent)
#         self.numCams = 7
#
#     def update(self):
#         # r = requests.get("https://picsum.photos/500").content
#         camData = {"Cam " + str(x): uuid.uuid4() for x in range(0, self.numCams)}
#         self.updateCameras.emit(camData)
