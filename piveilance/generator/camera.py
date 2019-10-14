from copy import deepcopy

from PyQt5.QtCore import pyqtSlot, QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QSizePolicy

from piveilance.config import Parser


class Camera(QLabel):
    def __init__(self,
                 name="default",
                 options=None,
                 parent=None):
        super(Camera, self).__init__(parent)
        self.setStaticOptions(name, options)

    def setStaticOptions(self, name, options):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(50, 50))
        self.label = QLabel()
        self.pixmap = None
        self.name = name
        self.movie = None
        self.setOptions(options)

    @pyqtSlot(object, name="reconfigure")
    def setOptions(self, options):
        self.options = deepcopy(options)
        for o, v in self.options.get_dict('overrides').items():
            if Parser.compare_str(o, self.name):
                self.options.update(v)
                break

        self.crop_ratio = self.options.get_float('crop_ratio')
        if self.crop_ratio < 0 or self.crop_ratio > 1:
            raise ValueError("Crop cannot be negative or inverse (>1)")

        self.position = self.options.get('position', None)
        self.order = self.options.get('order', None)
        self.size = self.options.get_int('size')
        self.showLabel = self.options.get_bool('labels', True)
        self.font_ratio = self.options.get_float('font_ratio', 0.4)
        self.direction = self.options.get_string('direction', 'right', decode=True)
        self.setScaledContents(self.options.get_bool('stretch'))
        self.setFrameSize()
        self.setLabel()

    def setFrameSize(self):
        if self.pixmap:
            self.setPixmap(self.pixmap.scaled(self.size, self.size))

    def setLabel(self):
        self.label.setText(self.name if self.showLabel else "")
        self.label.setFont(QFont("Arial", self.font_ratio * self.size))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setStyleSheet("color: #05FF00;"
                                 "font-weight: bold")

    @pyqtSlot(object, name="setimage")
    def setImage(self, camData=None):
        pass
