from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont, QPen

from piveilance.util import ImageManip




def test_add_text():


    img = QImage()
    img.load("ent.jpg")





    painter = QPainter(img)
    painter.setPen(Qt.blue)
    painter.setFont(QFont("Arial", 30))
    painter.drawText(QPoint(10,10), "Qt")
   # painter.end()

 #   painter.setFont(QFont.SansSerif)
 #   painter.setPen(QPen(Qt.red))
#    painter.drawText(img.rect(), Qt.AlignBottom, "Hello")

    #
    # painter.drawLine(img.rect().bottomLeft().x(), img.rect().bottomLeft().y() - 10,
    #            img.rect().bottomRight().x(), img.rect().bottomRight().y() - 10)

#    painter.end()
    img.save("x.jpg")

    # p.drawText(image.rect(), Qt::AlignCenter, "Text");
    # p.end();

    print()
