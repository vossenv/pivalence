from PyQt5.QtGui import QImage
from piveilance.util import ImageManip





img = QImage("ent.jpg")
img_2 = ImageManip.crop(img, 300, 0, 300, 0)
img_2.save("cropped_image.jpg")
