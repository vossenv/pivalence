import shutil
import sys
from os.path import exists

import click
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from click_default_group import DefaultGroup

from piveilance import layout
from piveilance._version import __version__
from piveilance.config import *
from piveilance.layoutManager import LayoutManager
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
def start(ctx, **kwargs):
    app = QApplication(sys.argv)
    _ = PiWndow(ctx, **kwargs)
    sys.exit(app.exec_())


class PiWndow(QMainWindow):
    setCamOptions = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self, ctx, **cli_options):
        super().__init__()

        title = "Pi Veilance"
        stylesheet = get_resource("styles.qss")
        icon = get_resource("icon.ico")

        configFile = cli_options.get('config') or "default_config.yaml"
        if not exists(configFile):
            shutil.copy(get_resource(configFile), ".")

        self.config = Config.from_yaml(configFile)
        # self.camConfig = self.config.get_config('cameras')
        # self.viewConfig = self.config.get_config('view')
        # self.layoutConfig = self.config.get_config('layout')

        self.initWindow(stylesheet, title, icon)
        self.layoutManager = LayoutManager(self.widget, self.grid, self.config)
        self.resized.connect(self.layoutManager.resizeEventHandler)
        self.showFullScreen() if self.fullscreen else self.show()


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
        labelAct = cmenu.addAction("Toggle labels")

        layoutMenu = cmenu.addMenu("Layout")
        flowAct = layoutMenu.addAction("Flow")
        fixedAct = layoutMenu.addAction("Fixed")


        maxMenu = cmenu.addMenu("Max Cams")
        entries = []
        if self.layoutManager.layout == layout.FlowLayout:
            entries.extend([i for i in range(1, 1 + len(self.layoutManager.camIds))])
        entries.append("Unlimited")
        for e in entries:
            a = maxMenu.addAction(str(e))
            a.name = "limit"
            a.value = e

        cropMenu = cmenu.addMenu("Crop ratio")
        entries = [float(i / 10) for i in range(0, 11)]
        for e in entries:
            a = cropMenu.addAction(str(e))
            a.name = "crop"
            a.value = e

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            qApp.quit()
        elif action == fullScreenAct:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        elif action == flowAct and self.layoutManager.layout != layout.FlowLayout:
            self.layoutManager.setLayout(layout.FlowLayout)
            self.layoutManager.arrange(triggerRedraw=True)
        elif action == fixedAct and self.layoutManager.layout != layout.FixedLayout:
            self.layoutManager.setLayout(layout.FixedLayout)
            self.layoutManager.arrange(triggerRedraw=True)

        elif action == stretchAct:
            current = self.camConfig.get_bool('stretch', False)
            self.camConfig['stretch'] = not current
            self.layoutManager.arrange()
        elif action == labelAct:
            current = self.camConfig.get_bool('labels', True)
            self.camConfig['labels'] = not current
            self.layoutManager.arrange()

        elif hasattr(action, 'name'):
            if action.name == "crop":
                self.camConfig['crop_ratio'] = action.value
                self.layoutManager.arrange()
            elif action.name == "limit":
                v = action.value
                self.layoutManager.maxCams = 0 if v == "Unlimited" else v
                self.layoutManager.arrange(triggerRedraw=True)


if __name__ == '__main__':
    cli()
