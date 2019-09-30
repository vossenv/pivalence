import math


def computeGrid(camCount, width, height):

    cols, rows, sideLength = calculateCols(camCount, width, height)
    remainder_height = height - sideLength * rows

    if remainder_height < 0:
        sideLength = sideLength - abs(remainder_height / rows)

    rheight = max(height - sideLength * rows, 0) / 2
    vheight = max(width - sideLength * cols, 0) / 2
    dimensions = (vheight, rheight, vheight, rheight)
    return cols, dimensions, sideLength


def calculateCols(camCount, width, height):
    """
    # Iterative computation to determine actual cols

    """
    # Start by initial guess that ncols = ncams
    cols = rows = sideLength = camCount
    while (cols > 0):
        rows = math.ceil(camCount / cols)
        sideLength = width / cols
        if (height - sideLength * rows) < sideLength:
            break
        cols -= 1
    cols = 1 if cols < 1 else cols
    return cols, rows, sideLength

def areSetsEqual(a, b):
    a = a or set()
    b = b or set()
    a = set(a)
    b = set(b)
    return  (a - b) == (b - a)
