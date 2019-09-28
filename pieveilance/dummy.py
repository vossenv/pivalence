from PyQt5.QtCore import QThread, pyqtSlot, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
import requests

class DummyGenerator(QThread):
    updateList= pyqtSignal(object)
    updateCameras = pyqtSignal(object)

    def __init__(self, parent=None):
        super(DummyGenerator, self).__init__(parent)
        self.num_cams = 7


    def getCameraList(self):
        return [x for x in range(0, self.num_cams)]

    def run(self):
        self.updateList.emit(self.getCameraList())

class DummyCamera(QLabel):

    def __init__(self,  source=None, size=300, name="default", scaled=False, parent=None):
        super(DummyCamera, self).__init__(parent)
        self.name = name
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.setImage()

    @pyqtSlot(object, name="size")
    def setFrameSize(self, size):
        pass
        # self.setPixmap(self.px.scaled(size, size))
        self.setPixmap(self.px.scaled(size, size))  # , Qt.KeepAspectRatio))

    def setImage(self):
        # r = requests.get("https://picsum.photos/500").content
        # qp = QPixmap()
        # qp.loadFromData(r)

        qp = QPixmap("resources/ent.jpg")
        self.px = qp
        qp = qp.scaled(300, 300)#, Qt.KeepAspectRatio)
        self.setPixmap(qp)

