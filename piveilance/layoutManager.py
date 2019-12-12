import random
import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

from piveilance.layout import WindowGeometry
from piveilance.repository import Repository
from piveilance.util import *


class LayoutManager(QObject):
    setCamOptions = pyqtSignal(object)

    def __init__(self, widget, grid, config):
        super(LayoutManager, self).__init__()

        self.camIds = []
        self.start = time.time()
        self.widget = widget
        self.grid = grid
        self.repository = Repository(config)
        self.setLayout(config['configuration']['layout'])
        self.setGenerator(config['configuration']['generator'])
        self.setView(config['configuration']['view'])
        self.geometry = WindowGeometry(
            self.layout.rows, self.layout.cols, self.layout.maxAllowed)

    @pyqtSlot(name="resize")
    def resizeEventHandler(self, triggerRedraw=False):
        self.arrange(triggerRedraw)

    @pyqtSlot(object, name="data")
    def recieveData(self, data, triggerRedraw=False):
        if (not self.camIds or time.time() - self.start > self.generator.listRefresh):
            newCams = list(data.keys())
            if newCams and not compareIter(newCams, self.camIds):
                triggerRedraw = True
            self.camIds = newCams
            self.start = time.time()
            random.shuffle(self.camIds)
            if triggerRedraw:
                self.arrange(True)

    def arrange(self, triggerRedraw=False):
        if not self.camIds:
            return

        preCols = self.geometry.cols
        self.updateWindowGeometry()

        if triggerRedraw or self.geometry.cols != preCols:
            c = {n: self.setCamLayoutFields(self.generator.createCamera(n)) for n in self.camIds}
            self.camObj = self.layout.style.buildLayout(c, self.geometry)
            self.clearLayout()

            for n, c in self.camObj.items():
                self.grid.addWidget(c, *c.position)
                self.grid.addWidget(c.label, *c.position)
                self.setCamOptions.connect(c.setOptions)

        camOpts = self.view.getCamGlobals()
        camOpts['size'] = self.geometry.frameSize
        self.setGlobalCamOptions(camOpts)

    def setCamLayoutFields(self, cam):
        l = self.layout.cameras.get(cam.id)
        if l:
            cam.order = l.get('order')
            cam.position = l.get('position')
        return cam

    def setMaxCams(self, max):
        self.layout.maxAllowed = max
        self.arrange(True)

    def setGlobalCamOptions(self, options):
        self.setCamOptions.emit(options)

    def setTargetCamOptions(self, id, options):
        try:
            self.camObj['id'].setOptions(options)
        except KeyError:
            raise ValueError("Camera " + id + " does not exist")

    def clearLayout(self):
        for i in reversed(range(self.grid.count())):
            self.grid.takeAt(i).widget().deleteLater()

    def setLayout(self, layoutId):
        self.layout = self.repository.getLayout(layoutId)

    # def setLayoutSyle(self, layoutStyle):
    #     self.layout.style = layoutStyle

    def setStretchMode(self, toggle):
        self.view.stretch = toggle
        self.arrange()

    def setLabelMode(self, toggle):
        self.view.labels = toggle
        self.arrange()

    def setView(self, viewId):
        self.view = self.repository.getView(viewId)

    def setGenerator(self, generatorId):
        self.generator = self.repository.getGenerator(generatorId)
        self.generator.updateCameras.connect(self.recieveData)
        self.generator.start()

    def setContentMargin(self, margins):
        m = margins if not self.view.stretch else (0, 0, 0, 0)
        self.grid.setContentsMargins(*m)

    def updateWindowGeometry(self):
        maxCams = self.layout.maxAllowed
        self.geometry.numCams = maxCams if maxCams else len(self.camIds)
        self.geometry.width = self.widget.frameGeometry().width()
        self.geometry.height = self.widget.frameGeometry().height()
        self.layout.updateLayoutGeometry(self.geometry)
        self.geometry.calculateAllProperties()
        self.setContentMargin(self.geometry.margins)
