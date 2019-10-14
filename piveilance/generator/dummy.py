import random
import time
import uuid

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap, QImage

from piveilance.generator.camera import Camera
from piveilance.generator.generator import Generator
from piveilance.util import ImageManip


class DummyGenerator(Generator):

    def __init__(self, config, parent=None):
        super(DummyGenerator, self).__init__(config, DummyCamera, parent)
        self.numCams = 7

    def update(self):
        # r = requests.get("https://picsum.photos/500").content
        camData = {"Cam " + str(x): uuid.uuid4() for x in range(0, self.numCams)}
        self.updateCameras.emit(camData)


class DummyCamera(Camera):
    def __init__(self, name="default", options=None, parent=None):
        super(DummyCamera, self).__init__(name, options, parent)

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):

        if not self.pixmap:
            img = QImage()
            img.load("resources/ent.jpg")
            if self.crop_ratio != 0:
                crop = max((img.width() - img.height()) * self.crop_ratio, 0)
                img = ImageManip.crop_direction(img, crop, self.direction)

            time.sleep(0.005 * random.randint(0, 1))
            self.pixmap = QPixmap().fromImage(img)
            self.setFrameSize()
