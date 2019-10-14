from PyQt5.QtCore import pyqtSlot, QSize
from PyQt5.QtGui import QMovie

from piveilance.generator.camera import Camera


class PlaceholderCamera(Camera):
    def __init__(self, name="default", options=None, parent=None):
        super(PlaceholderCamera, self).__init__(name, options, parent)
        self.setImage()

    def setFrameSize(self):
        if self.movie:
            self.movie.setScaledSize(QSize(self.size, self.size))

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        self.movie = QMovie("resources/noise.gif")
        self.setMovie(self.movie)
        self.setFrameSize()
        self.movie.start()
