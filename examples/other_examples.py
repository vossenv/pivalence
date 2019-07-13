


import sys
from PyQt5.QtWidgets import * #$QApplication, QWidget, QPushButton, QDesktopWidget, QMainWindow
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import PyQt5.QtGui as QtGui


class PiWndow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.init_menus()
        self.add_labels()
        self.setStyleSheet(open("styles.qss", "r").read())


        self.show()

    def buttonlayout(self, widget):
        grid = QGridLayout()
        widget.setLayout(grid)


        positions = [(i, j) for i in range(3) for j in range(3)]

        for p in positions:
            q = QLabel("Snakes")
            grid.addWidget(q, *p)

    def add_labels(self):

        q = QWidget()

        self.buttonlayout(q)

        # okButton = QPushButton("OK")
        # cancelButton = QPushButton("Cancel")
        #
        # hbox = QHBoxLayout()
        # hbox.addStretch(1)
        # hbox.addWidget(okButton)
        # hbox.addWidget(cancelButton)
        #
        # vbox = QVBoxLayout()
        # vbox.addStretch(1)
        # vbox.addLayout(hbox)

        #q.setLayout(vbox)


        self.setCentralWidget(q)


    def init_menus(self):
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        fileMenu.addAction(exitAct)
        #
        # impMenu = QMenu('Import', self)
        # impAct = QAction('Import mail', self)
        # impMenu.addAction(impAct)
        # newAct = QAction('New', self)
        # fileMenu.addAction(newAct)
        # fileMenu.addMenu(impMenu)

        # self.toolbar = self.addToolBar('Exit')
        # self.toolbar.addAction(exitAct)

        # qbtn = QPushButton('Quit', self)
        # qbtn.clicked.connect(QApplication.instance().quit)
        # qbtn.resize(qbtn.sizeHint())
        # qbtn.move(150, 150)

        #self.statusBar().showMessage('Ready')
        self.resize(640,480)
        self.center()
        #self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Icon')
        self.setWindowIcon(QIcon('bodomlogo-small.jpg'))

        # textEdit = QTextEdit()
        # self.setCentralWidget(textEdit)

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        newAct = cmenu.addAction("New")
        opnAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == quitAct:
            qApp.quit()


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PiWndow()
    sys.exit(app.exec_())