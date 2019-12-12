import shutil
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

        self.globalConfig = ConfigLoader(configFile).loadGlobalConfig()
        self.initWindow(stylesheet, title, icon)
        self.layoutManager = LayoutManager(self.widget, self.grid, self.globalConfig)
        self.resized.connect(self.layoutManager.resizeEventHandler)
        if self.layoutManager.view.fullscreen:
            self.showFullScreen()
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

        # layoutMenu = cmenu.addMenu("Layout")
        # flowAct = layoutMenu.addAction("Flow")
        # fixedAct = layoutMenu.addAction("Fixed")

        maxMenu = cmenu.addMenu("Max Cams")
        entries = []
        if self.layoutManager.layout.style.adjustNumberAllowed:
            entries.extend([i for i in range(1, 1 + len(self.layoutManager.camIds))])
        entries.append("Unlimited")
        for e in entries:
            a = maxMenu.addAction(str(e))
            a.name = "limit"
            a.value = e

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            qApp.quit()
        elif action == fullScreenAct:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        #
        # elif action == flowAct and self.layoutManager.layout != layout.FlowLayoutStyle:
        #     self.layoutManager.setLayout(layout.FlowLayoutStyle)
        #     self.layoutManager.arrange(triggerRedraw=True)
        # elif action == fixedAct and self.layoutManager.layout != layout.FixedLayoutStyle:
        #     self.layoutManager.setLayout(layout.FixedLayoutStyle)
        #     self.layoutManager.arrange(triggerRedraw=True)
        #
        elif action == stretchAct:
            current = self.layoutManager.view.stretch
            self.layoutManager.setStretchMode(not current)
        elif action == labelAct:
            current = self.layoutManager.view.labels
            self.layoutManager.setLabelMode(not current)

        elif hasattr(action, 'name'):
            if action.name == "limit":
                v = action.value
                self.layoutManager.setMaxCams(0 if v == "Unlimited" else v)


if __name__ == '__main__':
    cli()
