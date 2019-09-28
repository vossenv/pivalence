from PyQt5.QtCore import QThread, pyqtSlot, Qt, QSize, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
import requests

class DummyGenerator(QThread):

    updateCameras = pyqtSignal(object)

    def __init__(self, parent=None):
        super(DummyGenerator, self).__init__(parent)
        self.num_cams = 7


    def getCameraList(self):
        return [x for x in range(0, self.num_cams)]

    def run(self):
        self.updateCameras.emit(self.getCameraList())

class DummyCamera(QLabel):

    def __init__(self, parent=None, name="default"):
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
        qp = qp.scaled(300, 300, Qt.KeepAspectRatio)

        # qp = qp.scaledToHeight(200)
        self.setPixmap(qp)



    def computeGrid(self, camCount):

        if not camCount:
            return

        Ncam = camCount
        width = self.widget.frameGeometry().width()  # - self.h_margin*2
        height = self.widget.frameGeometry().height()  # - self.v_margin*2

        self.h_margin = 0  # if width > 700 and height > 50 else  0
        self.v_margin = 0  # 50 if height > 900 else 0

        width -= self.h_margin * 2
        height -= self.v_margin * 2
        cols = Ncam

        while True:

            rows = math.ceil(Ncam / cols)
            side_length = width / cols
            remainder = height - side_length * rows

            if remainder > side_length:
                cols = cols - 1
                if cols == 0:
                    cols = 1
                    break
            else:
                break

        current_cols = self.cols
        self.cols = cols
        self.sl = side_length

        t = height - self.sl * rows - 2 * self.h_margin
        n = rows
        if t < 0:
            self.sl = self.sl - abs(t / n)

        rheight = max(height - self.sl * rows, 0) / 2 + self.v_margin
        vheight = max(width - self.sl * cols, 0) / 2 + self.h_margin

        self.setCamSize.emit(self.sl)
        self.grid.setContentsMargins(vheight, rheight, vheight, rheight)

        if self.cols != current_cols:
            return self.cols

#
# class Camera(QLabel):
#     def __init__(self, parent=None, name="default"):
#         super(Camera, self).__init__(parent)
#         self.name = name
#         self.size = 300
#
#     @pyqtSlot(object, name="size")
#     def setFrameSize(self, size):
#         self.size = size
#         print()
#
#     @pyqtSlot(object, name="camgrid")
#     def setImage(self, camData):
#         if self.name in camData:
#             img = self.getImage(camData[self.name]['image'])
#
#             # qi = QImage()
#             # qi.loadFromData(img)
#             # z = qi.size()
#             # g = QRect(QPoint(0,0),z)
#             # g2 = QRect(g.center(), QSize(200, 200))
#             # copy = qi.copy(g2)
#             #
#             qp = QPixmap()
#             qp.loadFromData(img)
#             qp = qp.scaled(self.size, self.size)
#             qp = qp.scaledToHeight(self.size)
#             self.setPixmap(qp)#
#
#     def getImage(self, data):
#         byte = data.encode('utf-8')
#         return base64.decodebytes(byte)#
#
#
# class Generator(QThread):
#     updateCameras = pyqtSignal(object)
#     initializeContent = pyqtSignal(list)
#
#     def __init__(self, parent=None):
#         super(Generator, self).__init__(parent)
#         self.sleep = 0.1
#
#     def getCameraList(self):
#         cams = requests.get("http://192.168.50.139:9001/camlist").content
#         return json.loads(cams)
#
#     def update(self):
#         img = requests.get("http://192.168.50.139:9001/cameras/next")
#         data = json.loads(img.content)
#         camData = {v['source']: v for v in data}
#         self.updateCameras.emit(camData)
#
#     def run(self):
#         while True:
#             self.update()
#             time.sleep(self.sleep)






    # def resizeEvent(self, event):
    #     for l in self.labels:
    #
    #         pixmap = l.pixmap()
    #         px = pixmap.scaled(self.width(), self.height())
    #         self.label.setPixmap(self.pixmap)
    #         self.label.resize(self.width(), self.height())

    #
    # def mouseReleaseEvent(self, QMouseEvent):
    #     cursor = QCursor()
    #     print(cursor.pos())

    # self.grid.addWidget(Spacer(), 0, 0, rows, 1)
    # self.grid.addWidget(Spacer(), 0, cols+1, rows, 1)
    # self.grid.addWidget(Spacer(), rows+1,0,1,cols+2)
    # self.grid.addWidget(Spacer(), 0,0,1,cols+2)

# class Thread(QThread):
#     changePixmap = pyqtSignal(QPixmap)
#     changeLabel = pyqtSignal(str)
#
#     def __init__(self, parent=None, *args, **kwargs):
#         super(Thread, self).__init__(parent)
#
#     # path = "E:\\Pics"
#     # plist = [f for f in Path(path).glob('**/*.jpg')]
#     #
#     # def update(self):
#     #     qp = QPixmap(str(random.choice(self.plist))).scaled(200, 200)
#     #     return qp
#
#     def update(self):
#         img = requests.get("https://picsum.photos/500").content
#
#         # img = requests.get("http://192.168.50.139:9001/cameras/front_bottom/next")
#         # y =img.content
#
#         # img = requests.get("http://192.168.50.139:9001/cameras/next")
#         # x = json.loads(img.content)[1].get('image')
#         # x1 = x.encode('utf-8')
#         # y = base64.decodebytes(x1)
#
#         qp = QPixmap()
#         qp.loadFromData(img)
#         return qp
#
#     def run(self):
#         self.sleep = 0.025  # random.randint(10, 50)*.07
#         while True:
#             self.changePixmap.emit(self.update())
#             time.sleep(self.sleep)

# cam.setScaledContents(True)
# self.generator.updateCameras.connect(cam.setImage)
# s = QSizePolicy()
