from flask import Flask, render_template, request, jsonify
import urllib2, json, requests

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        print(form)
        selection = form["category"]
        mood = form["moodoptions"]
        if selection == "weather":
            getWeatherSongs()
        elif selection == "location":
            getLocationSongs()
        elif selection == "mood":
            getSongs(mood)

def getLocation():
    url = "http://ipinfo.io/"
    results = requests.get(url).json()
    city = results["city"]
    return city
            
def getLocationSongs():
    tag = getLocation()
    getSongs(tag)

def getWeather():
    city = getLocation()
    url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&APPID=537eb84d28d1b2075c6e44b37f511b10"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    weather = r["weather"][0]["main"]
    return weather

def getWeatherSongs():
    tag = getWeather()
    getSongs(tag)
    
def getSongs(tag):
    url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    songlist = []
    for song in r["tracks"]["track"]:
        print(song["name"])
        songlist.append(song)

if (__name__ == "__main__"):
    app.debug = True
    app.run(host='localhost', port=3000)
