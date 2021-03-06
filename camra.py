from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import urllib2, json, requests, spotipy, sqlite3, os
from sqlite3 import Error
from flask_login import LoginManager, login_user, logout_user, current_user
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import sys, random, os
from User import User
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from wordFilter import * 
from sqlalchemy import *

engine = create_engine('sqlite:///:memory:')
metadata = MetaData()
client_credentials_manager = SpotifyClientCredentials(client_id = '0b4d677f62e140ee8532bed91951ae52', client_secret = 'cc1e617a9c064aa982e8eeaf65626a94')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

def filterUsername(username, password):
    if not username:
        print ("no username")
        return -1
    if not password:
        print ("no password")
        return -1
    if (len(username) < 4) or (len(password) < 4):
        print ("too short")
        return -1
    if (len(username) > 15) or (len(password) > 15):
        print ("too long")
        return -1
    if ("~" in username) or ("~" in password):
        print("no special characters allowed: ~")
        return -1
    if ("!" in username) or ("!" in password):
        print("no special characters allowed: !")
        return -1
    if ("@" in username) or ("@" in password):
        print("no special characters allowed: @")
        return -1
    if ("#" in username) or ("#" in password):
        print("no special characters allowed: #")
        return -1
    if ("$" in username) or ("$" in password):
        print("no special characters allowed: $")
        return -1
    if ("%" in username) or ("%" in password):
        print("no special characters allowed: %")
        return -1
    if ("^" in username) or ("^" in password):
        print("no special characters allowed: ^")
        return -1
    if ("&" in username) or ("&" in password):
        print("no special characters allowed: &")
        return -1
    if ("*" in username) or ("*" in password):
        print("no special characters allowed: *")
        return -1
    if ("(" in username) or ("(" in password):
        print("no special characters allowed: (")
        return -1
    if (")" in username) or (")" in password):
        print("no special characters allowed: )")
        return -1
    if (username is "username") or (username is "password"):
        print("generic username. choose something else")
        return -1
    if (password is "username") or (password is "password"):
        print("generic password. choose something else")
        return -1
    if (filterBadSongs(username)):
        print ("explicit language in username not allowed")
        return -1
    if (filterBadSongs(password)):
        print ("explict language in password not allowed")
        return -1
    return 1
    
def createPlaylist():
    path = os.path.dirname(os.path.abspath(__file__))
    if (path is None):
        print ("Wrong file path")
    conn = sqlite3.connect(path + '/test.db')
    if (conn is None):
        print ("nonexistant database")
    cursor = conn.cursor()
    if (cursor is None):
        print "error in creating playlist"
    cursor.execute('''CREATE TABLE IF NOT EXISTS Song (s_id integer PRIMARY KEY, name text, artist text, url text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, keyword text, FOREIGN KEY(keyword) REFERENCES masterPlaylist(keyword), FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS masterPlaylist (mp_id integer, keyword text PRIMARY KEY, length integer, FOREIGN KEY(mp_id) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Account (a_id integer PRIMARY KEY, playlist integer, p_id integer, FOREIGN KEY(playlist) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username text, password text, p_id integer, PRIMARY KEY(username, p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Friends (myUsername text, friend text, FOREIGN KEY(friend) REFERENCES users(username), PRIMARY KEY(myUsername, friend)) ''')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Song'")
    if (cursor.fetchone() is None):
        print("error no Song table")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Playlist'")
    if (cursor.fetchone() is None):
        print("error no Playlist table")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='masterPlaylist'")
    if (cursor.fetchone() is None):
        print("error no masterPlaylist table")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Account'")
    if (cursor.fetchone() is None):
        print("error no Account table")
    conn.commit()
    
def getMasterList(tag):
    songlist = []
    songCounter = 0
    sOffset = 0
    while (songCounter < 200):
        print("fack u")
        results = sp.search(q = tag, limit = 2, offset = sOffset, type = 'playlist')
        for playlist in results["playlists"]["items"]:
            playlistid = playlist["id"]
            print(playlist["owner"]["id"])
            if (',' not in playlist["owner"]["id"]):
                playlistuser = playlist["owner"]["id"]
                print(playlistuser)
                sOffset += 2
                print("why are u here")
                psongs = sp.user_playlist_tracks(user = playlistuser, playlist_id = playlistid)
            else:
                continue
            for tInfo in psongs["items"]:
                song = {}
                if '-' not in tInfo["track"]["name"]:
                    if '@' not in tInfo["track"]["name"]:
                        if '#' not in tInfo["track"]["name"]:
                            if '$' not in tInfo["track"]["name"]:
                                if '%' not in tInfo["track"]["name"]:
                                    if '&' not in tInfo["track"]["name"]: 
                                        song["name"] = tInfo["track"]["name"]
                                        if '-' not in tInfo["track"]["artists"][0]["name"]:
                                            if '@' not in tInfo["track"]["artists"][0]["name"]:
                                                if '#' not in tInfo["track"]["artists"][0]["name"]:
                                                    if '$' not in tInfo["track"]["artists"][0]["name"]:
                                                        if '%' not in tInfo["track"]["artists"][0]["name"]:
                                                            if '&' not in tInfo["track"]["artists"][0]["name"]: 
                                                                song["artist"] = tInfo["track"]["artists"][0]["name"]
                                                                song["url"] = tInfo["track"]["preview_url"]
                                                                songCounter += 1
                                                                if (song["url"] != None):
                                                                    songlist.append(song)

    print("before this last fm")
    url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json&limit=200"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    #check to make sure that the r isnt null
    for song in r["tracks"]["track"]:
        results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
        if (results["tracks"]["items"] != []):
            if (results["tracks"]["items"][0]["preview_url"] != None):
                Nsong = {}
                Nsong["name"] = song["name"]
                Nsong["artist"] = song["artist"]["name"]
                Nsong["url"] = results["tracks"]["items"][0]["preview_url"]
                songlist.append(Nsong)
            else:
                print("WARNING: track has no preview")
        else:
            print("ERROR: no results")
    return songlist

def insertDBMaster(mPlaylist, keyword):
    print("entered insert db master")
    path = os.path.dirname(os.path.abspath(__file__))
    if (path is None):
        print ("Wrong file path")
    conn = sqlite3.connect(path + '/test.db')
    if (conn is None):
        print ("nonexistant database")
    cursor = conn.cursor()
    if (cursor == None):
         print ("ERROR opening cursor to database")
    insertSongs = []
    insertPlaylist = []
    insertMaster = []
    if (mPlaylist == None):
        print("ERROR: playlist to insertDBMaster does not exist")
        return -1
    if (keyword == None):
        print("ERROR: keyword to insertDBMaster does not exist")
        return -1
    else:
        pID = abs(hash(keyword)) % (10 ** 8)
        for song in mPlaylist:
            #create the hash for the song
            if (filterBadSongs(song["name"]) == False):
                songName = song["name"]
                songArtist = song["artist"]
                songURL = song["url"]
                songID = abs(hash(songName+songArtist)) % (10 ** 8)
                songTuple = (songID, songName, songArtist, songURL)
                for item in songTuple:
                    if (item == None):
                        print("ERROR: one or more fields in songTuple does not exist")
                        return -1
                playlistTuple = (pID, songID, keyword)
                insertPlaylist.append(playlistTuple)
                insertSongs.append(songTuple)
       
        cursor.executemany("INSERT OR REPLACE INTO Song VALUES (?,?,?,?)", insertSongs)
        conn.commit()
        cursor.executemany("INSERT OR REPLACE INTO Playlist VALUES (?,?,?)", insertPlaylist)
        conn.commit()
        cursor.execute("INSERT OR REPLACE INTO masterPlaylist VALUES (" + str(pID) + ", "+"'"+keyword+"'"+", " + str(len(mPlaylist)) + ")")
        conn.commit()
        print(keyword)
        cursor.execute("SELECT * FROM masterPlaylist WHERE mp_id = " + str(pID) + " AND keyword = " + "'"+ keyword +"'" + " AND length = " + str(len(mPlaylist)))
        if (cursor.fetchone() == None):
            print("ERROR: unable to insert Master Playlist entry")

def loadDatabases():
    print("enter")
    happySongs = getMasterList('happy')
    insertDBMaster(happySongs, 'happy')
    print("happy")
    sadSongs = getMasterList('sad')
    insertDBMaster(sadSongs, 'sad')
    print("sad")
    angrySongs = getMasterList('angry')
    insertDBMaster(angrySongs, 'angry')
    print("angry")
    nervousSongs = getMasterList('nervous')
    insertDBMaster(nervousSongs, 'nervous')
    print("nervous")
    scaredSongs = getMasterList('scared')
    insertDBMaster(scaredSongs, 'scared')
    print("scared")
    thunderstorm = getMasterList("Thunderstorm")
    insertDBMaster(thunderstorm, 'Thunderstorm')
    print("thunder")
    drizzle = getMasterList("Drizzle")
    insertDBMaster(drizzle, 'Drizzle')
    print("drizz")
    rain = getMasterList("Rain")
    insertDBMaster(rain, 'Rain')
    print("rain")
    snow = getMasterList("Snow")
    insertDBMaster(snow, 'Snow')
    print("snow")
    clear = getMasterList("Clear")
    insertDBMaster(clear, 'Clear')
    print("clear")
    clouds = getMasterList("Clouds")
    insertDBMaster(clouds, 'Clouds')
    print("cloud")
    extreme = getMasterList("Extreme")
    insertDBMaster(extreme, 'Extreme')
    print("extreme")
    boston = getMasterList("Boston")
    insertDBMaster(boston, 'Boston')
    print("bost")
    washingtonDC = getMasterList("Washington DC")
    insertDBMaster(washingtonDC, 'Washington DC')
    print("dc")
    LA = getMasterList("Los Angeles")
    insertDBMaster(LA, 'Los Angeles')
    print("la")
    seattle = getMasterList("Seattle")
    insertDBMaster(seattle, 'Seattle')
    print("seat")
    columbus = getMasterList("Columbus")
    insertDBMaster(columbus, 'Columbus')
    print("col")
    newyork = getMasterList("New York")
    insertDBMaster(newyork, 'New York')
    print("ny")
    honolulu = getMasterList("Honolulu")
    insertDBMaster(honolulu, 'Honolulu')
    print("honolulu")
    anchorage = getMasterList("Anchorage")
    insertDBMaster(anchorage, 'Anchorage')
    print("ank")
    nashville = getMasterList("Nashville")
    insertDBMaster(nashville, 'Nashville')
    print("nash")
    atlanta = getMasterList("Atlanta")
    insertDBMaster(atlanta, 'Atlanta')
    print("atl")
    dallas = getMasterList("Dallas")
    insertDBMaster(dallas, 'Dallas')
    print("dal")
    houston = getMasterList("Houston")
    insertDBMaster(houston, 'Houston')
    print("hous")
    chicago = getMasterList("Chicago")
    insertDBMaster(chicago, 'Chicago')
    print("chi")
    portland = getMasterList("Portland")
    insertDBMaster(portland, 'Portland')
    print("ptl")
    orlando = getMasterList("Orlando")
    insertDBMaster(orlando, 'Orlando')
    print("orl")
    miami = getMasterList("Miami")
    insertDBMaster(miami, 'Miami')
    print("miami")
    print("FIN")

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

@app.route("/", methods=["GET", "POST"])
def index():
    length = request.form.get("length")
    if (length is None):
        return render_template("index.html")#print on screen that you need a length
    return render_template("index.html")

@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        form = request.form
        if (form is None):
            print("No form found")
        if "category" in form:
            category = form["category"]
        else:
            message = "ERROR: You did not specify a category"
            return render_template("index.html", message=message)
        length = form["length"]
        print("printing length")
        print(length)
        if (length == ""):
            message = "ERROR: You did not specify a length"
            return render_template("index.html", message=message)
        else:
            length = int(length)
        mood = form["moodoption"]
        if (mood is None):
            print("No mood")
        songs = []
        if (category == "location"):
            songs = getLocationSongs(length)
        elif (category == "weather"):
            songs = getWeatherSongs(length)
        elif (category == "mood"):
            songs = getSongs(mood, length)
        elif (category == "random"):
            songs = getRandomSongs(length)
        else:
            return redirect(url_for('index'))#redirect to 404 screen
        return render_template('results.html', songs=songs)        

@app.route("/viewplaylist", methods=["GET", "POST"])
def viewplaylist():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        form = request.form
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        keyword = form["keyword"]
        if keyword is None:
            return redirect(url_for('index'))#404 page
        output = viewPlaylist(p_id)
        if (output == -1):
            return redirect(url_for('index'))#404 page
        return render_template('view.html', songs=output, p_id=p_id, keyword=keyword)
    
@app.route("/export", methods=["GET", "POST"])
def export():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        form = request.form
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        name = form["pName"]
        if name is None:
            return redirect(url_for('index'))#404 page
        username = form["sUsername"]
        if username is None:
            return redirect(url_for('index'))#404 page
        return exportSpotify(p_id, name, username)

@app.route("/modify", methods=["GET", "POST"])
def modify():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path + '/test.db')
        cursor = conn.cursor()
        output = []
        form = request.form
        s_ids = form.getlist("s_id")
        print(s_ids)
        for s_id in s_ids:
            cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id))
            song = cursor.fetchone()
            if (song != None):
                song = song[0]
            cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id))
            artist = cursor.fetchone()
            if (artist != None):
                artist = artist[0]
            cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id))
            url = cursor.fetchone()
            if (url != None):
                url = url[0]
            song_info = {}
            song_info["name"] = song
            song_info["artist"] = artist
            song_info["url"] = url
            song_info["s_id"] = s_id
            song_info_json = json.loads(json.dumps(song_info))
            output.append(song_info_json)
        return render_template('modify.html', songs=output)

@app.route("/submitmodify", methods=["GET", "POST"])
def submitmodify():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path + '/test.db')
        cursor = conn.cursor()
        output = []
        form = request.form
        s_ids = form.getlist("s_id")
        print("printing sid list")
        print(s_ids)
        print(s_ids[0])
        for s_id in s_ids:
            cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id))
            song = cursor.fetchone()
            if (song != None):
                song = song[0]
            cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id))
            artist = cursor.fetchone()
            if (artist != None):
                artist = artist[0]
            cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id))
            url = cursor.fetchone()
            if (url != None):
                url = url[0]
            song_info = {}
            song_info["name"] = song
            song_info["artist"] = artist
            song_info["url"] = url
            song_info["s_id"] = s_id
            song_info_json = json.loads(json.dumps(song_info))
            output.append(song_info_json)
        return render_template("results.html", songs = output)

@app.route("/save", methods=["GET", "POST"])
def save():
    if request.method == "GET":
        return redirect(url_for('index'))
    elif request.method == "POST":
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path + '/test.db')
        cursor = conn.cursor()
        output = []
        form = request.form
        s_ids = form.getlist("s_id")
        for s_id in s_ids:
            cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id))
            song = cursor.fetchone()
            if (song != None):
                song = song[0]
            cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id))
            artist = cursor.fetchone()
            if (artist != None):
                artist = artist[0]
            cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id))
            url = cursor.fetchone()
            if (url != None):
                url = url[0]
            song_info = {}
            song_info["name"] = song
            song_info["artist"] = artist
            song_info["url"] = url
            song_info["s_id"] = s_id
            song_info_json = json.loads(json.dumps(song_info))
            output.append(song_info_json)
        return insertUserPlaylist(output)

@app.route('/profile', methods=['GET','POST'])
def profile():
    if (current_user.is_authenticated):
        weather = getWeather()
        picURL = ""
        temp = getTemperature()
        message = ""
        if (weather == "Thunderstorm"):
            message = "It is thunderstorming right now."
            picURL = "https://banner.kisspng.com/20180316/grw/kisspng-thunderstorm-lightning-weather-clip-art-thunderstorm-cliparts-5aab4faa3b4bc4.2637266215211764902429.jpg"
        if (weather == "Drizzle"):
            message = "It is drizzling right now."
            picURL = "http://clipart-library.com/image_gallery/177131.png"
        if (weather == "Rain"):
            message = "It is raining right now."
            picURL = "http://www.clker.com/cliparts/w/F/h/x/4/3/rain-cloud-hi.png"
        if (weather == "Snow"):
            message = "It is snowing right now."
            picURL = "http://images.clipartpanda.com/snow-clipart-snow-leopard-clipart-830x830.png"
        if (weather == "Clear"):
            message = "It is clear right now."
            picURL = "http://www.clker.com/cliparts/E/m/H/T/6/Z/weather-clear-md.png"
        if (weather == "Clouds"):
            message = "It is cloudy right now."
            picURL = "http://worldartsme.com/images/its-cloudy-clipart-1.jpg"
        if (weather == "Extreme"):
            message = "The weather is extreme right now."
            picURL = "http://images.clipartpanda.com/tornado-clip-art-ncEyjGBai.png"
        userPlaylists = getUserPlaylists(current_user.username)
        if userPlaylists == -1:
            return redirect(url_for('index'))#404 page
        return render_template('profile.html', userPlaylists=userPlaylists, message=message, picURL = picURL, temp = temp)
    else:
        return redirect(url_for('index'))

@app.route('/addfriendbyusername', methods=['GET', 'POST'])
def addfriendbyusername():
    if request.method == 'GET':
        return redirect(url_for("index"))
    else:
        form = request.form
        friendUsername = form["friendUsername"]
        addFriends(current_user.username, friendUsername)
        return redirect(url_for("profile"))

@app.route('/friendsplaylists', methods=['GET', 'POST'])
def friendsplaylists():
    if (current_user.is_authenticated):
        weather = getWeather()
        picURL = ""
        temp = getTemperature()
        message = ""
        if (weather == "Thunderstorm"):
            message = "It is thunderstorming right now."
            picURL = "https://banner.kisspng.com/20180316/grw/kisspng-thunderstorm-lightning-weather-clip-art-thunderstorm-cliparts-5aab4faa3b4bc4.2637266215211764902429.jpg"
        if (weather == "Drizzle"):
            message = "It is drizzling right now."
            picURL = "http://clipart-library.com/image_gallery/177131.png"
        if (weather == "Rain"):
            message = "It is raining right now."
            picURL = "http://www.clker.com/cliparts/w/F/h/x/4/3/rain-cloud-hi.png"
        if (weather == "Snow"):
            message = "It is snowing right now."
            picURL = "http://images.clipartpanda.com/snow-clipart-snow-leopard-clipart-830x830.png"
        if (weather == "Clear"):
            message = "It is clear right now."
            picURL = "http://www.clker.com/cliparts/E/m/H/T/6/Z/weather-clear-md.png"
        if (weather == "Clouds"):
            message = "It is cloudy right now."
            picURL = "http://worldartsme.com/images/its-cloudy-clipart-1.jpg"
        if (weather == "Extreme"):
            message = "The weather is extreme right now."
            picURL = "http://images.clipartpanda.com/tornado-clip-art-ncEyjGBai.png"
        friendsplaylists = findFriends(current_user.username)
        print(friendsplaylists)
        if (friendsplaylists == -1):
            return redirect(url_for('index'))#404 page
        print(friendsplaylists)
        if (friendsplaylists == []):
            noFriendsMessage = "You do not have any friends right now."
            return render_template("friends.html", friendsPlaylist=friendsplaylists, message=message, picURL = picURL, temp = temp, noFriendsMessage = noFriendsMessage)
        if (friendsplaylists == [[]]):
            noFriendsMessage = "Your friends do not have any playlists generated."
            return render_template("friends.html", friendsPlaylist=friendsplaylists, message=message, picURL = picURL, temp = temp, noFriendsMessage = noFriendsMessage)
        noFriendsMessage = "You Have Friends"
        return render_template("friends.html", friendsPlaylist=friendsplaylists, message=message, picURL = picURL, temp = temp, noFriendsMessage = noFriendsMessage)
    else:
        return redirect(url_for('index'))#404 page
        
@app.route('/deleteplaylist', methods=['GET','POST'])
def deleteplaylist():
    if request.method == 'GET':
        return redirect(url_for('index.html'))
    if request.method == 'POST':
        p_id = request.form['p_id']
        if p_id is None:
            return redirect(url_for('index'))#404 page
        returnType = deletePlaylist(p_id)
        if returnType == -1:
            return redirect(url_for('index'))#404 page
        return redirect(url_for('profile'))
    else:
        return -1

@app.route('/deletesongs', methods=['GET','POST'])
def deletesongs():
    if request.method == 'GET':
        return redirect(url_for('index.html'))
    if request.method == 'POST':
        form = request.form
        if form is None:
            return redirect(url_for('index'))#404 page
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        songs = viewPlaylist(p_id)
        if songs == -1:
            return redirect(url_for('index'))#404 page
        return render_template('delete.html', songs=songs, p_id=p_id)

@app.route('/addsongs', methods=['GET','POST'])
def addsongs():
    if request.method == 'GET':
        return redirect(url_for('index.html'))
    if request.method == 'POST':
        form = request.form
        if form is None:
            return redirect(url_for('index'))#404 page
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        keyword = form["keyword"]
        if keyword is None:
            return redirect(url_for('index'))#404 page
        addToSaved(p_id, keyword)
        if addToSaved == -1:
            return redirect(url_for('index'))#404 page
        return redirect(url_for('profile'))
    else:
        return -1

@app.route('/addfrommaster', methods=["GET", "POST"])
def addfrommaster():
    if request.method == "GET":
        return redirect(url_for('index'))
    if request.method == "POST":
        form = request.form
        p_id = form["p_id"]
        sid_list = form.getlist("s_id")
        keyword = form["keyword"]
        songs = loadMasterPlaylist(keyword, sid_list)
        return render_template('add.html', songs=songs, p_id=p_id, keyword=keyword)

@app.route('/addfrommastercommit', methods=['GET','POST'])
def addfrommastercommit():
    if request.method == "GET":
        return redirect(url_for('index'))
    if request.method == "POST":
        form = request.form
        if form is None:
            return redirect(url_for('index'))#404 page
        sid_list = form.getlist("s_id")
        if sid_list is None:
            return redirect(url_for('index'))#404 page
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        keyword = form["keyword"]
        response = addMultipleToSaved(p_id, keyword, sid_list)
        if response == -1:
            return redirect(url_for('index'))#404 page
        print(p_id)
        return redirect(url_for('profile'))
    
@app.route('/deletesongscommit', methods=['GET','POST'])
def deletesongscommit():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        form = request.form
        if form is None:
            return redirect(url_for('index'))#404 page
        sid_list = form.getlist("s_id")
        if sid_list is None:
            return redirect(url_for('index'))#404 page
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))#404 page
        response = deleteFromSaved(p_id, sid_list)
        if response == -1:
            return redirect(url_for('index'))#404 page
        print(p_id)
        return redirect(url_for('profile'))

#add some sort of check for oh this user already exists, or please put in a password, please put in an email (don't leave blank)
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    form = request.form
    if form is None:
        return redirect(url_for('index'))#404 page
    username = form['username']
    if username is None:
        return redirect(url_for('login'))
    password = form['password']
    print(filterUsername(username, password))
    if filterUsername(username, password) == -1:
        return redirect(url_for('register'))
    else:
        print("shouldnt be in here u dumbfuk")
        check = User.query.filter_by(username = username).first()
        if (check is not None):
            print("in here!")
            message = "This username already exists. Try again"
            flash ("This username already exists. Try again", 'error')
            return render_template('register.html', message=message)
        else:
            if password is None:
                return redirect(url_for('login'))
            user = User(username, password, 0)
            if user is None:
                return redirect(url_for('login'))
            db.session.add(user)
            db.session.commit()
            flash('User successfully registered')
            return redirect(url_for('login'))
 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    if username is None:
        return redirect(url_for('login'))
    if password is None:
        return redirect(url_for('login')) 
    registered_user = User.query.filter_by(username=username, password=password).first()
    print(registered_user)
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    else:
        login_user(registered_user)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))

#are you sure you want to logout???
@app.route('/logout')
def logout():
    logout_user()
    session["user"] = None
    return redirect(url_for('index')) 

def getLocation():
    url = "http://ipinfo.io/"
    results = requests.get(url).json()
    if results is None:
        return -1
    city = results["city"]
    return city

#check to make sure that tag isnt null 
def getLocationSongs(length):
    tag = getLocation()
    if tag == -1:
        return -1
    return getSongs(tag, length)

def getWeather():
    city = getLocation()
    if city == -1:
        return -1
    url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&APPID=537eb84d28d1b2075c6e44b37f511b10"
    requested = urllib2.urlopen(url)
    if requested is None:
        return -1
    result = requested.read()
    r = json.loads(result)
    weather = r["weather"][0]["main"]
    print("weather" + weather)
    return weather

def getTemperature():
    city = getLocation()
    apiURL = "http://api.openweathermap.org"
    units = "units=imperial"
    API_KEY = "APPID=537eb84d28d1b2075c6e44b37f511b10"
    if (city == -1):
        return -1
    url = apiURL + "/data/2.5/weather?q="+city+"&"+units+"&"+API_KEY
    requested = urllib2.urlopen(url)
    if requested is None:
        return -1
    result = requested.read()
    r = json.loads(result)
    temperature = r["main"]["temp"]
    intTemp = int(round(temperature))
    return intTemp
    
#check to make sure that tag isnt null
def getWeatherSongs(length):
    tag = getWeather()
    if tag == -1:
        return -1
    return getSongs(tag, length)

def getSpotifySongs(results):
    if (results != None):
        psongs = {}
        for playlist in results["playlists"]["items"]:
            if (playlist["id"] != None):
                playlistid = playlist["id"]
            else:
                playlistid = "PlaylistID does not exist"
            if (playlist["owner"]["id"] != None and ',' not in playlist["owner"]["id"]):
                playlistuser = playlist["owner"]["id"]
            else:
                continue
            if ((playlistid != "PlaylistID does not exist") and (playlistid != "PlaylistUser does not exist")):
                psongs = sp.user_playlist_tracks(user = playlistuser, playlist_id = playlistid)
            else:
                continue
        return psongs
    else:
        return -1    

def createSpotifySongObjects(psongs):
    songlist = []
    if (psongs != None):
        for tInfo in psongs["items"]:
            if (tInfo != None):
                if (tInfo["track"] != None):
                    song = {}
                    if (tInfo["track"]["name"] != None):
                        song["name"] = tInfo["track"]["name"]
                    else:
                        song["name"] = "No Name Exists"
                    if (tInfo["track"]["artists"][0]["name"] != None):
                        song["artist"] = tInfo["track"]["artists"][0]["name"]
                    else:
                        song["artist"] = "No Artist Exists"
                    if (tInfo["track"]["preview_url"] != None):
                        song["url"] = tInfo["track"]["preview_url"]
                    else:
                        song["url"] = "No URL Exists"
                    if (song["url"] != "No URL Exists"):
                    # print("song: " + tInfo["track"]["name"])
                    # print("artist: " + tInfo["track"]["artists"][0]["name"])
                    # print("url:" + tInfo["track"]["preview_url"])
                        songlist.append(song)
        return songlist
    else:
        return -1

def createLastFMSongs(r):
    if (r != None):
        songlist = []
        for song in r["tracks"]["track"]:
            if (song != None):
                try:
                    results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
                except spotipy.client.SpotifyException, e:
                    continue
                if (results["tracks"]["items"] != []):
                    Nsong = {}
                    if (song["name"] != None):
                        Nsong["name"] = song["name"]
                    else:
                        Nsong["name"] = "Name Does Not Exist"
                    if (song["artist"]["name"] != None):
                        Nsong["artist"] = song["artist"]["name"]
                    else:
                        Nsong["artist"] = "Artist Does Not Exist"
                    if (results["tracks"]["items"][0]["preview_url"] != None):
                        Nsong["url"] = results["tracks"]["items"][0]["preview_url"]
                    else:
                        Nsong["url"] = "URL Does Not Exist"
                      #  print("url does not exist")
                    if ((Nsong["name"] != "Name Does Not Exist") and
                        (Nsong["artist"] != "Artist Does Not Exist") and
                        (Nsong["url"] != "URL Does Not Exist")):
                      #  print("everything ok")
                        songlist.append(Nsong)
        return songlist
    else:
        return -1
    
#generate random songs based on a random theme
def getRandomSongs(length):
    artists = ["Bob Marley", "Madonna", "The Beatles", "Elvis Presley", 
                   "Mariah Carey", "Stevie Wonder", "The Rolling Stones", "Paul McCartney",
                   "Rihanna", "Usher", "Marvin Gaye", "Katy Perry", "Billy Joel", 
                   "The Beach Boys", "Taylor Swift", "Carpenters", "Beyonce",
                   "Cher", "Maroon 5", "Bon Jovi", "P!nk", "Ray Charles", "Bruno Mars",
                   "Chris Brown", "Lady Gaga", "Nelly", "Bobby Darin",
                   "Paula Abdul", "Alicia Keys", "Kelly Clarkson",
                   "Destiny's Child", "Eminem", "JAY-Z", "Kanye West", "Justin Timberlake",
                   "Bruce Springsteen"]
    currentPopularArtists = ["Cardi B", "Drake", "Imagine Dragons", "Ed Sheeran", 
                             "The Weeknd", "Post Malone", "Kendrick Lamar", "Nicki Minaj",
                             "BTS", "Camila Cabello", "Bruno Mars", "Kane Brown", 
                             "Dua Lipa", "Carrie Underwood", "Maroon 5", "Florida Georgia Line", 
                             "Pentatonix", "Taylor Swift", "Halsey", "Thomas Rhett", 
                             "Justin Timberlake", "Demi Lovato", "P!nk", "Blake Shelton",
                             "Khalid", "Charlie Puth", "Portugal. The Man", "Eminem",
                             "Rihanna", "Meghan Trainor", "Lil Dicky", "Chris Brown",
                             "Logic", "Zedd", "Beyonce", "Adele", 
                             "twenty one pilots", "The Chainsmokers", "Linkin Park", "Justin Bieber",
                             "Niall Horan", "Sam Hunt", "Sam Smith", "Foster The People",
                             "DJ Khaled"]
    instrumentalArtists = ["Chopin", "Beethoven", "Mozart", "Debussy",
                        "Yiruma", "Vivaldi", "Mahler", "Stravinsky",
                        "Brian Crain", "Maurice Ravel", "Alex Christensen", "Schiller",
                        "Juliana", "Rebour", "Oneke", "Elba",
                        "Charlie Key", "Hushed"]
    countryArtists = ["Carrie Underwood", "George Strait", "Merle Haggard", "Willie Nelson",
                      "Alabama", "Alan Jackson", "Tim McGraw", "Buck Owens",
                      "Johnny Cash", "Kenny Rogers", "Dolly Parton", "Toby Keith",
                      "Randy Travis", "Ray Price", "Rascal Flatts", "Keith Urban",
                      "The Judds", "Blake Shelton", "Faith Hill",
                      "Lynn Anderson", "Charlie Rich", "Connie Smith", "Sugarland",
                      "Tracy Lawrence", "Sawyer Brown", "Lonestar", "Eric Church",
                      "Clay Walker", "Miranda Lambert"]
    rockArtists = ["Led Zeppelin", "The Beatles", "AC/DC", "Aerosmith", "Red Hot Chili Peppers",
                    "The Rolling Stones", "Pink Floyd", "The Who", "Fleetwood Mac", "Lynyrd Skynyrd",
                    "U2", "Radiohead", "Nirvana", "Green Day", "The Class", "Queen", "Black Sabbath",
                    "Ramones", "Creedence Clearwater Revival", "The Allman Brothers", "Pearl Jam", 
                    "The Kinks", "Foo Fighters", "ZZ Top", "Eagles", "The Doors", "Van Halen",
                    "Bon Jovi", "Def Leppard", "Rush", "R.E.M", "Dire Straits", "Talking Heads",
                    "The Police", "The Cure", "The Smashing Pumpkins", "Rage Against the Machine",
                    "Deep Purple", "Bob Seger", "The Monkees", "The Zombies", "The Everly Brothers", 
                    "Elton John", "Elvis Presley"]
    hipHopArtists = ["Beastie Boys", "A Tribe Called Quest", "Wu-Tang Clan","Public Enemy", 
                    "Run-D.M.C", "OutKast", "N.W.A", "The Roots", "Cypress Hill", "Salt-N-Pepa", 
                    "Bone Thugs-N-Harmony", "21 Savage", "2 Chainz", "Action Bronson", "Akon", 
                    "A$AP Ferg", "A$AP Rocky", "B.o.B", "Chance the Rapper" , "Chris Brown", 
                    "Coolio", "Dr. Dre", "Desiigner", "Eminem", "Flo Rida", "G-Eazy", "Ghostface Killah", 
                    "Gucci Mane", "Iggy Azalea", "Ice Cube", "J-Kwon", "J.Cole", "Jay Z", "Jeremih",
                    "Kanye West", "Kendrick Lamar", "Kid Cudi", "Kodak Black", "Lauryn Hill", "Lil Jon",
                    "LL Cool J", "Lil Uzi Vert", "Lil Wayne", "Lupe Fiasco", "Mac Miller", "Machine Gun Kelly",
                    "Meek Mill", "Nas", "Nicki Minaj", "Omarion", "Pitbull", "Post Malone", "Queen Latifah",
                    "Raekwon", "Queen Latifah", "Snoop Dogg", "Sean Paul", "SZA", "Timbaland", "Travis Scott",
                    "Tupac Shakur", "Ty Dolla Sign", "Vince Staples", "Waka Flocka Flame", "Wyclef Jean"]
    metalArtists = ["Metallica", "Judas Priest", "Slayer", "Pantera", "Megadeth", "Iron Maiden", 
                    "Slipknot", "Korn", "Sepultura", "System Of A Down", "Lamb Of God", "Mastodon", "Anthrax",
                    "Cannibal Corpse", "Disturbed", "Rammstein", "Alice in Chains", "Savatage", "Overkill",
                    "Napalm Death", "Dream Theater", "Darkthrone"]
    rnbArtists = ["Sly & the Family Stone", "Four Tops", "Gladys Knight & the Pips", "Chic", "The Temptations",
                    "Boyz II Men", "The Supremes", "The Miracles", "The Jackson 5", "The O'Jays", "Ohio Players",
                    "New Edition", "TLC", "The Pointer Sisters", "Blackstreet", "Commodores", "The Spinners", 
                    "The Drifters", "The Stylistics", "Sam & Dave", "The Whispers", "The Platters", "The Isley Brothers",
                    "Earth, Wind & Fire", "Prince", "Michael Jackson", "Stevie Wonder", "Whitney Houston", 
                    "Janet Jackson", "John Legend", "Aaliyah", "Marvin Gaye", "Erykah Badu", "Aretha Franklin", 
                    "Babyface", "Chaka Khan", "Ray Charles", "Otis Redding", "Etta James", "Jill Scott", 
                    "Maxwell", "Tina Turner", "Sam Cooke", "Al Green", "Anita Baker", "Donny Hathaway", "Isaac Hayes",
                    "Barry White", "Patti LaBelle", "Diana Ross", "Luther Vandross", "Curtis Mayfield", "Lionel Richie",
                    "Bill Withers", "James Brown", "Smokey Robinson"]
            
    selectedPlaylistNum = random.randint(0, 7)
    if selectedPlaylistNum == 0:
        artistLength = len(artists)
        selectedArtist = []
        selectedArtistSongs = []
        finalArray0 = []
        for x in range(5):
            selectedArtist.append(artists[random.randint(0, artistLength - 1)])
        if not selectedArtist:
            print("list is empty")
        for song in selectedArtist:
            print(song)
            selectedArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedArtistSongs)
            print(finalLength)
            finalArray0.append(selectedArtistSongs[random.randint(0, finalLength)])
        if not selectedArtistSongs:
            print("list is empty")
        return finalArray0
    elif selectedPlaylistNum == 1:
        popularArtistLength = len(currentPopularArtists)
        selectedPopularArtist = []
        selectedPopularArtistSongs = []
        finalArray1 = []
        for x in range(5):
            selectedPopularArtist.append(currentPopularArtists[random.randint(0, popularArtistLength - 1)])
        if not selectedPopularArtist:
            print("list is empty")
        for song in selectedPopularArtist:
            print(song)
            selectedPopularArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedPopularArtistSongs)
            print(finalLength)
            finalArray1.append(selectedPopularArtistSongs[random.randint(0, finalLength )])
        if not selectedPopularArtistSongs:
            print("list is empty")
        return finalArray1
    elif selectedPlaylistNum == 2:
        instrumentalArtistLength = len(instrumentalArtists)
        selectedInstrumentalArtist = []
        selectedInstrumentalArtistSongs = []
        finalArray2 = []
        for x in range(5):
            selectedInstrumentalArtist.append(instrumentalArtists[random.randint(0, instrumentalArtistLength - 1)])
        if not selectedInstrumentalArtist:
            print("list is empty")
        for song in selectedInstrumentalArtist:
            print(song)
            selectedInstrumentalArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedInstrumentalArtistSongs)
            print(finalLength)
            finalArray2.append(selectedInstrumentalArtistSongs[random.randint(0, finalLength  )])
        if not selectedInstrumentalArtistSongs:
            print("list is empty")
        return finalArray2
    elif selectedPlaylistNum == 3:
        countryArtistLength = len(countryArtists)
        selectedCountryArtist = []
        selectedCountryArtistSongs = []
        finalArray = []
        for x in range(5):
            selectedCountryArtist.append(countryArtists[random.randint(0, countryArtistLength - 1)])
        if not selectedCountryArtist:
            print("list is empty")
        for song in selectedCountryArtist:
            print(song)
            selectedCountryArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedCountryArtistSongs)
            print(finalLength)
            finalArray.append(selectedCountryArtistSongs[random.randint(0, finalLength  )])
        if not selectedCountryArtistSongs:
            print("list is empty")
        return finalArray
    elif selectedPlaylistNum == 4:
        rockArtistLength = len(rockArtists)
        selectedRockArtist = []
        selectedRockArtistSongs = []
        finalArray = []
        for x in range(5):
            selectedRockArtist.append(rockArtists[random.randint(0, rockArtistLength - 1)])
        if not selectedRockArtist:
            print("list is empty")
        for song in selectedRockArtist:
            print(song)
            selectedRockArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedRockArtistSongs)
            print(finalLength)
            finalArray.append(selectedRockArtistSongs[random.randint(0, finalLength )])
        if not selectedRockArtistSongs:
            print("list is empty")
        return finalArray
    elif selectedPlaylistNum == 5:
        hipArtistLength = len(hipHopArtists)
        selectedHipArtist = []
        selectedHipArtistSongs = []
        finalArray = []
        for x in range(5):
            selectedHipArtist.append(hipHopArtists[random.randint(0, hipArtistLength - 1)])
        if not selectedHipArtist:
            print("list is empty")
        for song in selectedHipArtist:
            print(song)
            selectedHipArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedHipArtistSongs)
            print(finalLength)
            finalArray.append(selectedHipArtistSongs[random.randint(0, finalLength )])
        if not selectedHipArtistSongs:
            print("list is empty")
        return finalArray
    elif selectedPlaylistNum == 6:
        metalArtistLength = len(metalArtists)
        selectedMetalArtist = []
        selectedMetalArtistSongs = []
        finalArray = []
        for x in range(5):
            selectedMetalArtist.append(metalArtists[random.randint(0, metalArtistLength - 1)])
        if not selectedMetalArtist:
            print("list is empty")
        for song in selectedMetalArtist:
            print(song)
            selectedMetalArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedMetalArtistSongs)
            print(finalLength)
            finalArray.append(selectedMetalArtistSongs[random.randint(0, finalLength  )])
        if not selectedMetalArtistSongs:
            print("list is empty")
        return finalArray
    elif selectedPlaylistNum == 7:
        rnbArtistLength = len(rnbArtists)
        selectedRnbArtist = []
        selectedRnbArtistSongs = []
        finalArray = []
        for x in range(5):
            selectedRnbArtist.append(rnbArtists[random.randint(0, rnbArtistLength - 1)])
        if not selectedRnbArtist:
            print("list is empty")
        for song in selectedRnbArtist:
            print(song)
            selectedRnbArtistSongs.extend(getSongs(song, length))
        for x in range(length):
            finalLength = len(selectedRnbArtistSongs)
            print(finalLength)
            finalArray.append(selectedRnbArtistSongs[random.randint(0, finalLength  )])
        if not selectedRnbArtistSongs:
            print("list is empty")
        return finalArray
    else:
        print("error")
        return -1

def getMasterList(tag):
    songlist = []
    songCounter = 0
    sOffset = 0
    while (songCounter < 200):
        results = sp.search(q = tag, limit = 2, offset = sOffset, type = 'playlist')
        if (results != None):
            psongs = getSpotifySongs(results)
            if (psongs == -1):
                continue
            else:
                sOffset += 2
                if (psongs != {}):
                    songlist = createSpotifySongObjects(psongs)
                    if (songlist == -1):
                        continue
                    else:
                        songCounter += len(songlist)
    url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json&limit=200"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    #check to make sure that the r isnt null
    if r != None:
        lastFMSongList = createLastFMSongs(r)
        if (lastFMSongList != -1):
            songlist.extend(lastFMSongList)
            return songlist
        else:
            return -1
    else:
        return -1            

def viewPlaylist(p_id):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    songList = []
    s_id_arr = []
    rows_count = cursor.execute("SELECT s_id FROM Playlist WHERE p_id ="+p_id)
    if rows_count == 0:
        print ("No such s_id")
        return -1
    sid = cursor.fetchone()
    while (sid != None):
        s_id_arr.append(sid)
        sid = cursor.fetchone()
    output = []
    for s_id in s_id_arr:
        rows_count = cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id[0]))
        if rows_count == 0:
            print ("No such song")
            return -1
        song = cursor.fetchone()
        if (song != None):
            song = song[0]
        else:
            print("Couldn't retrieve song")
        rows_count1 = cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
        if rows_count1 == 0:
            print ("No such artist")
            return -1
        artist = cursor.fetchone()
        if (artist != None):
            artist = artist[0]
        else:
            print("Couldn't retrieve artist")
        rows_count2 = cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
        if rows_count2 == 0:
            print ("No such artist")
            return -1
        url = cursor.fetchone()
        if (url != None):
            url = url[0]
        else:
            print("Couldn't retrieve url")
        song_info = {}
        song_info["name"] = song
        song_info["artist"] = artist
        song_info["url"] = url
        song_info["s_id"] = s_id[0]
        song_info_json = json.loads(json.dumps(song_info))
        output.append(song_info_json)
    return output

def deletePlaylist(p_id):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    if current_user.is_authenticated:
        cursor.execute("DELETE FROM Playlist WHERE p_id ="+p_id)
        cursor.execute("DELETE FROM users WHERE p_id = "+p_id)
        conn.commit()
    cursor.execute("SELECT * FROM Playlist WHERE p_id ="+p_id)
    checkPlaylist = cursor.fetchone()
    if (checkPlaylist != None):
        return -1
    cursor.execute("SELECT * FROM users WHERE p_id ="+p_id)
    checkUsers = cursor.fetchone()
    if (checkUsers != None):
        return -1
    else:
        return 0

def getRandomSIDs(cursor, tag, length):
    s_id_arr = []
    cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+tag+'"')
    sid = cursor.fetchone()
    if (sid == None):
        return -1
    else:
        while (sid != None):
            s_id_arr.append(sid)
            sid = cursor.fetchone()
        if (len(s_id_arr) < int(length)):
            return render_template("index.html", message = "You requested for too many songs. The maximum number of songs for this category is " + str(len(s_id_arr)))
        print(int(length))
        randomList = random.sample(s_id_arr, int(length))
        if (len(randomList) == int(length)):
            return randomList
        else:
            return getRandomSIDs(cursor, tag, length)

# Inserts the song into the playlist database
def insertUserPlaylist(output):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    if current_user.is_authenticated:
        username = current_user.username
        if (username == None):
            return redirect(url_for('index'))
        cursor.execute("SELECT p_id FROM users WHERE username = "+'"'+username+'"')
        numPlaylists = len(cursor.fetchall())
        keyword = username + str(numPlaylists) 
        pID = abs(hash(keyword)) % (10 ** 8)
        user = User(username, "0", pID)
        db.session.add(user)
        db.session.commit()
        cursor.execute("SELECT * FROM users WHERE p_id ="+str(pID))
        conn.commit()
        playlistInserted = cursor.fetchone()
        if (playlistInserted == None):
            return redirect(url_for('index'))
        insertPlaylist = []
        for song in output:
            if ((song["name"] != None) and (song["artist"] != None)):
                songName = song["name"]
                songArtist = song["artist"]
                songID = abs(hash(songName+songArtist)) % (10 ** 8)
                playlistTuple = (pID, songID, session["keyword"])
                insertPlaylist.append(playlistTuple)
        cursor.executemany("INSERT INTO Playlist VALUES (?,?,?)", insertPlaylist)
        conn.commit()
        for song in output:
            if ((song["name"] != None) and (song["artist"] != None)):
                songName = song["name"]
                songArtist = song["artist"]
                songID = abs(hash(songName+songArtist)) % (10 ** 8)
                cursor.execute("SELECT * FROM Playlist WHERE p_id="+str(pID)+" AND s_id="+str(songID))
                songInserted = cursor.fetchone()
                print(songInserted)
                if (songInserted == None):
                    return redirect(url_for(index))
        session["keyword"] = None
        return redirect(url_for('profile'), code = 307)
    else:
        return redirect(url_for('index'))    

def getUserPlaylists(username):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    if (cursor == None):
        print("ERROR: unable to retrieve DB info")
        return -1
    if (username == None):
        print("ERROR: unable to retrieve username to get user playlists")
        return -1
    dictList = []
    p_id_arr = []
    keywordList = []
    lengthList = []
    cursor.execute("SELECT p_id FROM Users WHERE username="+'"'+username+'"')
    p_id = cursor.fetchone()
    while (p_id != None):
        if p_id[0] != 0:
            p_id_arr.append(p_id)
        p_id = cursor.fetchone()
    print(p_id_arr)
    for pid in p_id_arr:
        cursor.execute("SELECT keyword FROM Playlist WHERE p_id ="+str(pid[0]))
        keyword = cursor.fetchone()
        if keyword == None:
            continue
        elif keyword[0] == None:
            continue
            #keywordList.append(keyword)
        else:
            keywordList.append(keyword[0].encode("ascii"))
    for pid in p_id_arr:
        cursor.execute("SELECT s_id FROM Playlist WHERE p_id ="+str(pid[0]))
        plLength = len(cursor.fetchall())
        lengthList.append(plLength)
    for index, pid in enumerate(p_id_arr):
        keywordURL = getPicture()
        if (keywordURL == -1):
            return redirect(url_for(index))#404
        dictList.append({'p_id': p_id_arr[index][0], 'keyword': keywordList[index], 'length': lengthList[index], 'username': username, 'keywordURL': keywordURL})
    return dictList
    

def createUserList(cursor, random_s_id):
    output = []   
    if (random_s_id is None or cursor is None):
        print ("ERROR: one or more input used to createUserList does not exist")
    else:
        for s_id in random_s_id:
            cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id[0]))
            song = cursor.fetchone()
            song = song[0]
            if (song == None):
                print("ERROR: something went wrong with the retrieval of song name")
            else:
                cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
                artist = cursor.fetchone()
                artist = artist[0]
                if (artist == None):
                    print("ERROR: something went wrong with the retrieval of song artist")
                else:
                    cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
                    url = cursor.fetchone()
                    url = url[0]
                    if (url == None):
                        print("ERROR: something went wrong with the retrieval of song url")
                    else:
                        song_info = {}
                        song_info["name"] = song
                        song_info["artist"] = artist
                        song_info["url"] = url
                        song_info["s_id"] = s_id[0]
                        song_info_json = json.loads(json.dumps(song_info))
                        output.append(song_info_json)
        if (output is None):
            print("ERROR: not able to retrieve the song information of the inputted list")
            return -1
    return output

def getSongs(tag,length):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    cursor.execute("SELECT keyword FROM masterPlaylist WHERE keyword ="+'"'+tag+'"')
    if (tag == None):
        print("ERROR: tag to getSongs does not exist")
        return -1
    if (length == None):
        print("ERROR: no length specified")
        return -1
    else:
        if (cursor.fetchone() == None):
            songlist = getMasterList(tag)
            if (songlist == -1):
                print("ERROR: unable to retrieve Master List")
                return -1
            else:
                ret = insertDBMaster(songlist, tag)
                if (ret == -1):
                    print("ERROR: unable to insert into Master")
                    return -1
                conn.commit()
        random_SIDs = getRandomSIDs(cursor, tag, length)
        if (random_SIDs == -1):
            print("ERROR: unable to get Random SIDS")
            return -1
        if type(random_SIDs) != list:
            return random_SIDs
        output = createUserList(cursor, random_SIDs) 
        if (output == -1):
            print("ERROR: unable to create User List")
            return -1
        else:  
            session["keyword"] = tag
            return output

def exportSpotify(pID, keyword, username):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    trackURIs = []
    if (pID == None):
        print("ERROR: playlist id to export doesn't exist")
        return -1
    if (keyword == None):
        print("ERROR: keyword of exporting playlist doesn't exist")
        return -1
    if (username == None):
        print("ERROR: Spotify username doesn't exist")
        return -1
    else:
        for row in cursor.execute("Select Song.name, Song.artist FROM Song, Playlist WHERE Playlist.s_id = Song.s_id AND Playlist.p_id = " + str(pID)):
            results = sp.search(q='track:' + row[0] + ' artist:' + row[1], type='track', limit=1)
            if (results["tracks"]["items"][0] != None):
                trackURI = results["tracks"]["items"][0]["uri"]
                trackURIs.append(trackURI)

        scope = 'playlist-modify-private'
        
        token = util.prompt_for_user_token(username, scope = scope, client_id = '0b4d677f62e140ee8532bed91951ae52', client_secret = 'cc1e617a9c064aa982e8eeaf65626a94', redirect_uri = 'http://localhost:3000/callback')
        if token:
            uSpot = spotipy.Spotify(auth=token)
            playlist = uSpot.user_playlist_create(username, keyword, public = False)
            result = uSpot.user_playlist_add_tracks(username, playlist["id"], trackURIs)
        else:
            print("unable to retrieve token")
            return -1
        return redirect(url_for('profile'))

def deleteFromSaved(pid, songsToDelete):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    if (pid == None):
        print("ERROR: pid to deleteFromSaved does not exist")
        return -1
    if (songsToDelete == None):
        print("ERROR: songs to deleteFromSaved does not exist")
        return -1
    else:
        for s_id in songsToDelete:
            cursor.execute('Delete FROM Playlist WHERE p_id =' + str(pid) + " AND s_id = " + str(s_id))
            conn.commit()
            cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(pid) + " AND s_id =" + str(s_id))
            if (cursor.fetchone() != None):
                print("ERROR: did not successfully delete song from desired playlist")
                return -1
    return redirect(url_for('profile'))

def addMultipleToSaved(pid, keyword, songsToAdd):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    if (pid == None):
        print("ERROR: pid to addMultipleToSaved does not exist")
        return -1
    if (songsToAdd == None):
        print("ERROR: songs to addMultipleToSaved does not exist")
        return -1
    else:
        for s_id in songsToAdd:
            playlistT = (pid, s_id, keyword)
            cursor.execute("INSERT INTO Playlist VALUES (?,?,?)", playlistT)
            print("inserting")
            conn.commit()
            cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(pid) + " AND s_id =" + str(s_id))
            if (cursor.fetchone() == None):
                print("ERROR: did not successfully insert song to desired playlist")
                return -1
        return redirect(url_for('profile'))
    
def addToSaved(pid,keyword):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    playlistT = ()
    if (pid == None):
        print("ERROR: pid to addToSaved does not exist")
        return -1
    if (keyword == None):
        print("ERROR: keyword to addToSaved does not exist")
        return -1
    if (cursor == None):
        print("ERROR: no connection to DB")
        return -1
    else:
        while (playlistT == ()):
            rows_count0 = cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+keyword+'"')
            if rows_count0 == 0:
                print ("No such artist")
                return -1
            sids = cursor.fetchall()
            if not sids:
                return -1
            sid = random.choice(sids)[0]
            if (sid == None):
                print("ERROR: relevant sid unable to be found")
            rows_count = cursor.execute("SELECT Playlist.s_id FROM Playlist WHERE Playlist.p_id =  " + str(pid) + " AND Playlist.s_id = " + str(sid))
            if rows_count == 0:
                print ("No such s_id")
                return -1
            playlistsid = cursor.fetchone()
            if (playlistsid == None):
                playlistT = (pid, sid, keyword)

        cursor.execute("INSERT INTO Playlist VALUES (?,?,?)", playlistT)
        print("inserting")
        conn.commit()
        rows_count = cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(playlistT[0]) + " AND s_id = " + str(playlistT[1]) + " AND keyword = " +'"'+ str(playlistT[2]) + '"')
        if rows_count == 0:
            print ("No such playlist")
            return -1
        if (cursor.fetchone() == None):
            print("ERROR: unable to insert new song into playlist")
            return -1
        return redirect(url_for('profile'))

def loadMasterPlaylist(keyword, currentSIDs):
    output = []
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor == None):
        print ("ERROR opening cursor to database")
    cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+keyword+'"')
    sids = cursor.fetchall()
    for sid in sids:
        if str(sid[0]) not in currentSIDs:
            rows_count0 = cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(sid[0]))
            if rows_count0 == 0:
                print ("No such artist")
                return -1
            song = cursor.fetchone()
            if (song != None):
                song = song[0]
            else:
                print("Song name not retrieved")
            rows_count = cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(sid[0]))
            if rows_count == 0:
                print ("No such artist")
                return -1
            artist = cursor.fetchone()
            if (artist != None):
                artist = artist[0]
            else:
                print("Song artist not retrieved")
            rows_count1 = cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(sid[0]))
            if rows_count1 == 0:
                print ("No such url")
                return -1
            url = cursor.fetchone()
            if (url != None):
                url = url[0]
            else:
                print("Song url not retrieved")
            song_info = {}
            song_info["name"] = song
            song_info["artist"] = artist
            song_info["url"] = url
            song_info["s_id"] = sid[0]
            song_info_json = json.loads(json.dumps(song_info))
            output.append(song_info_json)
    if (output is None):
        print("ERROR: not able to retrieve the song information of the inputted list")
        return -1
    return output

def addFriends(username, friendUsername):
    if not username:
        return -1
    if not friendUsername:
        return -1
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if (cursor is None):
        print ("ERROR opening cursor to database")
    rows_count = cursor.execute("SELECT * FROM Friends WHERE friend="+'"'+friendUsername+'"') 
    conn.commit()  
    if rows_count == 0:
        print ("No such friend")
        return -1
    else:
        cursor.execute("INSERT INTO Friends VALUES (?,?)", (username, friendUsername))
        conn.commit()
        return friendUsername

def findFriends(username):
    if not username:
        print ("no username")
        return -1
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if cursor is None:
        print("cursor none")
        return -1
    friendPlaylist = []
    if (cursor == None):
        print ("ERROR opening cursor to database")
    cursor.execute("SELECT Friends.friend FROM Friends WHERE myUsername="+'"'+username+'"')
    friends = cursor.fetchall()
    if not friends:
        print("no friends")
        return []
    for friend in friends:
        newFriend = getUserPlaylists(friend[0])
        friendPlaylist.append(newFriend)
    conn.commit()
    return friendPlaylist

def getPicture():
    """
    apiURL = "https://pixabay.com/api/"
    apiKey = "8862810-93a7d872dc2914a91ddd617f6"
    url = apiURL + "?key=" + apiKey + "&q=" + keyword + "&image_type=photo"
    requested = urllib2.urlopen(url)
    if (requested is None):
        return -1
    result = requested.read()
    if (result is None):
        return -1
    r = json.loads(result)
    if (r is None):
        return -1
    picURL = r["hits"][0]["previewURL"]
    if (picURL is None):
        return -1
    """
    return "http://i0.kym-cdn.com/photos/images/facebook/001/250/498/dd3.png"
    
# This method pre-stores popular tags for emotion, location, and weather  
def init_db(): 
    db.init_app(app)
    db.app = app
    db.create_all()

if (__name__ == "__main__"):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db()
    try:
        stopDB = True
        path = os.path.dirname(os.path.abspath(__file__))
        conn = sqlite3.connect(path + '/test.db')
        cursor = conn.cursor()
        if (cursor == None):
            print ("ERROR opening cursor to database")
        cursor.execute('SELECT SQLITE_VERSION() ')
        data = cursor.fetchone()
        createPlaylist()
        cursor.execute("SELECT mp_id from masterPlaylist where keyword = 'happy'")
        if cursor.fetchone() == None:
            if stopDB:
                loadDatabases()
                stopDB = False
        print "SQLite version: %s" % data 
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='localhost', port=3000)

