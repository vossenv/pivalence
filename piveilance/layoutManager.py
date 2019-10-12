import random
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from piveilance.generator.dummy import DummyCamera, DummyGenerator
from piveilance.layout import FixedLayout, FlowLayout, WindowGeometry
from piveilance.util import *


class LayoutManager(QObject):
    setCamOptions = pyqtSignal(object)

    def __init__(self, widget, grid, camConfig, layoutConfig):
        super(LayoutManager, self).__init__()

        self.camIds = []
        self.start = time.time()
        self.widget = widget
        self.grid = grid
        self.camConfig = camConfig
        self.layoutConfig = layoutConfig
        self.refresh = layoutConfig.get_float('list_refresh', 10)
        self.maxCams = max(layoutConfig.get_int('max_allowed', 0), 0)

        path = self.camConfig.get('type', 'picam.PiCamGenerator').split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[-1])
        style = layoutConfig.get('style', 'flow')

        self.setLayout(FixedLayout if style == 'fixed' else FlowLayout)
        self.generator = gen_class(self.camConfig)
        self.generator.updateCameras.connect(self.recieveData)
        self.generator.start()

    @pyqtSlot(name="resize")
    def resizeEventHandler(self, triggerRedraw=False):
        self.arrange(triggerRedraw)

    @pyqtSlot(object, name="data")
    def recieveData(self, data, triggerRedraw=False):

        if (not self.camIds
                or time.time() - self.start > self.refresh):

            newCams = list(data.keys())
            if newCams and not compareIter(newCams, self.camIds):
                triggerRedraw = True

            self.camIds = newCams
            self.start = time.time()
            random.shuffle(self.camIds)

            if triggerRedraw:
                self.arrange(True)

    def arrange(self, triggerRedraw=False):
        preCols = WindowGeometry.cols
        self.camIds = self.camIds or []
        self.updateWindowGeometry()

        if triggerRedraw or WindowGeometry.cols != preCols:
            c = [self.generator.createCamera(n) for n in self.camIds]

            self.camObj = self.layout.buildLayout(c)
            self.clearLayout()
            for c in self.camObj:
                if c.position:
                    self.grid.addWidget(c, *c.position)
                    self.grid.addWidget(c.label, *c.position)
                    self.setCamOptions.connect(c.setOptions)

            for p in WindowGeometry.free:
                d = DummyCamera(str(p), self.camConfig)
                d.position = p
                self.grid.addWidget(d, *d.position)
                self.grid.addWidget(d.label, *d.position)
                self.setCamOptions.connect(d.setOptions)
                d.setImage()

        self.setCamOptions.emit(self.camConfig)


    def clearLayout(self):
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setLayout(self, layout):
        self.layout = layout
        self.layout.config = self.layoutConfig

    def setContentMargin(self, margins):
        m = margins if not self.camConfig.get_bool('stretch') else (0, 0, 0, 0)
        self.grid.setContentsMargins(*m)

    def updateWindowGeometry(self):
        n = self.maxCams if self.maxCams else len(self.camIds)
        w = self.widget.frameGeometry().width()
        h = self.widget.frameGeometry().height()
        WindowGeometry.update(width=w, height=h, numCams=n)
        WindowGeometry.update(**self.layout.calculate(w, h, n))
        WindowGeometry.calculateAllProperties()
        self.camConfig['size'] = WindowGeometry.frameSize
        self.setContentMargin(WindowGeometry.margins)
