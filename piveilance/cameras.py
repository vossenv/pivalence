import base64
import random
import time
from copy import deepcopy

from PyQt5.QtCore import pyqtSlot, QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtWidgets import QLabel, QSizePolicy

from piveilance.config import Config
from piveilance.util import ImageManip, compare_str


def parseCameraType(cameraType):
    if cameraType == 'PiCam':
        return PiCamera
    elif cameraType == 'Placeholder':
        return PlaceholderCamera
    elif cameraType == "DummyCam":
        return DummyCamera
    else:
        raise ValueError("No such camera type: " + cameraType)

class Camera(QLabel):
    def __init__(self, **kwargs):
        super(Camera, self).__init__(None)
        self.setStaticOptions(Config(kwargs))

    def setStaticOptions(self, options):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.label = QLabel()
        self.pixmap = None
        self.id = options['id']
        self.movie = None
        self.setOptions(options)

    @pyqtSlot(object, name="reconfigure")
    def setOptions(self, options):
        self.options = deepcopy(options)
        # for o, v in self.options.get_dict('overrides').items():
        #     if compare_str(o, self.id):
        #         self.options.update(v)
        #         break

        self.crop_ratio = self.options.get_float('crop_ratio')
        if self.crop_ratio < 0 or self.crop_ratio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        self.position = self.options.get('position', None)
        self.order = self.options.get('order', None)
        self.size = self.options.get_int('size', 50)
        self.showLabel = self.options.get_bool('labels', True)
        self.font_ratio = self.options.get_float('font_ratio', 0.4)
        self.direction = self.options.get_string('direction', 'right')
        self.setScaledContents(self.options.get_bool('stretch', False))
        self.setFrameSize()
        self.setLabel()

    def setFrameSize(self):
        if self.pixmap:
            self.setPixmap(self.pixmap.scaled(self.size, self.size))

    def setLabel(self):
        self.label.setText(self.id if self.showLabel else "")
        self.label.setFont(QFont("Arial", self.font_ratio * self.size))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setStyleSheet("color: #05FF00;"
                                 "font-weight: bold")

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        pass


class PiCamera(Camera):
    def __init__(self, **kwargs):
        super(PiCamera, self).__init__(**kwargs)

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        if self.id in camData:
            data = self.getImage(camData[self.id]['image'])
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


class DummyCamera(Camera):
    def __init__(self, id="default", options=None, parent=None):
        super(DummyCamera, self).__init__(id, options, parent)

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


class PlaceholderCamera(Camera):
    def __init__(self, id="default", position=None, options=None, parent=None):
        super(PlaceholderCamera, self).__init__(id, options, parent)
        self.position = position
        self.setImage()

    def setFrameSize(self):
        if self.movie:
            self.movie.setScaledSize(QSize(self.size, self.size))

    def setImage(self, camData=None):
        self.movie = QMovie("resources/noise.gif")
        self.setMovie(self.movie)
        self.setFrameSize()
        self.movie.start()
