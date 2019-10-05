import shutil
import sys
from os.path import exists

import click
import math
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from click_default_group import DefaultGroup

from piveilance import util
from piveilance._version import __version__
from piveilance.cameras.camera import *
from piveilance.cameras.dummy import *
from piveilance.config import *
from piveilance.resources import get_resource


@click.group(cls=DefaultGroup, default='start', default_if_no_args=True)
def cli():
    pass


@cli.command()
@click.pass_context
@click.option('-c', '--config',
              help="point to config ini by name",
              type=click.Path(exists=True),
              default=None, )
@click.option('-f', '--fullscreen',
              help="toggle fullscreen",
              is_flag=True,
              default=None)
@click.option('-s', '--stretch',
              help="toggle stretch",
              is_flag=True,
              default=None)
def start(ctx, **kwargs):
    app = QApplication(sys.argv)
    _ = PiWndow(ctx, **kwargs)
    sys.exit(app.exec_())


class PiWndow(QMainWindow):
    setCamSize = pyqtSignal(object)
    setCamOptions = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self, ctx, **cli_options):
        super().__init__()

        title = "Pi Veilance"
        stylesheet = get_resource("styles.qss")
        icon = get_resource("icon.ico")

        cliArgs, configFile = self.parseCLIArgs(cli_options)
        self.config = Config.from_yaml(configFile).merge(cliArgs)
        self.camConfig = self.config.get_config('cameras')
        self.viewConfig = self.config.get_config('view')

        self.setCamClass()
        self.beginDataFlows()
        self.initWindow(stylesheet, title, icon)
        self.showFullScreen() if self.fullscreen else self.show()

    def parseCLIArgs(self, cli_options):

        configFile = cli_options.get('config') or "config.yaml"
        if not exists(configFile):
            shutil.copy(get_resource(configFile), ".")

        cli = {}
        for o in cli_options:
            v = cli_options[o]
            if not v:
                continue
            elif v and o in ['fullscreen']:
                Config.merge_dict(cli, Config.make_dict(['view', o], v))
            elif v and o in ['stretch']:
                Config.merge_dict(cli, Config.make_dict(['cameras', o], v))

        return cli, configFile

    def setCamClass(self):
        self.camClass = self.camConfig.get('type', 'picam')
        if self.camClass == "picam":
            self.globalGen = PiCamGenerator
        elif self.camClass == "dummy":
            self.globalGen = DummyGenerator
        else:
            raise TypeError("Unknown camera class: " + self.camClass)

    def initWindow(self, stylesheet, title, icon):
        self.fullscreen = self.viewConfig.get_bool('fullscreen', False)
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

        cropMenu = cmenu.addMenu("Crop ratio")
        entries = [str(float(i / 10)) for i in range(0, 11)]

        for e in entries:
            a = cropMenu.addAction(e)
            a.name = "crop_" + e

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()
        elif action == fullScreenAct:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif action == stretchAct:
            current = self.camConfig.get_bool('stretch', False)
            self.camConfig['stretch'] = not current
            self.setCameraGrid()

        elif hasattr(action, 'name') and action.name.startswith("crop"):
            r = float(action.name.split("_")[1])
            self.camConfig['crop_ratio'] = r
            self.setCameraGrid()

    def beginDataFlows(self):
        self.camlist = []
        self.cols = 0
        self.max_cameras = self.camConfig.get_int('max_allowed', 0)
        self.generator = self.globalGen(self.camConfig)
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
        new_cols, dimensions, self.camConfig['size'] = \
            util.computeGrid(len(self.camlist), width, height)

        if not self.camConfig.get_bool('stretch'):
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
            for i, name in enumerate(self.camlist):
                cam = self.generator.createCamera(name, self.camConfig)
                self.setCamSize.connect(cam.setFrameSize)
                self.setCamOptions.connect(cam.setOptions)
                self.grid.addWidget(cam, *positions[i])
        self.setCamSize.emit(self.camConfig['size'])
        self.setCamOptions.emit(self.camConfig)


if __name__ == '__main__':
    cli()
