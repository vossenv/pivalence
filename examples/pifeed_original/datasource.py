import requests
import datetime

class SecurityCamConnector(object):

    def __init__(self):
        self.authorization = {"username": "caragcookiemonster@gmail.com", "password": "C@ragian5"}
        self.devices = ["2048", "2049"]
      #  self.logger = open("auth.txt", "a")

        try:
            self.headers = self.Authenticate()
        except:
            pass

    def Authenticate(self):

        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}

        URL = "https://www.alarm.com/web/Default.aspx"
        parameters = ['afg', 'auth_CustomerDotNet', 'twoFactorAuthenticationId', 'ASP.NET_SessionId']

        data = {'IsFromNewSite': '1',
                'ctl00$ContentPlaceHolder1$loginform$txtUserName': self.authorization['username'],
                'txtPasswordt': self.authorization['password']}

        auth_data = (requests.post(url=URL, data=data, headers=headers, allow_redirects=False)).cookies._cookies

        cookieJar = auth_data['www.alarm.com']['/']
        cookieJar['twoFactorAuthenticationId'] = auth_data['.alarm.com']['/']['twoFactorAuthenticationId']

        headers['Cookie'] = "cookieTest=1;IsFromNewSite=1; loggedInAsSubscriber=1;"
        for c in parameters:
            headers['Cookie'] += c + "=" + cookieJar[c].value + ";"

      #  self.logger.write("Authenticated at:  " + datetime.datetime.now().strftime("%Y-%m-%d: %H:%M:%S") + "\n")
      #  self.logger.flush()

        return headers

    def get(self, deviceId):

        Image_Base_URL = "https://www.alarm.com/web/Video/GetImage.aspx?res=0&qual=10&deviceID="

        r = requests.get(url=(Image_Base_URL + deviceId), headers=self.headers, timeout=3)

        if ("Login" in str(r.content)) or r.status_code is not 200:
            self.headers = self.Authenticate()

            raise AssertionError("Cookies exipred, re-authenticating")

        if r.content is not None:
            return r
        else:
            raise AssertionError("Empty or invalid response")


class LocalCamConnector(object):

    def get(self, address):

        r = requests.get("http://" + address + ":9001/frame", timeout=3)

        if r.status_code is 200 and r.content is not None:
            return r
        else:
            raise AssertionError("Empty or invalid response")

class LocalAPIConnector(object):

    def __init__(self):
        self.server = "http://192.168.50.139:9001"

    def get(self, name):

        r = requests.get( self.server + "/cameras/" + name + "/next", timeout=3)

        if r.status_code is 200 and r.content is not None:
            return r
        else:
            raise AssertionError("Empty or invalid response")


class WeatherConnector(object):

    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5/weather?"
        self.zip = "55407"
        self.units = "imperial"
        self.api_key = "d446ade3c095f0739178c40ed40583be"
        self.target = self.base_url + "zip=" + self.zip + ",us&units=" + self.units + "&APPID=" + self.api_key

    def getCurrentData(self):

        temps = dict()
        wind = dict()
        weather = dict()

        try:
            response = requests.get(self.target).json()
        except Exception as e:
            raise requests.ConnectionError("Failed to retrive data... " + str(e))

        full_data = self.decode(response)

        wind['speed'] = {'value': float(full_data['wind']['speed']) * 2.23694, 'units': 'mph'}
        wind['direction'] = {'value': float(full_data['wind']['deg']), 'units': 'deg'}
        wind['direction']['friendly'] = self.convertToDirection(wind['direction']['value'])

        temps['current'] = {'value': float(full_data['main']['temp']), 'units': 'F'}
        temps['min'] = {'value': float(full_data['main']['temp_min']), 'units': 'F'}
        temps['max'] = {'value': float(full_data['main']['temp_max']), 'units': 'F'}

        weather['temperature'] = temps
        weather['wind'] = wind
        weather['conditions'] = full_data['weather'][0]
        weather['humidity'] = {'value': float(full_data['main']['humidity']), 'units': '%'}
        weather['pressure'] = {'value': float(full_data['main']['pressure']) * 1.33322, 'units': 'mmHg'}
        weather['icon'] = {'url': "https://openweathermap.org/img/w/" + weather['conditions']['icon'] + ".png"}
        weather['all'] = full_data

        try:
            weather['icon']['content'] = requests.get(weather['icon']['url']).content
        except:
            pass

        return weather

    def convertToDirection(self, d):

        if d == 0 or d == 360:
            dir = 'N'
        elif d == 90:
            dir = 'W'
        elif d == 180:
            dir = 'S'
        elif d == 270:
            dir = 'E'
        elif (0 < d) and (d < 90):
            dir = 'NW'
        elif (90 < d) and (d < 180):
            dir = 'SW'
        elif (180 < d) and (d < 270):
            dir = 'SE'
        elif (270 < d) and (d < 360):
            dir = 'NE'
        else:
            dir = 'Unknown'

        return dir

    def decode(self, encoded):

        decoded = dict()

        for k in encoded:
            v = encoded[k]
            k_dec = k.encode("ascii", "replace")

            if isinstance(v, dict):
                decoded[k_dec] = self.decode(v)
            elif isinstance(v, list):
                x = list()
                for entry in v:
                    x.append(self.decode(entry))
                decoded[k_dec] = x

            else:
                v_dec = str(v).encode("ascii", "replace")
                decoded[k_dec] = v_dec
        return dict(decoded)
