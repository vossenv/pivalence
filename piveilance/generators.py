import json
import logging
import time

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from piveilance.cameras import PiCamera
from piveilance.util import parse_type


class Generator(QThread):
    updateCameras = pyqtSignal(object)

    def __init__(self, id=None, updateInterval=None, cameraRepo=None, parent=None, **kwargs):
        super(Generator, self).__init__(parent)
        self.id = parse_type(id, str)
        self.cameraRepo = parse_type(cameraRepo, dict)
        self.updateInterval = parse_type(updateInterval, float)
        self.logger = logging.getLogger()

    def update(self):
        pass

    def run(self):
        while True:
            self.update()
            time.sleep(self.updateInterval)

    def createCamera(self, camId):
        try:
            defaultOptions = self.cameraRepo['default']
        except KeyError:
            print("Missing default camera settings - using builtin")
            defaultOptions = self.defaultCamera()
        cameraConfig = self.cameraRepo.get(camId)
        if cameraConfig:
            for k in defaultOptions:
                if cameraConfig.get(k) is None:
                    cameraConfig[k] = defaultOptions[k]
        else:
            cameraConfig = defaultOptions
            cameraConfig['id'] = camId

        cam = self.camType(**cameraConfig)
        self.updateCameras.connect(cam.setImage)
        return cam


class PiCamGenerator(Generator):

    def __init__(self, **kwargs):
        super(PiCamGenerator, self).__init__(**kwargs)
        self.dataUrl = parse_type(kwargs.get('dataUrl'), str)
        self.listRefresh = parse_type(kwargs.get('listRefresh', 10), float)
        self.camType = PiCamera

    def defaultCamera(self):
        # fall back in case missing from config
        return {
            'id': 'default',
            'type': 'PiCam',
            'crop_ratio': 0.2,
            'direction': 'right'
        }

    def update(self):
        try:
            img = requests.get(self.dataUrl)
            data = json.loads(img.content)
            camData = {v['source']: v for v in data}
            self.updateCameras.emit(camData)
        except Exception as e:
            print(str(e))  # need to handle

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
