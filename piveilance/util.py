
def compareIter(a, b):
    return (len(a) == len(b) and
            {x in b for x in a} ==
            {x in b for x in a} ==
            {True})


class ImageManip():

    @classmethod
    def crop_direction(cls, image, amount, direction='center'):
        if direction == 'right':
            return ImageManip.crop(image, 0, 0, 0, amount)
        elif direction == 'hcenter':
            return ImageManip.crop(image, 0, amount / 2, 0, amount / 2)
        elif direction == 'vcenter':
            return ImageManip.crop(image, amount / 2, 0, amount / 2, 0)
        elif direction == 'left':
            return ImageManip.crop(image, 0, 0, 0, amount)
        elif direction == 'top':
            return ImageManip.crop(image, amount, 0, 0, 0)
        elif direction == 'bottom':
            return ImageManip.crop(image, 0, 0, amount, 0)
        elif direction == 'square':
            return ImageManip.crop(image, amount/4, amount/4, amount/4, amount/4)
        raise ValueError("Invalid direction: " + direction)

    @classmethod
    def crop(cls, image, top, left, bottom, right):
        w = image.width() - left - right
        h = image.height() - top - bottom
        return image.copy(left, top, w, h)

    @classmethod
    def cropCenter(cls, image, size):
        return cls.crop(image, size, size, size, size)
