import sys
from os.path import join

import math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pieveilance.resources as resources
from pieveilance.camera import *
from pieveilance.dummy import *


class PiWndow(QMainWindow):
    setCamSize = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self):

        # noinspection PyArgumentList
        super().__init__()

        resource_dir = resources.resource_dir
        if getattr(sys, 'frozen', False):
            resource_dir = join(sys._MEIPASS, resources.__name__)

        title = "Pi Veilance"
        stylesheet = join(resource_dir, "styles.qss")
        icon = join(resource_dir, "bodomlogo-small.jpg")

        self.global_cam = DummyCamera
        self.global_gen = DummyGenerator

        self.global_cam = Camera
        self.global_gen = PiCamGenerator

        self.initWindow(stylesheet, title, icon)
        self.beginDataFlows()
        self.show()

    def initWindow(self, stylesheet, title, icon):

        # noinspection PyArgumentList
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
        self.generator = self.global_gen(self)
        self.generator.updateList.connect(self.setCameraGrid)
        self.generator.start()

    @pyqtSlot(object, name="camgrid")
    def setCameraGrid(self, camlist=None):

        # Must keep as instance var in case called with none
        self.camlist = camlist or self.camlist

        if not self.camlist:
            return

        # see if there are new column count as calculated by compute
        new_cols, dimensions, camSize = self.computeGrid(len(self.camlist))
        self.grid.setContentsMargins(*dimensions)

        # Cameras must be repositioned
        if new_cols == self.cols:
            self.setCamSize.emit(camSize)

        else:
            # clear the layout
            for i in reversed(range(self.grid.count())):
                self.grid.takeAt(i).widget().deleteLater()

            # calculate new rows and positions
            self.cols = new_cols
            rows = math.ceil(len(self.camlist) / new_cols)
            positions = [(i, j) for i in range(rows) for j in range(new_cols)]

            # add the cameras
            for i, c in enumerate(self.camlist):
                cam = self.global_cam(self.generator, camSize, c)
                self.setCamSize.connect(cam.setFrameSize)
                self.grid.addWidget(cam, *positions[i])

    def computeGrid(self, camCount):

        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()

        h_margin = 0  # if width > 700 and height > 50 else  0
        v_margin = 0  # if height > 900 else 0
        # width -= h_margin * 2
        # height -= v_margin * 2

        cols, rows, sideLength = self.calculate_cols(camCount, width, height)

        remainder_height = height - sideLength * rows - 2 * h_margin

        if remainder_height < 0:
            sideLength = sideLength - abs(remainder_height / rows)

        rheight = max(height - sideLength * rows, 0) / 2 + v_margin
        vheight = max(width - sideLength * cols, 0) / 2 + h_margin

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())
