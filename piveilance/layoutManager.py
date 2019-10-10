import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

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
        self.generator.updateCameras.connect(self.recieveData)
        self.layout = FixedLayout if self.style == 'fixed' else FlowLayout
        self.camList = []
        self.geom = Geometry(cols=0)
        self.start_time = time.time()
        self.generator.start()


    @pyqtSlot(name="resize")
    def resizeEventHandler(self, triggerRedraw=False):
        self.arrange(triggerRedraw)

    @pyqtSlot(object, name="data")
    def recieveData(self, data, triggerRedraw=False):

        # if lists are not eqal
        # if time has elapsed
        # if camlist is empty

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

        if not self.camList:
            return

        g = self.getLayoutGeometry()
        self.camConfig['size'] = g.frameSize
        self.setContentMargin(g.margins)

        # Cameras must be repositioned
        if triggerRedraw or g.cols != self.geom.cols:
            camObjList = [self.generator.createCamera(n, self.camConfig) for n in self.camList]
            cams = self.layout.buildLayout(camObjList[0:g.numCams], g.rows, g.cols)
            self.clearLayout()
            for c in cams:
                self.grid.addWidget(c, *c.position)
                self.grid.addWidget(c.label, *c.position)
                self.setCamOptions.connect(c.setOptions)

        self.geom = g
        self.setCamOptions.emit(self.camConfig)

    def clearLayout(self):
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setContentMargin(self, margins):
        m = margins if not self.camConfig.get_bool('stretch') else (0, 0, 0, 0)
        self.grid.setContentsMargins(*m)

    def getLayoutGeometry(self):

        n = self.maxCams if self.maxCams else len(self.camList)
        w = self.widget.frameGeometry().width()
        h = self.widget.frameGeometry().height()
        g = Geometry(width=w, height=h, numCams=n)
        g.update(self.layout.calculate(w, h, n))
        g.calculateAllProperties()
        return g

class Geometry():

    def __init__(self,
                 rows=None,
                 cols=None,
                 numCams=None,
                 height=None,
                 width=None,
                 frameSize=None,
                 margins=None):

        self.rows = rows
        self.cols = cols
        self.numCams = numCams
        self.height = height
        self.width = width
        self.frameSize = frameSize
        self.margins = margins

    def correctFrameSize(self):
        remainder_height = self.height - self.frameSize * self.rows
        if remainder_height < 0:
            self.frameSize = self.frameSize - abs(remainder_height / self.rows)

    def setMargins(self):
        rheight = max(self.height - self.frameSize * self.rows, 0) / 2
        vheight = max(self.width - self.frameSize * self.cols, 0) / 2
        self.margins = (vheight, rheight, vheight, rheight)

    def calculateAllProperties(self):
        self.correctFrameSize()
        self.setMargins()

    def update(self, values):
        for k, v in values.items():
            if v is not None:
                self.__setattr__(k, v)
