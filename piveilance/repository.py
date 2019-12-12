import piveilance.generators
import piveilance.generators
from piveilance.cameras import PlaceholderCamera
from piveilance.layout import Layout, View


class Repository():
    
    def __init__(self, objectData):
        self.objectData = objectData
        
    def getLayout(self, layoutId):
        newLayout = self.objectData['layouts'].get(layoutId)
        if not newLayout:
            raise ValueError("No layout found for id: '{}'".format(layoutId))
        newLayout['styleName'] = newLayout.pop('style_name', None)
        newLayout['maxAllowed'] = newLayout.pop('max_allowed', None)
        return Layout(**newLayout)

    def getView(self, viewId):
        view = self.objectData['views'].get(viewId)
        if not view:
            raise ValueError("No view found for id: '{}'".format(viewId))
        view['fontRatio'] = view.pop('font_ratio', None)
        return View(**view)

    def getGenerator(self, generatorId):

        generatorConfig = self.objectData['generators'].get(generatorId)
        if not generatorConfig:
            raise ValueError("No generator found for id: '{}'".format(generatorId))

        generatorConfig['dataUrl'] = generatorConfig.pop('data_url', None)
        generatorConfig['updateInterval'] = generatorConfig.pop('update_interval', None)
        generatorConfig['listRefresh'] = generatorConfig.pop('list_refresh', None)
        generatorConfig['cameraRepo'] = self.objectData['cameras']

        try:
            generatorType = getattr(piveilance.generators, generatorConfig['type'])
        except KeyError:
            raise ValueError("Missing generator type - this field is required")
        except AttributeError:
            raise ValueError("Invalid generator type specified: '{}'.  "
                             "Allowed are [PiCamGenerator]".format(generatorConfig['type']))
        return generatorType(**generatorConfig)

    @classmethod
    def placeholder(cls, id, name=None, position=None):
        return PlaceholderCamera(id=id, name=name or id, position=position)