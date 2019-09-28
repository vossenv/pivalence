import json
import threading
import time

import cv2
import numpy as np
import requests
import screeninfo


def decode_string(string):
    try:
        return str(string.decode())
    except:
        return str(string)


class Camera(object):

    def __init__(self,
                 id,
                 refresh_rate,
                 update_url,
                 friendly_name=None,
                 color=True):
        self.id = id
        self.color = color
        self.refresh_rate = refresh_rate
        self.friendly_name = friendly_name if friendly_name else id
        self.update_url = update_url
        self.details = {}

    def update(self):
        r = requests.get(url=self.update_url, timeout=3)
        nparr = np.fromstring(r.content, np.uint8)
        z = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return z

class App:

    def __init__(self):
        self.server = 'http://192.168.50.139:9001'
        self.camera_list_path = self.server + '/camlist'
        self.camera_update_path = self.server + '/cameras/{}/next'
        self.color = True
        self.refresh_rate = 0.1
        self.threadList = []
        self.screen = screeninfo.get_monitors()
        self.global_cams = {}
        self.run()

    def run(self):
        self.update_camera_list()
        tl = []
        for cam in self.global_cams.values():
            t = threading.Thread(target=self.show_cam, args=[cam])
            t.setDaemon(True)
            t.start()
            tl.append(t)

        tl[0].join()
        #time.sleep()

    def update_camera_list(self):
        updated_cams = {}
        response = requests.get(url=self.camera_list_path)
        if response.status_code != 200:
            raise requests.RequestException(self.camera_list_path
                +  " " + str(response.content))

        for c in json.loads(response.content):
        #for c in ['front_bottom', '2048']:
            id = decode_string(c)
            cam = Camera(
                id=id,
                update_url=self.camera_update_path.format(id),
                refresh_rate=self.refresh_rate,
                color=self.color
            )
            updated_cams[id] = cam
        self.global_cams = updated_cams

    def show_cam(self, cam):
        while True:
            img = cam.update()
            cv2.imshow(cam.friendly_name, img)
            cv2.waitKey(50)

    #
    # def launchThreads(self):
    #
    #     for k, v in self.displayCache.items():
    #         t = threading.Thread(target=self.camLoader, args=[v])
    #         t.setDaemon(True)
    #
    #         t.start()
    #         self.threadList.append(t)

    # def displayLoop(self):
    #
    #     while True:
    #         time.sleep(self.dispUpdate)
    #
    #         r1 = np.concatenate(
    #             (self.displayCache['1'].data, self.displayCache['2'].data),
    #             axis=2)
    #         r2 = np.concatenate(
    #             (self.displayCache['3'].data, self.displayCache['4'].data),
    #             axis=2)
    #         r3 = np.concatenate(
    #             (self.displayCache['5'].data, self.displayCache['6'].data),
    #             axis=1)
    #
    #         rt1 = np.concatenate((r1, r2), axis=1)
    #         full = np.concatenate((rt1, r3), axis=2)
    #
    #         cv2.imshow("security feed",
    #                    cv2.resize(full[0, :, :, :], (1200, 800)))
    #         # cv2.moveWindow("security feed", -2, -30)
    #
    #         cv2.waitKey(100)
    #         time.sleep(0.25)



def main():
    App()

if __name__ == "__main__":
    main()