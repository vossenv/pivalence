import time

from PyQt5.QtCore import QThread, pyqtSignal


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
