import shutil
import sys
from os.path import exists

import click
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from click_default_group import DefaultGroup

from piveilance._version import __version__
from piveilance.config import ConfigLoader
from piveilance.layoutManager import LayoutManager
from piveilance.resources import get_resource, get_image


@click.group(cls=DefaultGroup, default='start', default_if_no_args=True)
def cli():
    pass


@cli.command()
@click.pass_context
@click.option('-f', '--file',
              help="point to config ini by name",
              type=click.Path(exists=True),
              default=None, )
@click.option('-c', '--config',
              help="specify config id",
              type=str,
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
        icon = get_image("icon.ico")

        configFile = cli_options.get('file') or "config.yaml"
        useConfig = cli_options.get('config')

        if not exists(configFile):
            shutil.copy(get_resource("default_config.yaml"), "config.yaml")

        self.globalConfig = ConfigLoader(configFile).loadGlobalConfig()
        if useConfig:
            self.globalConfig['id'] = useConfig
        self.initWindow(stylesheet, title, icon)
        self.layoutManager = LayoutManager(self.widget, self.grid, self.globalConfig)
        self.resized.connect(self.layoutManager.resizeEventHandler)
        self.updateStatusBar()
        if self.layoutManager.view.fullscreen:
            self.showFullScreen()
            self.setCursor(Qt.BlankCursor)
        else:
            self.showNormal()

    def initWindow(self, stylesheet, title, icon):
        self.widget = QWidget()
        self.resize(1024, 768)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setCentralWidget(self.widget)
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(self.grid)
        self.setStyleSheet(open(stylesheet, "r").read())

    def updateStatusBar(self, message=""):
        text = "Version: {0} | Layout: {1} | View: {2}"
        self.statusBar().showMessage(text.format(
            __version__,
            self.layoutManager.layout.id,
            self.layoutManager.view.id
        ))

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
        coordAct = cmenu.addAction("Show/Hide coordinates")
        fixedAct = cmenu.addAction("Show/Hide fix state")
        labelAct = cmenu.addAction("Show/Hide labels")
        layoutMenu = cmenu.addMenu("Layout")

        if self.layoutManager.layout.adjustNumberAllowed:
            entries = []
            maxMenu = cmenu.addMenu("Max Cams")
            entries.extend([i for i in range(1, 1 + len(self.layoutManager.camIds))])
            entries.append("Unlimited")
            for e in entries:
                a = maxMenu.addAction(str(e))
                a.name = "limit"
                a.value = e

        entries = self.layoutManager.repository.getAllLayoutIds()
        for e in entries:
            a = layoutMenu.addAction(str(e))
            a.name = "layout"
            a.value = e

        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()
        elif action == fullScreenAct:
            if self.isFullScreen():
                self.showNormal()
                self.setCursor(Qt.ArrowCursor)
            else:
                self.showFullScreen()
                self.setCursor(Qt.BlankCursor)
        elif action == stretchAct:
            current = self.layoutManager.view.stretch
            self.layoutManager.setStretchMode(not current)
        elif action == labelAct:
            current = self.layoutManager.view.labels
            self.layoutManager.setLabelMode(not current)
        elif action == coordAct:
            current = self.layoutManager.view.showCoords
            self.layoutManager.setLabelCoordMode(not current)
        elif action == fixedAct:
            current = self.layoutManager.view.showFixed
            self.layoutManager.setLabelFixedMode(not current)
        elif hasattr(action, 'name'):
            if action.name == "limit":
                v = action.value
                self.layoutManager.setMaxCams(0 if v == "Unlimited" else v)
            elif action.name == "layout":
                self.layoutManager.setLayout(action.value)
                self.updateStatusBar()



if __name__ == '__main__':
    cli()
