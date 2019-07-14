import sys, os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PiWndow(QMainWindow):

    def __init__(self):
        super().__init__()

        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
        else:
            # we are running in a normal Python environment
            bundle_dir = os.path.dirname(os.path.abspath(__file__))

        self.appTitle = "Pi Valence"
        self.stylesheetPath = os.path.join(bundle_dir,"resources", "styles.qss")
        self.appIcon = os.path.join(bundle_dir,"resources", "bodomlogo-small.jpg")
        self.initUI()

    def initUI(self):
        self.initWindow()
        self.setGridContent()
        self.setStyleSheet(open(self.stylesheetPath, "r").read())
        self.show()

    def setGridContent(self):
        positions = [(i, j) for i in range(3) for j in range(3)]
        for p in positions:
            q = Snake()
            self.grid.addWidget(q, *p)

    def initWindow(self):
        self.resize(640, 480)
        self.center()
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.grid)
        self.setWindowTitle(self.appTitle)
        self.setWindowIcon(QIcon(self.appIcon))
        self.setCentralWidget(self.widget)
        self.statusBar().showMessage('Placeholder')

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
        if action == quitAct:
            qApp.quit()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class Snake(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("I am a snake!!")
        self.setObjectName("snake")



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())
