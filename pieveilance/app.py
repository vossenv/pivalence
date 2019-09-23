import sys
from os.path import join

import math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import pieveilance.resources as resources
from pieveilance.generator import *


class PiWndow(QMainWindow):
    setCamSize = pyqtSignal(object)

    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()

        resource_dir = resources.resource_dir
        if getattr(sys, 'frozen', False):
            resource_dir = join(sys._MEIPASS, resources.__name__)

        title = "Pi Veilance"
        stylesheet = join(resource_dir, "styles.qss")
        icon = join(resource_dir, "bodomlogo-small.jpg")

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
        self.move(qr.topLeft())
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Placeholder')
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.grid)
        self.setStyleSheet(open(stylesheet, "r").read())

    def resizeEvent(self, event):
        """
        Overridden method - resize the gride on window resize
        :param event:
        :return:
        """

        # self.computeGrid()
        self.setCameraGrid()
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
        # current number of cameras
        self.camCount = 0
        self.camlist = []
        self.cols = 3

        self.generator = DummyGenerator(self)
        self.generator.updateCameras.connect(self.setCameraGrid)
        self.generator.start()

    @pyqtSlot(object, name="camgrid")
    def setCameraGrid(self, camlist=None):

        # Must keep as instance var in case called with none
        self.camlist = camlist or self.camlist

        # see if there are new column count as calculated by compute
        new_cols = self.computeGrid(len(self.camlist))

        if new_cols:

            # clear the layout
            for i in reversed(range(self.grid.count())):
                self.grid.takeAt(i).widget().deleteLater()

            # calculate new rows and positions
            rows = math.ceil(len(self.camlist) / new_cols)
            positions = [(i, j) for i in range(rows) for j in range(new_cols)]

            # add the cameras
            for i, c in enumerate(self.camlist):
                cam = DummyCamera(name=c)
                self.setCamSize.connect(cam.setFrameSize)
                self.grid.addWidget(cam, *positions[i])

            # recheck correct layout
            self.computeGrid(len(self.camlist))

    def computeGrid(self, camCount):

        Ncam = camCount
        width = self.widget.frameGeometry().width()  # - self.h_margin*2
        height = self.widget.frameGeometry().height()  # - self.v_margin*2

        self.h_margin = 0  # if width > 700 and height > 50 else  0
        self.v_margin = 0  # 50 if height > 900 else 0

        width -= self.h_margin * 2
        height -= self.v_margin * 2
        cols = Ncam

        while True:

            rows = math.ceil(Ncam / cols)
            side_length = width / cols
            remainder = height - side_length * rows

            if remainder > side_length:
                cols = cols - 1
                if cols == 0:
                    cols = 1
                    break
            else:
                break

        current_cols = self.cols
        self.cols = cols
        self.sl = side_length

        t = height - self.sl * rows - 2 * self.h_margin
        n = rows
        if t < 0:
            self.sl = self.sl - abs(t / n)

        rheight = max(height - self.sl * rows, 0) / 2 + self.v_margin
        vheight = max(width - self.sl * cols, 0) / 2 + self.h_margin

        self.setCamSize.emit(self.sl)
        self.grid.setContentsMargins(vheight, rheight, vheight, rheight)

        if self.cols != current_cols:
            return self.cols


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())

