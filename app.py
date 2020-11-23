from flask import Flask, render_template, request
import os
import finedust
import urllib
app = Flask(__name__)
__dir = os.getcwd()


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

    tmX1, tmY1 = finedust.tmLocation(do1, si1, urllib.parse.quote(dong1))
    print(tmX1, tmY1)
    tmX2, tmY2 = finedust.tmLocation(do2, si2, urllib.parse.quote(dong2))
    print(tmX2, tmY2)
    station1 = finedust.measuringStation(tmX1, tmY1)
    station2 = finedust.measuringStation(tmX2, tmY2)
    print(station1[0][1], station2[0][1])
    pm10s, pm25s = finedust.fineDust(station1, 0)
    pm10d, pm25d = finedust.fineDust(station2, 0)
    result10s, result25s = finedust.check(float(pm10s), float(pm25s))
    result10d, result25d = finedust.check(float(pm10d), float(pm25d))
    s1, s2, d1, d2 = finedust.convertToString(
        result10s, result25s, result10d, result25d)

    print(tmX1, tmY1, station1, pm10s, pm25s, result10s, result25s, s1, s2)
    print(tmX2, tmY2, station2, pm10d, pm25d, result10d, result25d, d1, d2)
    return render_template('result.html', pm10s=pm10s, pm25s=pm25s, pm10d=pm10d, pm25d=pm25d, pm10sValue=s1, pm25sValue=s2, pm10dValue=d1, pm25dValue=d2, result=finedust.makeResult(result10s, result25s, result10d, result25d))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port="3000")
