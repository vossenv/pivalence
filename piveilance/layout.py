import math

from piveilance.util import parse_collection, parse_type


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
        self.style = parseLayout(self.styleName)
        self.cameras = {v['id']: v for v in self.cameras}

    def updateLayoutGeometry(self, geometry):
        return self.style.calculate(geometry)


# def layoutProperties(self, **kwargs):


def parseLayout(style):
    return FixedLayoutStyle if style == 'fixed' else FlowLayoutStyle


class FlowLayoutStyle():

    @classmethod
    def calculate(cls, geometry):

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

    @classmethod
    def buildLayout(cls, camList, geometry, *args):

        cams = sorted(camList.values(), key=lambda x: x.order or len(camList) + 1)
        cams = cams[0: geometry.numCams]
        for i, c in enumerate(cams):
            c.position = geometry.grid[i]
        return {c.id: c for c in cams}


class FixedLayoutStyle():

    @classmethod
    def calculate(cls, width, rows, cols, **kwargs):

        """
        # Rows and cols are predefined from the config

        """
        kwargs['frameSize'] = width / cols
        return kwargs

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

        z = getPlaceholder('no')

        fixedCoords = cls.config.get_dict('positions', {})

        x = {parse_collection(v): k for k, v in fixedCoords.items()}

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

    def __init__(self):

        self.rows = 0
        self.cols = 0
        self.numCams = 0
        self.height = 0
        self.width = 0
        self.frameSize = 0
        self.margins = (0,0,0,0)
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
