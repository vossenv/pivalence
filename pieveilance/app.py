import sys
from os.path import exists

import math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pieveilance.camera import *
from pieveilance.config import *
from pieveilance.dummy import *
from pieveilance.resources import *


class PiWndow(QMainWindow):
    setCamSize = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self):
        super().__init__()

        cfg_file = "config.ini"
        resource_folder = resource_dir
        if getattr(sys, 'frozen', False):
            resource_folder = sys._MEIPASS

        cfg_file = cfg_file if exists(cfg_file) else get_resource(cfg_file)
        self.config = ConfigLoader.load(cfg_file)

        title = "Pi Veilance"
        stylesheet = join(resource_folder, "styles.qss")
        icon = join(resource_folder, "bodomlogo-small.jpg")

        self.setCamClass()
        self.beginDataFlows()
        self.initWindow(stylesheet, title, icon)
        self.showFullScreen() if self.fullscreen else self.show()

    def setCamClass(self):
        self.camClass = self.config.get('cameras', 'type', 'picam')
        if self.camClass == "picam":
            self.globalCam = Camera
            self.globalGen = PiCamGenerator

        elif self.camClass == "dummy":
            self.globalCam = DummyCamera
            self.globalGen = DummyGenerator
        else:
            raise TypeError("Unknown camera class: " + self.camClass)

    def initWindow(self, stylesheet, title, icon):
        view_config = self.config.get_config("view")
        self.fullscreen = view_config.get_bool('fullscreen', False)
        self.stretch = view_config.get_bool('stretch', False)
        self.widget = QWidget()
        self.resize(1024, 768)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Placeholder')
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.grid)
        self.setStyleSheet(open(stylesheet, "r").read())
        self.resized.connect(self.setCameraGrid)

    def resizeEvent(self, event):
        """
        Overridden method - resize the gride on window resize
        :param event:
        :return:
        """
        self.resized.emit()
        return super(PiWndow, self).resizeEvent(event)

    def contextMenuEvent(self, event):
        """
        Override to add menu quit option
        :param event:
        :return:
        """

        cmenu = QMenu(self)
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()

    def beginDataFlows(self):
        self.camlist = []
        self.cols = 3
        self.generator = self.globalGen(self)
        self.generator.updateList.connect(self.setCameraGrid)
        self.generator.start()

    @pyqtSlot(object, name="camgrid")
    @pyqtSlot(name="resize")
    def setCameraGrid(self, camlist=None):

        # Must keep as instance var in case called with none
        self.camlist = camlist or self.camlist

        if not self.camlist:
            return

        # see if there are new column count as calculated by compute
        new_cols, dimensions, camSize = self.computeGrid(len(self.camlist))

        if not self.stretch:
            self.grid.setContentsMargins(*dimensions)

        # Cameras must be repositioned
        if new_cols != self.cols:

            # calculate new rows and positions
            self.cols = new_cols
            rows = math.ceil(len(self.camlist) / new_cols)
            positions = [(i, j) for i in range(rows) for j in range(new_cols)]

            # clear the layout
            for i in reversed(range(self.grid.count())):
                self.grid.takeAt(i).widget().deleteLater()

            # add the cameras
            for i, c in enumerate(self.camlist):
                cam = self.globalCam(self.generator, camSize, c, self.stretch)
                self.setCamSize.connect(cam.setFrameSize)
                self.grid.addWidget(cam, *positions[i])
        self.setCamSize.emit(camSize)

    def computeGrid(self, camCount):

        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()
        cols, rows, sideLength = self.calculate_cols(camCount, width, height)
        remainder_height = height - sideLength * rows

        if remainder_height < 0:
            sideLength = sideLength - abs(remainder_height / rows)

        rheight = max(height - sideLength * rows, 0) / 2
        vheight = max(width - sideLength * cols, 0) / 2
        dimensions = (vheight, rheight, vheight, rheight)
        return cols, dimensions, sideLength

    def calculate_cols(self, camCount, width, height):
        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        cols = rows = sideLength = camCount
        while (cols > 0):
            rows = math.ceil(camCount / cols)
            sideLength = width / cols
            if (height - sideLength * rows) < sideLength:
                break
            cols -= 1
        cols = 1 if cols < 1 else cols
        return cols, rows, sideLength

    def deleteItems(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteItems(item.layout())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())
