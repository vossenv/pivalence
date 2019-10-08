import random

import math


class FlowLayout():

    def __init__(self, grid, createCamera, layoutConfig):
        super(FlowLayout).__init__()
        self.grid = grid
        self.createCamera = createCamera

    def calculateProperties(self, width, height, camCount=None):

        """
        # Iterative computation to determine actual cols

        """
        # Start by initial guess that ncols = ncams
        cols = rows = sideLength = camCount
        while (cols > 0):
            rows = math.ceil(camCount / cols)
            sideLength = width / cols
            if ((height - sideLength * rows) < sideLength
                    and (rows * cols - camCount) <= 1
                    or rows > cols):
                break
            cols -= 1
        cols = 1 if cols < 1 else cols
        return rows, cols, sideLength

    def buildLayout(self, camList, options, rows, cols, maxCams):
        camList = [self.createCamera(n, options) for n in camList]
        fixedCams = sorted([c for c in camList if c.position], key=lambda x: x.position)
        freeCams = [c for c in camList if not c.position]
        random.shuffle(freeCams)
        fixedCams.extend(freeCams)

        camsOutput = []
        positions = [(i, j) for i in range(rows) for j in range(cols)]
        for c in fixedCams[0:maxCams]:
            p = positions.pop(0)
            self.grid.addWidget(c, *p)
            self.grid.addWidget(c.label, *p)
            camsOutput.append(c)
        return camsOutput


class FixedLayout():

    def __init__(self, grid, createCamera, layoutConfig):
        super(FixedLayout).__init__()
        self.grid = grid
        self.createCamera = createCamera
        self.layoutConfig = layoutConfig
        self.rows = self.layoutConfig.get_int('rows', 2)
        self.cols = self.layoutConfig.get_int('cols', 3)

    def calculateProperties(self, width, height, camCount=None):
        sideLength = min(width/self.cols, height/self.rows)
        return self.rows, self.cols, sideLength


    def buildLayout(self, camList, options, rows, cols, maxCams):
        camList = [self.createCamera(n, options) for n in camList]
        maxCams = rows*cols
        camsOutput = []
        positions = [(i, j) for i in range(rows) for j in range(cols)]
        for c in camList[0:maxCams]:
            p = positions.pop(0)
            self.grid.addWidget(c, *p)
            self.grid.addWidget(c.label, *p)
            camsOutput.append(c)
        return camsOutput