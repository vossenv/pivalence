import math

from piveilance.config import Parser


class FlowLayout():

    @classmethod
    def calculate(cls, width, height, camCount=None):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        cols = rows = frameSize = camCount
        while (cols > 0):
            rows = math.ceil(camCount / cols)
            frameSize = width / cols
            if ((height - frameSize * rows) < frameSize
                    and (rows * cols - camCount) <= 1
                    or rows > cols):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols

        return {'rows': rows, 'cols': cols, 'frameSize': frameSize}

    @classmethod
    def buildLayout(cls, camList):

        camList = sorted(camList, key=lambda x: x.order or len(camList) + 1)
        for i, c in enumerate(camList[0: WindowGeometry.numCams]):
            c.position = WindowGeometry.grid[i]
        return camList


class FixedLayout():
    config = None

    @classmethod
    def calculate(cls, width, height, *args):
        cols = cls.config.get_int('cols', 3)
        rows = cls.config.get_int('rows', 3)
        frameSize = min(width / cols, height / rows)
        return {'rows': rows, 'cols': cols, 'frameSize': frameSize}

    @classmethod
    def buildLayout(cls, camList):

        pos = cls.convertCoordinates(cls.config.get_dict('positions', {}))
        free = [c for c in WindowGeometry.grid if c not in pos.values()]

        for c in camList:
            p = pos.get(c.name)
            if p in WindowGeometry.grid:
                c.position = p
            elif free:
                c.position = free.pop(0)
        return camList

    @classmethod
    def convertCoordinates(cls, pos):
        pos = pos.copy()
        pos.update({k: Parser.parse_collection(v) for k, v in pos.items()})
        pos.update({k: cls.correctCoordinates(v) for k, v in pos.items()})
        return pos

    @classmethod
    def correctCoordinates(cls, coords):
        return (coords[0] - 1, coords[1] - 1)

class WindowGeometry():
    rows = None
    cols = None
    numCams = None
    height = None
    width = None
    frameSize = None
    margins = None
    grid = None

    @classmethod
    def correctFrameSize(cls):
        remainder_height = cls.height - cls.frameSize * cls.rows
        if remainder_height < 0:
            cls.frameSize = cls.frameSize - abs(remainder_height / cls.rows)

    @classmethod
    def setMargins(cls):
        rheight = max(cls.height - cls.frameSize * cls.rows, 0) / 2
        vheight = max(cls.width - cls.frameSize * cls.cols, 0) / 2
        cls.margins = (vheight, rheight, vheight, rheight)

    @classmethod
    def calculateAllProperties(cls):
        cls.grid = [(i, j) for i in range(cls.rows) for j in range(cls.cols)]
        cls.correctFrameSize()
        cls.setMargins()

    @classmethod
    def update(cls, **values):
        for k, v in values.items():
            if v is not None:
                setattr(cls, k, v)
