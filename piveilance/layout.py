import math

from piveilance.cameras import PlaceholderCamera
from piveilance.util import parse_collection, parse_type


class LayoutStyle():

    def calculate(self, geometry):
        pass

    def buildLayout(self, camList, geometry, *args):
        pass


class Layout:

    def __init__(self,
                 id="unidentified",
                 styleName='flow',
                 cols=3,
                 rows=3,
                 maxAllowed=0,
                 cameras=None):
        self.id = parse_type(id, str)
        self.styleName = parse_type(styleName, str)
        self.cols = parse_type(cols, int)
        self.rows = parse_type(rows, int)
        self.maxAllowed = max(parse_type(maxAllowed, int), 0)
        self.cameras = parse_type(cameras, list)
        self.cameras = {v['id']: v for v in self.cameras}
        self.setLayout(self.styleName)

    def updateLayoutGeometry(self, geometry):
        return self.style.calculate(geometry)

    def setLayout(self, style):
        self.style = FixedLayoutStyle() if style == 'fixed' else FlowLayoutStyle()


class FlowLayoutStyle(LayoutStyle):
    adjustNumberAllowed = True

    def calculate(self, geometry):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams

        cols = rows = frameSize = numCams = geometry.numCams
        while cols > 0:
            rows = math.ceil(numCams / cols)
            frameSize = geometry.width / cols
            if ((geometry.height - frameSize * rows) < frameSize
                    and (rows * cols - numCams) <= 1
                    or rows > cols):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols

        geometry.rows = rows
        geometry.cols = cols
        geometry.frameSize = frameSize
        return geometry

    def buildLayout(self, camList, geometry, *args):

        cams = sorted(camList.values(), key=lambda x: x.order or len(camList) + 1)
        cams = cams[0: geometry.numCams]
        # cams = [PlaceholderCamera(id=c.id,name=c.name) for c in cams]
        for i, c in enumerate(cams):
            c.position = geometry.grid[i]
        return {c.id: c for c in cams}


class FixedLayoutStyle(LayoutStyle):
    adjustNumberAllowed = False

    def calculate(self, geometry):

        """
        # Rows and cols are predefined from the config

        """
        geometry.frameSize = geometry.width / geometry.cols
        return geometry

    # @classmethod
    # def filterCameraPositions(self, camList):
    #     positions = self.config.get_dict('positions', {})
    #     return {k: v for k, v in positions.items() if k in camList}

    # @classmethod
    # def buildLayout2(self, camList, geometry, getPlaceholder):
    #
    #     #  pos = self.convertCoordinates(self.filterCameraPositions(camList))
    #
    #     pos = self.convertCoordinates(self.config.get_dict('positions', {}))
    #     rev = {v: k for k, v in pos.items()}
    #     free = [c for c in geometry.grid if c not in pos.values()]
    #     free.extend([k for k in rev if rev[k] not in camList.keys()])
    #
    #     for n, c in camList.items():
    #         p = pos.get(c.name)
    #         if p in geometry.grid:
    #             c.position = p
    #         elif free:
    #             p = free.pop(0)
    #             c.position = p if p in geometry.grid else None
    #
    #     geometry.free = free
    #
    #     for p in geometry.free:
    #         d = getPlaceholder(str(p))
    #         d.position = p
    #         camList[d.name] = d
    #
    #     return camList

    def buildLayout(self, camList, geometry, getPlaceholder):

        if not camList:
            return {}

        newList = {}

        z = getPlaceholder('no')

        fixedCoords = self.config.get_dict('positions', {})

        x = {parse_collection(v): k for k, v in fixedCoords.items()}

        for c in geometry.grid:
            print()

        # remainingCoords = set(WindowGeometry.grid.copy())
        #
        # fixedCoords = self.convertCoordinates(self.config.get_dict('positions', {}))
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


class WindowGeometry():

    def __init__(self, rows=0, cols=0, numcams=0):

        self.rows = rows
        self.cols = cols
        self.numCams = numcams
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

    def update(self, **values):
        for k, v in values.items():
            if v is not None:
                setattr(self, k, v)


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
