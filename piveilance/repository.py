import piveilance.generators
import piveilance.generators

from piveilance.model import View


class Repository():

    def __init__(self, objectData):
        self.objectData = objectData

    def getLayout(self, layoutId):
        newLayout = self.objectData['layouts'].get(layoutId)
        if not newLayout:
            raise ValueError("No layout found for id: '{}'".format(layoutId))

        _class = getattr(piveilance.model, newLayout['type'])
        return _class(**newLayout)

    def getView(self, viewId):
        view = self.objectData['views'].get(viewId)
        if not view:
            raise ValueError("No view found for id: '{}'".format(viewId))
        return View(**view)

    def getGenerator(self, generatorId):

        generatorConfig = self.objectData['generators'].get(generatorId)
        if not generatorConfig:
            raise ValueError("No generator found for id: '{}'".format(generatorId))
        generatorConfig['cameraRepo'] = self.objectData['cameras']
        try:
            generatorType = getattr(piveilance.generators, generatorConfig['type'])
        except KeyError:
            raise ValueError("Missing generator type - this field is required")
        except AttributeError:
            raise ValueError("Invalid generator type specified: '{}'.  "
                             "Allowed are [PiCamGenerator]".format(generatorConfig['type']))
        return generatorType(**generatorConfig)

    def getAllLayoutIds(self):
        return list(self.objectData['layouts'].keys())