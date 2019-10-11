import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from piveilance.layout import FixedLayout, FlowLayout
from piveilance.util import *


class LayoutManager(QObject):
    setCamOptions = pyqtSignal(object)

    def __init__(self, widget, grid, camConfig, layoutConfig):
        super(LayoutManager, self).__init__()

        self.camList = []
        self.start_time = time.time()
        self.g = WindowGeometry
        self.widget = widget
        self.grid = grid
        self.camConfig = camConfig
        self.list_refresh = layoutConfig.get_float('list_refresh', 10)
        self.maxCams = max(layoutConfig.get_int('max_allowed', 0), 0)

        path = self.camConfig.get('type', 'picam.PiCamGenerator').split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[-1])
        style = layoutConfig.get('style', 'flow')

        self.layout = FixedLayout if style == 'fixed' else FlowLayout
        self.generator = gen_class(self.camConfig)
        self.generator.updateCameras.connect(self.recieveData)
        self.generator.start()

    @pyqtSlot(name="resize")
    def resizeEventHandler(self, triggerRedraw=False):
        self.arrange(triggerRedraw)

    @pyqtSlot(object, name="data")
    def recieveData(self, data, triggerRedraw=False):

        camList = list(data.keys())

        if not camList:
            return
        elif not self.camList:
            triggerRedraw = True
        elif not areSetsEqual(camList, self.camList):
            triggerRedraw = True
        elif time.time() - self.start_time > self.list_refresh:
            triggerRedraw = True
            self.start_time = time.time()

        self.camList = camList

        if triggerRedraw:
            self.arrange(True)

    def arrange(self, triggerRedraw=False):
        startCols = self.g.cols
        if not self.camList:
            return

        self.updateWindowGeometry()

        if triggerRedraw or self.g.cols != startCols:

            self.clearLayout()
            cams = [self.generator.createCamera(n, self.camConfig)
                    for n in self.camList[0:self.g.numCams]]

            for c in self.layout.buildLayout(cams, self.g.rows, self.g.cols):
                self.grid.addWidget(c, *c.position)
                self.grid.addWidget(c.label, *c.position)
                self.setCamOptions.connect(c.setOptions)

        self.setCamOptions.emit(self.camConfig)

    def clearLayout(self):
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setContentMargin(self, margins):
        m = margins if not self.camConfig.get_bool('stretch') else (0, 0, 0, 0)
        self.grid.setContentsMargins(*m)

    def updateWindowGeometry(self):
        n = self.maxCams if self.maxCams else len(self.camList)
        w = self.widget.frameGeometry().width()
        h = self.widget.frameGeometry().height()
        WindowGeometry.update(width=w, height=h, numCams=n)
        WindowGeometry.update(**self.layout.calculate(w, h, n))
        WindowGeometry.calculateAllProperties()
        self.camConfig['size'] = self.g.frameSize
        self.setContentMargin(WindowGeometry.margins)

class WindowGeometry():
    rows = None
    cols = None
    numCams = None
    height = None
    width = None
    frameSize = None
    margins = None

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
        cls.correctFrameSize()
        cls.setMargins()

    @classmethod
    def update(cls, **values):
        for k, v in values.items():
            if v is not None:
                setattr(cls, k, v)
