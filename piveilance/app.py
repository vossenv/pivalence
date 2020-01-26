import shutil
import sys
import socket

from os.path import exists

import click
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDesktopWidget, QGridLayout, qApp, QMenu
from click_default_group import DefaultGroup

from piveilance import messaging
from piveilance._version import __version__
from piveilance.config import ConfigLoader, Logging
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
@click.option('-d', '--debug',
              help="start in debug mode",
              is_flag=True)
def start(ctx, **kwargs):
    app = QApplication(sys.argv)
    _ = PiWndow(ctx, **kwargs)
    sys.exit(app.exec_())


class PiWndow(QMainWindow):
    setCamOptions = pyqtSignal(object)
    resized = pyqtSignal()

    def __init__(self, ctx, **cli_options):
        super().__init__()

        # Top level exception hook for logging
        sys.excepthook = messaging.ErrorHandler.excephook

        title = "Pi Veilance"
        stylesheet = get_resource("styles.qss")
        icon = get_image("icon.ico")

        log_level = "DEBUG" if cli_options['debug'] else "INFO"
        Logging.init_logger(get_resource("logger_config.yaml"), log_level)
        self.logger = Logging.get_logger()

        configFile = cli_options.get('file') or "config.yaml"
        configOverride = cli_options.get('config')
        if not exists(configFile):
            self.logger.info("No config found - generating default config...")
            shutil.copy(get_resource("default_config.yaml"), "config.yaml")

        self.logger.info("Initialized with options: " + str(cli_options))
        self.logger.info("Loading global configuration file: " + configFile)
        self.globalConfig = ConfigLoader(configFile).loadGlobalConfig()

        if configOverride:
            # Overrides the choice of launch configuration
            self.logger.debug("Overriding launch config id '{0}' with user specified: '{1}'"
                              .format(self.globalConfig['id'], configOverride))
            self.globalConfig['id'] = configOverride

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
        self.logger.debug("Initializing window")
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

    def updateStatusBar(self):
        text = "Version: {0} | Configuration: {1} | Layout: {2} | View: {3} | Address: {4}"
        text = text.format(
            __version__,
            self.layoutManager.globcalConfig.id,
            self.layoutManager.layout.id,
            self.layoutManager.view.id,
            self.getIp()
        )
        self.logger.debug("Updating status: " + text)
        self.statusBar().showMessage(text)

    def getIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        s.close()
        return str(ip)

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
            current = self.layoutManager.view.showLabels
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
