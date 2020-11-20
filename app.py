from flask import Flask, render_template, request
from xml.etree import ElementTree
import requests
import os
import urllib

app = Flask(__name__)
__dir = os.getcwd()


def tmLocation(city, gu, dong):
    url = f'http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName={dong}&pageNo=1&numOfRows=10&ServiceKey=XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D'
    webpage = requests.get(url)
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.findall("item")
    length = len(itemTag)
    print(webpage.text)
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
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.findall("item")
    length = len(itemTag)
    station = []
    result = []
    distance = float(1000000.0)
    for i in range(0, length):
        tempStation = itemTag[i].find("stationName").text
        tempDistance = itemTag[i].find("tm").text
        result.append((float(tempDistance), tempStation))
        # if float(tempDistance) < float(distance):
        #     distance = tempDistance
        #     station = tempStation
    station = sorted(result, key=lambda stati: stati[0])
    return station


def fineDust(station, i):
    if i >= len(station):
        return 0, 0
    city = urllib.parse.quote(station[i][1])
    url = f'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty?stationName={city}&dataTerm=month&pageNo=1&numOfRows=10&ServiceKey=XwB4AI%2FK2JzvYUajkPyxGJ9IscGR%2FW0lrSTGfuWv9s7T4vWQonWulhbZaBQ0x78CHgl7SBF43dkfNfYsUnd1Hg%3D%3D&ver=1.3'
    webpage = requests.get(url)
    root = ElementTree.fromstring(webpage.text)
    bodyTag = root.find("body")
    itemsTag = bodyTag.find("items")
    itemTag = itemsTag.find("item")
    pm10 = itemTag.find("pm10Value").text
    pm25 = itemTag.find("pm25Value").text
    if pm10 == '-' or pm25 == '-':
        pm10, pm25 = fineDust(station, i+1)
    print(station[i][1])
    return pm10, pm25


def makeResult(results10, results25, resultd10, resultd25):
    result = ''
    if results25 >= 2:
        mask = "kf94"
    elif results10 >= 2:
        mask = "kf80"

    if results25 > 2 or results10 > 2:
        result = f"가급적 외출을 자제하시고 외출시엔 {mask} 마스크를 꼭 착용해주시고, "
    elif results25 > 1 or results10 > 1:
        result = f"외출시에 {mask} 마스크를 꼭 착용해주시고, "
    else:
        result = "출발지에선 마스크를 착용 안하셔도 되고, "

    if resultd25 >= 2:
        mask = "kf94"
    elif resultd10 >= 2:
        mask = "kf80"

    if resultd25 > 2 or resultd10 > 2:
        result = result + f"도착하시면 실내로 들어가시거나 {mask} 마스크를 꼭 착용하셔야 합니다!"
    elif resultd25 > 1 or resultd10 > 1:
        result = result + f"도착하셔도 {mask} 마스크를 꼭 착용하셔야 합니다!"
    else:
        result = result + "도착지에서는 마스크를 벗으셔도 됩니다!"

    if results10 < 2 and resultd10 < 2 and results25 < 2 and resultd25 < 2:
        result = "마스크를 착용안하시고 외출하셔도 됩니다!"
    return result


def check(pm10, pm25):
    pm10Stat = ''
    pm25Stat = ''
    if pm10 < 30:
        pm10Stat = 0  # good
    elif pm10 < 80:
        pm10Stat = 1  # nomal
    elif pm10 < 150:
        pm10Stat = 2  # bad
    else:
        pm10Stat = 3  # very bad

    if pm25 < 15:
        pm25Stat = 0  # good
    elif pm25 < 35:
        pm25Stat = 1  # nomal
    elif pm25 < 75:
        pm25Stat = 2  # bad
    else:
        pm25Stat = 3  # very bad

    return pm10Stat, pm25Stat


def convertToString(result10s, result25s, result10d, result25d):
    if result10s == 0:
        s1 = "좋음"
    elif result10s == 1:
        s1 = "보통"
    elif result10s == 2:
        s1 = "나쁨"
    elif result10s == 3:
        s1 = "매우나쁨"

    if result25s == 0:
        s2 = "좋음"
    elif result25s == 1:
        s2 = "보통"
    elif result25s == 2:
        s2 = "나쁨"
    elif result25s == 3:
        s2 = "매우나쁨"

    if result10d == 0:
        d1 = "좋음"
    elif result10d == 1:
        d1 = "보통"
    elif result10d == 2:
        d1 = "나쁨"
    elif result10d == 3:
        d1 = "매우나쁨"

    if result25d == 0:
        d2 = "좋음"
    elif result25d == 1:
        d2 = "보통"
    elif result25d == 2:
        d2 = "나쁨"
    elif result25d == 3:
        d2 = "매우나쁨"

    return s1, s2, d1, d2


@app.route("/")
def hello():
    return render_template('main.html')


@app.route("/result", methods=['POST'])
def result():
    temp1 = request.form["sigudong1"]
    temp2 = request.form["sigudong2"]
    print(temp1, temp2)
    arr1 = temp1.split(' ')
    arr2 = temp2.split(' ')
    if len(arr1) == 3:
        do1, si1, dong1 = arr1[0], arr1[1], arr1[2]
    else:
        do1, si1, dong1 = arr1[0], arr1[1] + " " + arr1[2], arr1[3]
    if len(arr2) == 3:
        do2, si2, dong2 = arr2[0], arr2[1], arr2[2]
    else:
        do2, si2, dong2 = arr2[0], arr2[1] + " " + arr2[2], arr2[3]

    tmX1, tmY1 = tmLocation(do1, si1, urllib.parse.quote(dong1))
    print(tmX1, tmY1)
    tmX2, tmY2 = tmLocation(do2, si2, urllib.parse.quote(dong2))
    print(tmX2, tmY2)
    station1 = measuringStation(tmX1, tmY1)
    station2 = measuringStation(tmX2, tmY2)
    print(station1[0][1], station2[0][1])
    pm10s, pm25s = fineDust(station1, 0)
    pm10d, pm25d = fineDust(station2, 0)
    result10s, result25s = check(float(pm10s), float(pm25s))
    result10d, result25d = check(float(pm10d), float(pm25d))
    s1, s2, d1, d2 = convertToString(
        result10s, result25s, result10d, result25d)

    print(tmX1, tmY1, station1, pm10s, pm25s, result10s, result25s, s1, s2)
    print(tmX2, tmY2, station2, pm10d, pm25d, result10d, result25d, d1, d2)
    return render_template('result.html', pm10s=pm10s, pm25s=pm25s, pm10d=pm10d, pm25d=pm25d, pm10sValue=s1, pm25sValue=s2, pm10dValue=d1, pm25dValue=d2, result=makeResult(result10s, result25s, result10d, result25d))


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port="3000")
