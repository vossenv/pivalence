import random

import math

from piveilance.config import Parser


class FlowLayout():

    @classmethod
    def calculate(cls, width, height, camCount=None):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        cols = rows = frameSize = camCount
        while (cols > 0):
            rows = math.ceil(camCount / cols)
            frameSize = width / cols
            if ((height - frameSize * rows) < frameSize
                    and (rows * cols - camCount) <= 1
                    or rows > cols):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols

        return {'rows': rows, 'cols': cols, 'frameSize': frameSize}

    @classmethod
    def buildLayout(cls, camList, rows, cols):

        random.shuffle(camList)
        camList = sorted(camList, key=lambda x: x.order or len(camList)+1)

        grid = set((i, j) for i in range(rows) for j in range(cols))

        for c in camList:
            if grid:
                c.position = grid.pop()

        return camList

class FixedLayout():
    config = None

    @classmethod
    def calculate(cls, width, height, *args):
        cols = cls.config.get_int('cols')
        rows = cls.config.get_int('rows')
        frameSize = min(width / cols, height / rows)

        return {'rows': rows, 'cols': cols, 'frameSize': frameSize}

    @classmethod
    def correctCoordinates(cls, coords):
        return (coords[0] - 1, coords[1] - 1)

    @classmethod
    def buildLayout(cls, camList, *args):

        cols = cls.config.get_int('cols')
        rows = cls.config.get_int('rows')

        grid = set((i, j) for i in range(rows) for j in range(cols))
        pos = (cls.config.get_dict('positions') or {}).copy()

        pos.update({k: Parser.parse_collection(v) for k, v in pos.items()})
        pos.update({k: cls.correctCoordinates(v) for k, v in pos.items()})

        free = grid - set(pos.values())

        for c in camList:
            p = pos.get(c.name)
            if p in grid:
                c.position = p
            elif free:
                c.position = free.pop()

        x = {c.name:c.position for c in camList}


        return camList
