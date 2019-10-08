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
        self.camList = []
        self.cols = 0

        camClass = self.camConfig.get('type', 'picam.PiCamGenerator')
        path = camClass.split(".")
        module = __import__('piveilance.generator.' + path[0], fromlist=[''])
        gen_class = getattr(module, path[1])

        self.generator = gen_class(self.camConfig)
        self.generator.updateList.connect(self.redrawGrid)
        self.generator.start()

    @pyqtSlot(object, name="redraw")
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
        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()
        newCols, newRows, dimensions, self.camConfig['size'] = \
            computeGrid(maxCams, width, height)

        if not self.camConfig.get_bool('stretch'):
            self.grid.setContentsMargins(*dimensions)
        else:
            self.grid.setContentsMargins(0, 0, 0, 0)

        # Cameras must be repositioned
        if redrawCams or newCols != self.cols:

            # clear the layout
            for i in reversed(range(self.grid.count())):
                self.grid.takeAt(i).widget().deleteLater()

            # add the cameras
            # calculate new rows and positions
            self.cols = newCols
            positions = [(i, j) for i in range(newRows) for j in range(newCols)]
            camObjList = self.buildLayout(self.camList, self.camConfig)
            for c in camObjList[0:maxCams]:
                self.setCamOptions.connect(c.setOptions)
                p = positions.pop(0)
                self.grid.addWidget(c, *p)
                self.grid.addWidget(c.label, *p)

        self.setCamOptions.emit(self.camConfig)

    def buildLayout(self, camList, options):

        camList = [self.generator.createCamera(n, options) for n in camList]
        fixedCams = sorted([c for c in camList if c.priority], key=lambda x: x.priority)
        freeCams = [c for c in camList if not c.priority]
        random.shuffle(freeCams)
        fixedCams.extend(freeCams)
        return fixedCams
