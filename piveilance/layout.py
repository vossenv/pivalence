import math

from piveilance.util import parse_collection


def parseLayout(style):
    return FixedLayout if style == 'fixed' else FlowLayout


class FlowLayout():

    @classmethod
    def calculate(cls, width, height, camCount):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams

        cols = rows = frameSize = camCount
        while cols > 0:
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
    def buildLayout(cls, camList, *args):

        cams = sorted(camList.values(), key=lambda x: x.order or len(camList) + 1)
        for i, c in enumerate(cams[0: WindowGeometry.numCams]):
            c.position = WindowGeometry.grid[i]
        return {c.name: c for c in cams}


class FixedLayout():
    config = None

    @classmethod
    def calculate(cls, width, height, *args):

        """
        # Rows and cols are predefined from the config

        """
        cols = cls.config.get_int('cols', 3)
        rows = cls.config.get_int('rows', 3)
        frameSize = width / cols
        return {'rows': rows, 'cols': cols, 'frameSize': frameSize}

    @classmethod
    def filterCameraPositions(cls, camList):
        positions = cls.config.get_dict('positions', {})
        return {k: v for k, v in positions.items() if k in camList}

    @classmethod
    def buildLayout2(cls, camList, getPlaceholder):

        #  pos = cls.convertCoordinates(cls.filterCameraPositions(camList))

        pos = cls.convertCoordinates(cls.config.get_dict('positions', {}))
        rev = {v: k for k, v in pos.items()}
        free = [c for c in WindowGeometry.grid if c not in pos.values()]
        free.extend([k for k in rev if rev[k] not in camList.keys()])

        for n, c in camList.items():
            p = pos.get(c.name)
            if p in WindowGeometry.grid:
                c.position = p
            elif free:
                p = free.pop(0)
                c.position = p if p in WindowGeometry.grid else None

        WindowGeometry.free = free

        for p in WindowGeometry.free:
            d = getPlaceholder(str(p))
            d.position = p
            camList[d.name] = d

        return camList

    @classmethod
    def buildLayout(cls, camList, getPlaceholder):

        if not camList:
            return {}

        newList = {}

        fixedCoords = cls.config.get_dict('positions', {})

        x =  {parse_collection(v): k for k, v in fixedCoords.items()}

        for c in WindowGeometry.grid:

            print()

        # remainingCoords = set(WindowGeometry.grid.copy())
        #
        # fixedCoords = cls.convertCoordinates(cls.config.get_dict('positions', {}))
        # for name, pos in fixedCoords.items():
        #     if pos not in WindowGeometry.grid:
        #         print("Warning: specified position {0} for {1} lies outside the grid".format(pos, name))
        #     if name in camList.keys():
        #         newList[name] = camList.pop(name)
        #         newList[name].position = pos
        #     else:
        #         newList[name] = getPlaceholder(name, pos)
        #     remainingCoords.remove(pos)

        # try:
        #     for name in camList.copy():
        #         newList[name] = camList.pop(name)
        #         newList[name].position = remainingCoords.pop()
        # except Exception as e:
        #     print("Remaining cameras could not be added - no space left in grid! " + str(camList.keys))
        # try:
        #     keys = camList.keys()
        #     for p in remainingCoords:
        #         cam = camList.pop()
        #         newList[str(p)] = getPlaceholder(str(p), p)
        # except Exception as e:
        #    print()

        return newList

    @classmethod
    def parseTuple(cls, strTuple):
        return

    @classmethod
    def convertCoordinates(cls, pos):

        """
        # Convert literal string coordinates to tuple

        """
        pos = pos.copy()
        cc = lambda c: (c[0] - 1, c[1] - 1)
        pos.update({k: Parser.parse_collection(v) for k, v in pos.items()})
        pos.update({k: cc(v) for k, v in pos.items()})
        return pos


class WindowGeometry():
    rows = None
    cols = None
    numCams = None
    height = None
    width = None
    frameSize = None
    margins = None
    grid = None
    free = None

    @classmethod
    def total(cls):
        return cls.cols * cls.rows

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
