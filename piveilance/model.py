import base64
import math
import random
import time

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
        self.cameras = {v['id']: v for v in parse_type(cameras, list)}
        self.geometry = WindowGeometry(self.rows, self.cols)

    def calculate(self):
        pass

    def build(self, camList, geometry, *args):
        pass

    def updateGeometry(self, width, height, camLimit):
        self.maxAllowed = self.maxAllowed or camLimit
        self.geometry.width = width
        self.geometry.height = height
        self.calculate()

    def setCamLayoutFields(self, camList):
        for c in camList.values():
            if c.id in self.cameras:
                c.order = self.cameras[c.id].get('order')
                c.position = self.cameras[c.id].get('position')


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
                    or (rows > cols and cols > 2)):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols

        g.rows = rows
        g.cols = cols
        g.frameSize = frameSize
        g.calculateAllProperties()

    def build(self, camList, *args):

        self.setCamLayoutFields(camList)
        cams = sorted(camList.values(), key=lambda x: x.order or len(camList) + 1)
        cams = cams[0: self.maxAllowed]
        # cams = [PlaceholderCamera(id=c.id,name=c.name) for c in cams]

        for i, c in enumerate(cams):
            c.position = self.geometry.grid[i]
        return {c.id: c for c in cams}


# class FixedLayoutStyle(LayoutStyle):
#     adjustNumberAllowed = False
#
#     def calculate(self, geometry):
#
#         """
#         # Rows and cols are predefined from the config
#
#         """
#         geometry.frameSize = geometry.width / geometry.cols
#         return geometry
#
#     # @classmethod
#     # def filterCameraPositions(self, camList):
#     #     positions = self.config.get_dict('positions', {})
#     #     return {k: v for k, v in positions.items() if k in camList}
#
#     # @classmethod
#     # def buildLayout2(self, camList, geometry, getPlaceholder):
#     #
#     #     #  pos = self.convertCoordinates(self.filterCameraPositions(camList))
#     #
#     #     pos = self.convertCoordinates(self.config.get_dict('positions', {}))
#     #     rev = {v: k for k, v in pos.items()}
#     #     free = [c for c in geometry.grid if c not in pos.values()]
#     #     free.extend([k for k in rev if rev[k] not in camList.keys()])
#     #
#     #     for n, c in camList.items():
#     #         p = pos.get(c.name)
#     #         if p in geometry.grid:
#     #             c.position = p
#     #         elif free:
#     #             p = free.pop(0)
#     #             c.position = p if p in geometry.grid else None
#     #
#     #     geometry.free = free
#     #
#     #     for p in geometry.free:
#     #         d = getPlaceholder(str(p))
#     #         d.position = p
#     #         camList[d.name] = d
#     #
#     #     return camList
#
#     def buildLayout(self, camList, geometry, ):
#
#         if not camList:
#             return {}
#
#         newList = {}
#
#         z = getPlaceholder('no')
#
#         fixedCoords = self.config.get_dict('positions', {})
#
#         x = {parse_collection(v): k for k, v in fixedCoords.items()}
#
#         for c in geometry.grid:
#             print()
#
#         # remainingCoords = set(WindowGeometry.grid.copy())
#         #
#         # fixedCoords = self.convertCoordinates(self.config.get_dict('positions', {}))
#         # for name, pos in fixedCoords.items():
#         #     if pos not in WindowGeometry.grid:
#         #         print("Warning: specified position {0} for {1} lies outside the grid".format(pos, name))
#         #     if name in camList.keys():
#         #         newList[name] = camList.pop(name)
#         #         newList[name].position = pos
#         #     else:
#         #         newList[name] = getPlaceholder(name, pos)
#         #     remainingCoords.remove(pos)
#
#         # try:
#         #     for name in camList.copy():
#         #         newList[name] = camList.pop(name)
#         #         newList[name].position = remainingCoords.pop()
#         # except Exception as e:
#         #     print("Remaining cameras could not be added - no space left in grid! " + str(camList.keys))
#         # try:
#         #     keys = camList.keys()
#         #     for p in remainingCoords:
#         #         cam = camList.pop()
#         #         newList[str(p)] = getPlaceholder(str(p), p)
#         # except Exception as e:
#         #    print()
#
#         return newList

# @classmethod
# def parseTuple(self, strTuple):
#     return
#
# @classmethod
# def convertCoordinates(self, pos):
#
#     """
#     # Convert literal string coordinates to tuple
#
#     """
#     pos = pos.copy()
#     cc = lambda c: (c[0] - 1, c[1] - 1)
#     pos.update({k: Parser.parse_collection(v) for k, v in pos.items()})
#     pos.update({k: cc(v) for k, v in pos.items()})
#     return pos


class View():

    def __init__(self,
                 id,
                 fullscreen,
                 stretch,
                 fontRatio,
                 labels):
        self.id = parse_type(id, str)
        self.fullscreen = parse_type(fullscreen, bool)
        self.stretch = parse_type(stretch, bool)
        self.font_ratio = parse_type(fontRatio, float)
        self.labels = parse_type(labels, bool)

    def getCamGlobals(self):
        return {
            'stretch': self.stretch,
            'font_ratio': self.font_ratio,
            'show_labels': self.labels
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
        self.movie = None

        self.crop_ratio = options.get_float('crop_ratio', 0)
        if self.crop_ratio < 0 or self.crop_ratio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        self.name = options.get('name', self.id)
        self.position = options.get('position', None)
        self.order = options.get('order', None)
        self.size = options.get_int('size', 50)
        self.show_labels = options.get_bool('show_labels', False)
        self.font_ratio = options.get_float('font_ratio', 0.025)
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
        self.label.setText(self.name if self.show_labels else "")
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


# class DummyCamera(Camera):
#     def __init__(self, id="default", options=None, parent=None):
#         super(DummyCamera, self).__init__(id, options, parent)
#
#     @pyqtSlot(object, name="setimage")
#     def setImage(self, camData=None):
#
#         if not self.pixmap:
#             img = QImage()
#             img.load("resources/ent.jpg")
#             if self.crop_ratio != 0:
#                 crop = max((img.width() - img.height()) * self.crop_ratio, 0)
#                 img = ImageManip.crop_direction(img, crop, self.direction)
#
#             time.sleep(0.005 * random.randint(0, 1))
#             self.pixmap = QPixmap().fromImage(img)
#             self.setFrameSize()


class PlaceholderCamera(Camera):

    def __init__(self, **kwargs):
        super(PlaceholderCamera, self).__init__(**kwargs)
        self.setImage()

    def setFrameSize(self):
        if self.movie:
            self.movie.setScaledSize(QSize(self.size, self.size))

    def setImage(self, camData=None):
        self.movie = QMovie("resources/noise.gif")
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
        self.free = []

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
