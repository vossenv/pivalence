
import threading
import time
import cv2
import numpy as np
import screeninfo
import datetime
from examples.pifeed_original import datasource as ds

import json
import requests

# "2048",
# "2049",
# "back_bottom",
# "front_bottom",
# "front_top",
# "back_top",
# "pi4",
# "test"

url = 'http://192.168.50.139:9001/camlist'

z = requests.get(url=url)

cams = json.loads(z.content)


print()


class Main:

    def __init__(self):

        self.localCamSleep = 0.1
        self.alarmCamSleep = .5
        self.dispUpdate = 0.05
        self.color = True
        self.displayCache = {}
        self.threadList = []
        self.screen = screeninfo.get_monitors()

    def buildCameraList(self):

        tempList = []
        tempList.append(Camera('1', "192.168.50.78","local", self.localCamSleep, name='back_top', color=self.color))
        tempList.append(Camera('2', "192.168.50.230","local", self.localCamSleep, name='back_bottom', color=self.color))
        tempList.append(Camera('3', "192.168.50.227","local",  self.localCamSleep, name= 'front_top', color=self.color))
        tempList.append(Camera('4', "192.168.50.59","local",  self.localCamSleep, name='front_bottom', color=self.color))

        tempList.append(Camera('5', "2048","alarm",  self.alarmCamSleep, name="2048", dim=(614, 384), color=self.color))
        tempList.append(Camera('6', "2049","alarm",  self.alarmCamSleep,  name="2049", dim=(614, 384), color=self.color))

        for cam in tempList:
            self.displayCache[cam.id] = cam

    def camLoader(self, camera):

        logger = open("feed.txt", "a")

        while True:

            try:

                camera.update()

            except Exception as e:

                logger.write("Exception\t"
                             + str(camera.name) + " @ "
                             + str(camera.target) + ": "
                             + str(e.message) + "\n")


            time.sleep(camera.sleepTime)



    def launchThreads(self):

        for k, v in self.displayCache.items():

            t = threading.Thread(target=self.camLoader, args=[v])
            t.setDaemon(True)

            t.start()
            self.threadList.append(t)


    def displayLoop(self):

        while True:

            time.sleep(self.dispUpdate)

            r1 = np.concatenate((self.displayCache['1'].data, self.displayCache['2'].data), axis=2)
            r2 = np.concatenate((self.displayCache['3'].data, self.displayCache['4'].data), axis=2)
            r3 = np.concatenate((self.displayCache['5'].data, self.displayCache['6'].data), axis=1)


            rt1 = np.concatenate((r1, r2), axis=1)
            full = np.concatenate((rt1, r3), axis=2)

            cv2.imshow("security feed", cv2.resize(full[0,:,:,:], (1200,800)))
           # cv2.moveWindow("security feed", -2, -30)

            cv2.waitKey(100)
            time.sleep(0.25)


    def run(self):

        self.buildCameraList()
        self.launchThreads()
        self.displayLoop()

        time.sleep(100)

class Camera(object):

    def __init__(self, id, target, type, sleepTime, name=None, dim=None, color=True):
        self.id = id
        self.target = target
        self.type = type
        self.sleepTime = sleepTime
        self.dim = dim if dim else (512,384)
        self.name = name if name else "unknown"
        self.frame = [1,self.dim[1],self.dim[0]]
        self.info = {}


        if color:
            self.frame += [3]
            self.conversion = cv2.COLOR_BGR2RGB
        else:
            self.conversion =  cv2.COLOR_BGR2GRAY

        self.data = np.zeros(self.frame, dtype="uint8")

        if type == "local":
            self.connector = ds.LocalAPIConnector()

        elif type == "alarm":
            self.connector = ds.SecurityCamConnector()
        else:
            raise TypeError ("Unkown device type: " + type)



    def update(self):

        resp = self.connector.get(self.name)
        nparr = np.fromstring(resp.content, np.uint8)

        # if self.type == "local":
        #     try:
        #         self.info['Percent-Motion'] = resp.headers['Percent-Motion']
        #     except:
        #         pass


        try:

            if len(nparr > 100):
                z = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if self.type == "alarm":
                    cv2.putText(z, datetime.datetime.now().strftime("%Y-%m-%d: %H:%M:%S:%f"), (18, z.shape[0] - 25), cv2.FONT_HERSHEY_DUPLEX, 1.6, (255, 255, 255), 2, cv2.LINE_AA)

                np.copyto(self.data[0, :, :], cv2.resize(cv2.cvtColor(z, self.conversion), self.dim))


        except Exception as e:
            print (str(len(nparr)) + " " + str(e))





Main().run()
