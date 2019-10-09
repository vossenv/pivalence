import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QThread

from piveilance.layout import FixedLayout, FlowLayout
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
        self.style = layoutConfig.get('style', 'flow')
        self.list_refresh = layoutConfig.get_float('list_refresh', 10)
        self.maxCams = max(layoutConfig.get_int('max_allowed', 0), 0)

        path = self.camConfig.get('type', 'picam.PiCamGenerator').split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[-1])

        self.generator = gen_class(self.camConfig)

        if self.style == 'fixed':
            # self.layout = FixedLayout(self.grid, self.generator.createCamera, self.layoutConfig)
            self.layout = FixedLayout
        else:
            self.layout = FlowLayout
            # self.layout = FlowLayout(self.grid, self.generator.createCamera, self.layoutConfig)

        self.cols = 0
        self.camList = self.generator.getCameraList()
        self.redrawGrid()
        self.generator.start()
        self.layoutMonitor = LayoutMonitor(self)
        self.layoutMonitor.start()

    @pyqtSlot(name="resize")
    def redrawGrid(self, camList=None, redrawCams=False):

        if camList and not areSetsEqual(camList, self.camList):
            redrawCams = True

        # Must keep as instance var in case called with none
        self.camList = camList or self.camList

        if not self.camList:
            return

        numCams = self.maxCams if self.maxCams else len(self.camList)
        width, height = self.get_window_size()
        rows, cols, sideLength = self.layout.calculateProperties(width, height, numCams)
        dimensions, sideLength = self.computeDims(rows, cols, width, height, sideLength)
        self.setContentMargin(dimensions)
        self.camConfig['size'] = sideLength

        camObjList = [self.generator.createCamera(n, self.camConfig) for n in self.camList]

        # Cameras must be repositioned
        if redrawCams or cols != self.cols:
            self.clearLayout()
            cams = self.layout.buildLayout(camObjList[0:numCams], rows, cols)
            for c in cams:
                self.grid.addWidget(c, *c.position)
                self.grid.addWidget(c.label, *c.position)
                self.setCamOptions.connect(c.setOptions)

        self.cols = cols
        self.setCamOptions.emit(self.camConfig)

    def get_window_size(self):
        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()
        return width, height

    def clearLayout(self):
        # clear the layout
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setContentMargin(self, dimensions):
        if not self.camConfig.get_bool('stretch'):
            self.grid.setContentsMargins(*dimensions)
        else:
            self.grid.setContentsMargins(0, 0, 0, 0)

    def computeDims(self, rows, cols, width, height, sideLength):
        remainder_height = height - sideLength * rows
        if remainder_height < 0:
            sideLength = sideLength - abs(remainder_height / rows)
        rheight = max(height - sideLength * rows, 0) / 2
        vheight = max(width - sideLength * cols, 0) / 2
        dimensions = (vheight, rheight, vheight, rheight)
        return dimensions, sideLength


class LayoutMonitor(QThread):

    def __init__(self, layoutManager, parent=None):
        super(LayoutMonitor, self).__init__(parent)
        self.lm = layoutManager

    def run(self):
        start = time.time()
        while True:
            if time.time() - start > self.lm.list_refresh:
                self.lm.camList = self.lm.generator.getCameraList()
                start = time.time()
            time.sleep(1)
