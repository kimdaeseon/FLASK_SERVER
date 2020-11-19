from flask import Flask
from xml.etree import ElementTree
import requests
import urllib


def tmLocation(city, gu, dong):
    url = f'http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName={dong}&pageNo=1&numOfRows=10&ServiceKey=XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D'
    webpage = requests.get(url)
    print(webpage.text)
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.findall("item")
    print(webpage.text)
    length = len(itemTag)
    for i in range(0, length):
        si = itemTag[i].find("sidoName").text
        sgg = itemTag[i].find("sggName").text
        tmX = itemTag[i].find("tmX").text
        tmY = itemTag[i].find("tmY").text
        if gu in sgg:
            break
        else:
            tmX, tmY = 0, 0

    return tmX, tmY


def measuringStation(tmX, tmY):
    url = f'http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getNearbyMsrstnList?tmX={tmX}&tmY={tmY}&ServiceKey=XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D'
    webpage = requests.get(url)
    print(webpage.text)
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.findall("item")
    length = len(itemTag)
    station = ""
    distance = float(1000000.0)
    for i in range(0, length):
        tempStation = itemTag[i].find("stationName").text
        tempDistance = itemTag[i].find("tm").text
        if float(tempDistance) < float(distance):
            distance = tempDistance
            station = tempStation

    return station


def fineDust(city):
    url = f'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName={city}&dataTerm=month&pageNo=1&numOfRows=10&ServiceKey=XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D&ver=1.3'
    webpage = requests.get(url)
    print(webpage.text)
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.find("item")
    pm10 = itemTag.find("pm10Value").text
    pm25 = itemTag.find("pm25Value").text

    return pm10, pm25


def check(pm10, pm25):
    pm10Stat = ''
    pm25Stat = ''
    if pm10 < 30:
        pm10Stat = 'good'
    elif pm10 < 80:
        pm10Stat = 'nomal'
    elif pm10 < 150:
        pm10Stat = 'bad'
    else:
        pm10Stat = 'terrible'

    if pm25 < 15:
        pm25Stat = 'good'
    elif pm25 < 35:
        pm25Stat = 'nomal'
    elif pm25 < 75:
        pm25Stat = 'bad'
    else:
        pm25Stat = 'terrible'

    return pm10Stat, pm25Stat


tmX, tmY = tmLocation("경기도", "용인시", urllib.parse.quote("서천동"))
station = measuringStation(tmX, tmY)
pm10, pm25 = fineDust(urllib.parse.quote(station))
print(tmX, tmY, station, pm10, pm25)
#print(a, b)
# city = '강서구'
# key = 'XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D'
# url = 'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty'
# payload = {'stationName': city, 'dataTerm': 'month', 'pageNo': '1', 'numOfRows': '10',
#            'ServiceKey': key, 'ver': '1.3'}


# app = Flask(__name__)
# @app.route("/hello")
# def hello():
#     return "<h1>JaeSung Fighting</h1>"


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port="8080")
