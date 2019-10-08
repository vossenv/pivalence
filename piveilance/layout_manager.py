import random

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from piveilance.util import *


class LayoutManager(QObject):
    setCamOptions = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self, widget, grid, camConfig, layoutConfig):
        super(LayoutManager, self).__init__()
        self.widget = widget
        self.grid = grid
        self.camConfig = camConfig
        self.layoutConfig = layoutConfig

        self.cols = 0
        self.list_refresh = layoutConfig.get_float('list_refresh', 10)

        path = self.camConfig.get('type', 'picam.PiCamGenerator').split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[-1])

        self.generator = gen_class(self.camConfig)
        self.camList = self.generator.getCameraList()
        self.redrawGrid()
        self.generator.start()

    @pyqtSlot(name="resize")
    def redrawGrid(self, camList=None, redrawCams=False):

        if camList and not areSetsEqual(camList, self.camList):
            redrawCams = True

        # Must keep as instance var in case called with none
        self.camList = camList or self.camList

        if not self.camList:
            return

        # see if there are new column count as calculated by compute
        maxCams = max(self.camConfig.get_int('max_allowed', 0), 0) or len(self.camList)
        rows, cols, dimensions, size = self.computeDims(maxCams)

        self.camConfig['size'] = size
        if not self.camConfig.get_bool('stretch'):
            self.grid.setContentsMargins(*dimensions)
        else:
            self.grid.setContentsMargins(0, 0, 0, 0)

        # Cameras must be repositioned
        if redrawCams or cols != self.cols:
            self.cols = cols
            self.clearLayout()
            self.buildFlowLayout(self.camList, self.camConfig, rows, cols, maxCams)
        self.setCamOptions.emit(self.camConfig)

    def clearLayout(self):
        # clear the layout
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def buildFlowLayout(self, camList, options, rows, cols, maxCams):

        camList = [self.generator.createCamera(n, options) for n in camList]
        fixedCams = sorted([c for c in camList if c.position], key=lambda x: x.position)
        freeCams = [c for c in camList if not c.position]
        random.shuffle(freeCams)
        fixedCams.extend(freeCams)

        positions = [(i, j) for i in range(rows) for j in range(cols)]
        for c in fixedCams[0:maxCams]:
            self.setCamOptions.connect(c.setOptions)
            p = positions.pop(0)
            self.grid.addWidget(c, *p)
            self.grid.addWidget(c.label, *p)

    def computeDims(self, camCount):

        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()

        cols, rows, sideLength = self.calculateCols(camCount, width, height)
        remainder_height = height - sideLength * rows

        if remainder_height < 0:
            sideLength = sideLength - abs(remainder_height / rows)

        rheight = max(height - sideLength * rows, 0) / 2
        vheight = max(width - sideLength * cols, 0) / 2
        dimensions = (vheight, rheight, vheight, rheight)
        return rows, cols, dimensions, sideLength

    def calculateCols(self, camCount, width, height):
        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        cols = rows = sideLength = camCount
        while (cols > 0):
            rows = math.ceil(camCount / cols)
            sideLength = width / cols
            if ((height - sideLength * rows) < sideLength
                    and (rows * cols - camCount) <= 1
                    or rows > cols):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols
        return cols, rows, sideLength



# start = time.time()
# if time.time() - start > self.list_refresh:
#     self.updateList.emit(self.getCameraList())
#     start = time.time()
