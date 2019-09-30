import shutil
import sys
from os.path import exists

import click
import math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from piveilance import util
from piveilance._version import __version__
from piveilance.cameras.camera import *
from piveilance.cameras.dummy import *
from piveilance.config import *
from piveilance.resources import get_resource


@click.command()
@click.option('--debug',
              is_flag=True,
              default=None)
@click.option('-c', '--config',
              help="point to config ini by name",
              type=click.Path(exists=True),
              default=None)
@click.option('-f', '--fullscreen',
              help="toggle fullscreen",
              is_flag=True,
              default=None)
@click.option('-s', '--stretch',
              help="toggle stretch",
              is_flag=True,
              default=None)
def main(**kwargs):
    app = QApplication(sys.argv)
    ex = PiWndow(**kwargs)
    sys.exit(app.exec_())


class PiWndow(QMainWindow):
    setCamSize = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self, **options):
        super().__init__()

        title = "Pi Veilance"
        default_properties = "config.ini"
        stylesheet = get_resource("styles.qss")
        icon = get_resource("icon.ico")

        if options['config']:
            props = options['config']
        else:
            props = default_properties
            if not exists(props):
                shutil.copy(get_resource(props), ".")

        self.config = ConfigLoader.load(props)
        self.cam_config = self.config.get_config('cameras')
        self.options = options
        self.setCamClass()
        self.beginDataFlows()
        self.initWindow(stylesheet, title, icon)
        self.showFullScreen() if self.fullscreen else self.show()

    def setCamClass(self):
        self.camClass = self.cam_config.get('type', 'picam')
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
        self.fullscreen = (self.options['fullscreen']
                           or view_config.get_bool('fullscreen', False))
        self.stretch = (self.options['stretch']
                        or view_config.get_bool('stretch', False))
        self.widget = QWidget()
        self.resize(1024, 768)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Version: ' + __version__)
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
        fullScreenAct = cmenu.addAction("Toggle fullscreen")
        stretchAct = cmenu.addAction("Toggle stretch")

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()
        elif action == fullScreenAct:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif action == stretchAct:
            self.stretch = not self.stretch
            self.setCameraGrid(adjust=True)

    def beginDataFlows(self):
        self.camlist = []
        self.cols = 0
        self.max_cameras = self.cam_config.get_int('max_allowed', 0)
        self.generator = self.globalGen(self.cam_config)
        self.generator.updateList.connect(self.setCameraGrid)
        self.generator.start()

    @pyqtSlot(object, name="camgrid")
    @pyqtSlot(name="resize")
    def setCameraGrid(self, camlist=None, adjust=False):

        if camlist and not util.areSetsEqual(camlist, self.camlist):
            adjust = True

        # Must keep as instance var in case called with none
        self.camlist = camlist or self.camlist

        if not self.camlist:
            return

        if self.max_cameras > 0:
            self.camlist = self.camlist[0:self.max_cameras]

        # see if there are new column count as calculated by compute
        width = self.widget.frameGeometry().width()
        height = self.widget.frameGeometry().height()
        new_cols, dimensions, camSize = \
            util.computeGrid(len(self.camlist), width, height)

        if not self.stretch:
            self.grid.setContentsMargins(*dimensions)
        else:
            self.grid.setContentsMargins(0, 0, 0, 0)

        # Cameras must be repositioned
        if adjust or new_cols != self.cols:

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


if __name__ == '__main__':
    main()
