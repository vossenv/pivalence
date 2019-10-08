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

        path = self.camConfig.get('type', 'picam.PiCamGenerator').split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[-1])

        self.generator = gen_class(self.camConfig)

        if self.style == 'fixed':
            self.layout = FixedLayout(self.grid, self.generator.createCamera, self.layoutConfig)
        else:
            self.layout = FlowLayout(self.grid, self.generator.createCamera, self.layoutConfig)

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

        maxCams = self.getMaxCams()
        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()
        rows, cols, sideLength = self.layout.calculateProperties(width, height, maxCams)
        self.setContentMargin(rows, cols, width, height, sideLength)
        self.camConfig['size'] = sideLength

        # Cameras must be repositioned
        if redrawCams or cols != self.cols:
            self.clearLayout()
            cams = self.layout.buildLayout(self.camList, self.camConfig, rows, cols, maxCams)
            for c in cams:
                self.setCamOptions.connect(c.setOptions)

        self.cols = cols
        self.setCamOptions.emit(self.camConfig)

    def getMaxCams(self):
        # return either the config setting or the number of cams
        return max(self.camConfig.get_int('max_allowed', 0), 0) or len(self.camList)

    def clearLayout(self):
        # clear the layout
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setContentMargin(self, rows, cols, width, height, sideLength):
        if not self.camConfig.get_bool('stretch'):
            dimensions = self.computeDims(rows, cols, width, height, sideLength)
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
        return dimensions


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
