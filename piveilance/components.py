import base64
import json
import math
import random
import time

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import pyqtSlot, QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap, QImage, QMovie
from PyQt5.QtWidgets import QLabel, QSizePolicy

from piveilance.config import Config
from piveilance.util import ImageManip
from piveilance.util import parse_type


class Layout:

    def __init__(self,
                 id="unidentified",
                 type='flow',
                 cols=3,
                 rows=3,
                 maxAllowed=0,
                 cameras=None):
        self.id = parse_type(id, str)
        self.type = parse_type(type, str)
        self.cols = parse_type(cols, int)
        self.rows = parse_type(rows, int)
        self.maxAllowed = max(parse_type(maxAllowed, int), 0)
        self.geometry = WindowGeometry(self.rows, self.cols)
        self.cameraMap = {v['id']: v for v in parse_type(cameras, list)}

        for c in self.cameraMap.values():
            c['position'] = parse_type(c.get('position'), tuple)
            c['order'] = parse_type(c.get('order'), int)

    def calculate(self):
        pass

    def build(self, camMap):
        pass

    def updateGeometry(self, width, height, camIds):
        self.maxAllowed = self.maxAllowed or len(camIds)
        self.geometry.width = width
        self.geometry.height = height
        self.calculate()


class FlowLayout(Layout):

    def __init__(self, *args, **kwargs):
        super(FlowLayout, self).__init__(*args, **kwargs)
        self.adjustNumberAllowed = True

    def calculate(self):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        g = self.geometry
        cols = rows = frameSize = self.maxAllowed
        while cols > 0:
            rows = math.ceil(self.maxAllowed / cols)
            frameSize = g.width / cols
            if ((g.height - frameSize * rows) < frameSize
                    and (rows * cols - self.maxAllowed) <= 1
                    or (rows > cols and cols > 3)):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols

        g.rows = rows
        g.cols = cols
        g.frameSize = frameSize
        g.calculateAllProperties()

    def build(self, camMap):

        cams = camMap.values()

        for c in cams:
            if c.id in self.cameraMap:
                c.order = self.cameraMap[c.id].get('order')

        cams = sorted(cams, key=lambda x: x.order or len(cams) + 1)
        cams = cams[0: self.maxAllowed]

        for i, c in enumerate(cams):
            c.position = self.geometry.grid[i]
        return {c.id: c for c in cams}


class FixedLayout(Layout):

    def __init__(self, *args, **kwargs):
        super(FixedLayout, self).__init__(*args, **kwargs)
        self.adjustNumberAllowed = False

    def calculate(self):
        """
        # Rows and cols are predefined from the config

        """
        self.geometry.frameSize = self.geometry.width / self.geometry.cols
        self.geometry.calculateAllProperties()

    def build(self, camMap):

        positioned = {}
        freeCams = {c for c in camMap.values() if c.id not in self.cameraMap}
        camsByPosition = {c.get('position'): c for c in self.cameraMap.values()}

        for p, c in camsByPosition.items():
            if p not in self.geometry.grid:
                if c['id'] in camMap:
                    freeCams.add(camMap[c['id']])
                else:
                    freeCams.add(PlaceholderCamera(id=c['id']))

        for pos in self.geometry.grid:
            if pos in camsByPosition:
                camId = camsByPosition[pos]['id']
                cam = camMap.get(camId)
                if not cam:
                    cam = PlaceholderCamera(id=camId)
            else:
                if freeCams:
                    cam = freeCams.pop()
                    camId = cam.id
                else:
                    camId = "undefined-{}".format(pos)
                    cam = PlaceholderCamera(id=camId, name="Offline")
            cam.position = pos
            positioned[camId] = cam

            for i,c in positioned.items():
                if c.id in self.cameraMap and c.position in self.geometry.grid:
                    c.isFixed = True

        return positioned


class FlowFixedLayout(FixedLayout):

    def __init__(self, *args, **kwargs):
        super(FlowFixedLayout, self).__init__(*args, **kwargs)
        self.adjustNumberAllowed = False

    def updateGeometry(self, width, height, camIds):

        totalCams = len(set(camIds) | set(self.cameraMap.keys()))
        gridsize = self.cols * self.rows
        self.maxAllowed = max(totalCams, gridsize)
        self.geometry.width = width
        self.geometry.height = height

        if totalCams <= gridsize:
            self.geometry.rows = self.rows
            self.geometry.cols = self.cols
            self.style = FixedLayout
        else:
            self.style = FlowLayout
        self.calculate()

    def calculate(self, type=FlowLayout):
        l = self.style(maxAllowed=self.maxAllowed)
        l.geometry = self.geometry
        l.calculate()


class GlobalConfig():

    def __init__(self,
                 id="default",
                 layout="default",
                 generator="default",
                 view="default",
                 placeholder="offline.gif"):
        self.id = parse_type(id, str)
        self.layout = parse_type(layout, str)
        self.generator = parse_type(generator, str)
        self.view = parse_type(view, str)
        self.placeholder = parse_type(placeholder, str)


class View():

    def __init__(self,
                 id,
                 fullscreen,
                 stretch,
                 fontRatio,
                 showLabels,
                 showCoords,
                 showFixed,
                 labelColor):
        self.id = parse_type(id, str)
        self.fullscreen = parse_type(fullscreen, bool)
        self.stretch = parse_type(stretch, bool)
        self.fontRatio = parse_type(fontRatio, float)
        self.showLabels = parse_type(showLabels, bool)
        self.showCoords = parse_type(showCoords, bool)
        self.showFixed = parse_type(showFixed, bool)
        self.labelColor = parse_type(labelColor, str)

    def getCamGlobals(self):
        return {
            'stretch': self.stretch,
            'fontRatio': self.fontRatio,
            'showLabels': self.showLabels,
            'showCoords': self.showCoords,
            'showFixed': self.showFixed,
            'labelColor': self.labelColor,
        }


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
        self.ip = "unknown"
        self.movie = None
        self.isFixed = False

        self.cropRatio = options.get_float('cropRatio', 0)
        if self.cropRatio < 0 or self.cropRatio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        self.name = options.get('name', self.id)
        self.position = options.get('position', None)
        self.order = options.get('order', None)
        self.size = options.get_int('size', 50)
        self.showLabels = options.get_bool('showLabels', False)
        self.showCoords = options.get_bool('showCoords', True)
        self.showFixed = options.get_bool('showFixed', True)
        self.labelColor = options.get_string('labelColor', '#05FF00')
        self.fontRatio = options.get_float('fontRatio', 0.025)
        self.direction = options.get_string('direction', 'right')
        self.stretch = options.get_bool('stretch', False)
        self.setOptions({})

    @pyqtSlot(dict, name="updateCamOptions")
    def setOptions(self, options):
        # validate ?
        vars(self).update(options)
        self.setScaledContents(self.stretch)
        self.setFrameSize()
        self.setLabel()

    def setFrameSize(self):
        if self.pixmap:
            self.setPixmap(self.pixmap.scaled(self.size, self.size))

    def setLabel(self):
        # fit text if too big
        text = self.name if self.showLabels else ""
        pre = ""
        if self.showCoords:
            pre = str(self.position)
        if self.isFixed and self.showFixed:
            pre += "F"
        text = pre + " " + text
        if self.showLabels:
            address = self.ip.split(".")
            if len(address) == 1:
                label_ip =  self.ip[:5]
            else:
                label_ip = "." + address[-1]
            text += " " + label_ip

        self.label.setText(text)
        self.label.setFont(QFont("Arial", self.fontRatio * self.size))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setStyleSheet("color: {}; font-weight: bold".format(self.labelColor))

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        pass


class PiCamera(Camera):
    def __init__(self, **kwargs):
        super(PiCamera, self).__init__(**kwargs)

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        if self.id in camData:
            self.ip = camData[self.id].get("ip") or ""
            self.setLabel()
            data = self.getImage(camData[self.id]['image'])
            img = QImage()
            img.loadFromData(data)
            if self.cropRatio != 0:
                crop = max((img.width() - img.height()) * self.cropRatio, 0)
                img = ImageManip.crop_direction(img, crop, self.direction)

            time.sleep(0.005 * random.randint(0, 1))
            self.pixmap = QPixmap().fromImage(img)
            self.setFrameSize()

    def getImage(self, data):
        byte = data.encode('utf-8')
        return base64.decodebytes(byte)


class PlaceholderCamera(Camera):
    image = "resources/image/offline.gif"

    def __init__(self, **kwargs):
        super(PlaceholderCamera, self).__init__(**kwargs)
        self.setImage()

    def setFrameSize(self):
        if self.movie:
            self.movie.setScaledSize(QSize(self.size, self.size))

    def setImage(self, camData=None):
        self.movie = QMovie(self.image)
        self.setMovie(self.movie)
        self.setFrameSize()
        self.movie.start()


class WindowGeometry():

    def __init__(self, rows=0, cols=0):
        self.rows = rows
        self.cols = cols
        self.height = 0
        self.width = 0
        self.frameSize = 0
        self.margins = (0, 0, 0, 0)
        self.grid = []

    def total(self):
        return self.cols * self.rows

    def correctFrameSize(self):
        remainder_height = self.height - self.frameSize * self.rows
        if remainder_height < 0:
            self.frameSize = self.frameSize - abs(remainder_height / self.rows)

    def setMargins(self):
        rheight = max(self.height - self.frameSize * self.rows, 0) / 2
        vheight = max(self.width - self.frameSize * self.cols, 0) / 2
        self.margins = (vheight, rheight, vheight, rheight)

    def calculateAllProperties(self):
        self.grid = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        self.correctFrameSize()
        self.setMargins()


class Generator(QThread):
    updateCameras = pyqtSignal(object)

    def __init__(self, id=None, updateInterval=None, cameraRepo=None, parent=None, **kwargs):
        super(Generator, self).__init__(parent)
        self.id = parse_type(id, str)
        self.cameraRepo = parse_type(cameraRepo, dict)
        self.updateInterval = parse_type(updateInterval, float)

    def update(self):
        pass

    def run(self):
        while True:
            self.update()
            time.sleep(self.updateInterval)

    def createCamera(self, camId):
        # Fills in defaults for none fields
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

    def defaultCamera(self):
        pass


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

