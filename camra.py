from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import urllib2, json, requests, spotipy, sqlite3, os
from sqlite3 import Error
from flask_login import LoginManager, login_user, logout_user, current_user
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import sys, random
from User import User
from flask_sqlalchemy import SQLAlchemy
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

def createPlaylist():
   # conn = sqlite3.connect('test.db',  check_same_thread=False)
   # cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Song (s_id integer PRIMARY KEY, name text, artist text, url text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, keyword text, FOREIGN KEY(keyword) REFERENCES masterPlaylist(keyword), FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS masterPlaylist (mp_id integer, keyword text PRIMARY KEY, length integer, FOREIGN KEY(mp_id) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Account (a_id integer PRIMARY KEY, playlist integer, p_id integer, FOREIGN KEY(playlist) REFERENCES Playlist(p_id))''')
    conn.commit()

try:
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SQLITE_VERSION() ')
    data = cursor.fetchone()
    createPlaylist()
    print "SQLite version: %s" % data 
except sqlite3.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

@app.route("/", methods=["GET", "POST"])
def index():
    allRequests = []
    length = request.form.get("length")
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        category = form["category"]
        length = form["length"]
        mood = form["moodoption"]
        songs = []
        if (category == "location"):
            songs = getLocationSongs(length)
        elif (category == "weather"):
            songs = getWeatherSongs(length)
        elif (category == "mood"):
            songs = getSongs(mood, length)
        session["output"] = songs
    return redirect(url_for("results"), code = 307)

@app.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        return render_template('results.html', songs=session["output"])

@app.route("/viewplaylist", methods=["GET", "POST"])
def viewplaylist():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        form = request.form
        p_id = form["p_id"]
        keyword = form["keyword"]
        output = viewPlaylist(p_id)
        return render_template('view.html', songs=output, p_id=p_id, keyword=keyword)
    
@app.route("/export", methods=["GET", "POST"])
def export():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        form = request.form
        p_id = form["p_id"]
        name = form["pName"]
        username = form["sUsername"]
        return exportSpotify(p_id, name, username)

@app.route("/modify", methods=["GET", "POST"])
def modify():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        return render_template('modify.html', songs=session["output"])

@app.route("/submitmodify", methods=["GET", "POST"])
def submitmodify():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        newoutput = []
        form = request.form
        newlist = form.getlist("songnames")
        for song in session["output"]:
            if song["name"] in newlist:
                newoutput.append(song)
        session["output"] = newoutput
        return redirect(url_for("results"), code = 307)

@app.route("/save", methods=["GET", "POST"])
def save():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        return insertUserPlaylist()

@app.route('/profile', methods=['GET','POST'])
def profile():
    if request.method == 'GET':
        if (current_user.is_authenticated):
            userPlaylists = getUserPlaylists()
            return render_template('profile.html', userPlaylists=userPlaylists)
        else:
            return redirect(url_for('index'))
    else:
        userPlaylists = getUserPlaylists()
        print(userPlaylists)
        return render_template('profile.html', userPlaylists=userPlaylists)
    
@app.route('/deleteplaylist', methods=['GET','POST'])
def deleteplaylist():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        p_id = request.form['p_id']
        deletePlaylist(p_id)
        return redirect(url_for('profile'))

@app.route('/deletesongs', methods=['GET','POST'])
def deletesongs():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        form = request.form
        p_id = form["p_id"]
        songs = viewPlaylist(p_id)
        return render_template('delete.html', songs=songs, p_id=p_id)

@app.route('/addsongs', methods=['GET','POST'])
def addsongs():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        form = request.form
        p_id = form["p_id"]
        keyword = form["keyword"]
        print(p_id)
        print(keyword)
        addToSaved(p_id, keyword)
        return redirect(url_for('profile'))

@app.route('/deletesongscommit', methods=['GET','POST'])
def deletesongscommit():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        form = request.form
        sid_list = form.getlist("s_id")
        print(sid_list)
        p_id = form["p_id"]
        deleteFromSaved(p_id, sid_list)
        print(p_id)
        return redirect(url_for('profile'))

#add some sort of check for oh this user already exists, or please put in a password, please put in an email (don't leave blank)
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    form = request.form
    username = form['username']
    password = form['password']
   # check = User.query.filter_by(username = username).first()
    #print(check)
    #if (check is not None):
      #  print("in here!")
       # flash ("This username already exists. Try again", 'error')
        #return redirect(url_for('register'))
    user = User(username, password, 0)
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
    print(username)
    print(password)
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
    city = results["city"]
    return city

#check to make sure that tag isnt null 
def getLocationSongs(length):
    tag = getLocation()
    return getSongs(tag, length)

def getWeather():
    city = getLocation()
    url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&APPID=537eb84d28d1b2075c6e44b37f511b10"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    weather = r["weather"][0]["main"]
    print("weather" + weather)
    return weather

#check to make sure that tag isnt null
def getWeatherSongs(length):
    tag = getWeather()
    return getSongs(tag, length)


def getMasterList(tag):
    songlist = []
    songCounter = 0
    sOffset = 0
    
    while (songCounter < 200):
        results = sp.search(q = tag, limit = 2, offset = sOffset, type = 'playlist')

        for playlist in results["playlists"]["items"]:
            playlistid = playlist["id"]
            playlistuser = playlist["owner"]["id"]
            sOffset += 2
            psongs = sp.user_playlist_tracks(user = playlistuser, playlist_id = playlistid)
       
            for tInfo in psongs["items"]:
                song = {}
                song["name"] = tInfo["track"]["name"]
                song["artist"] = tInfo["track"]["artists"][0]["name"]
                song["url"] = tInfo["track"]["preview_url"]
                songCounter += 1
                if (song["url"] != None):
                    print("song: " + tInfo["track"]["name"])
                    print("artist: " + tInfo["track"]["artists"][0]["name"])
                    print("url:" + tInfo["track"]["preview_url"])
                    songlist.append(song)
        
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
    return songlist

def viewPlaylist(p_id):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    songList = []
    s_id_arr = []
    cursor.execute("SELECT s_id FROM Playlist WHERE p_id ="+p_id)
    sid = cursor.fetchone()
    while (sid != None):
        s_id_arr.append(sid)
        sid = cursor.fetchone()
    output = []
    for s_id in s_id_arr:
        cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id[0]))
        song = cursor.fetchone()[0]
        cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
        artist = cursor.fetchone()[0]
        cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
        url = cursor.fetchone()[0]
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
    if current_user.is_authenticated:
        cursor.execute("DELETE FROM Playlist WHERE p_id ="+p_id)
        cursor.execute("DELETE FROM users WHERE p_id = "+p_id)
        conn.commit()

def getRandomSIDs(cursor, tag, length):
    s_id_arr = []
    cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+tag+'"')
    sid = cursor.fetchone()
    while (sid != None):
        s_id_arr.append(sid)
        sid = cursor.fetchone()
    if (len(s_id_arr) < int(length)):
        return render_template("index.html", message = "You requested for too many songs. The maximum number of songs for this category is " + str(len(s_id_arr)))
    print(int(length))
    print random.sample(s_id_arr, int(length))
    return random.sample(s_id_arr, int(length))

# Inserts the song into the playlist database
def insertUserPlaylist():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    if current_user.is_authenticated:
        username = current_user.username
        cursor.execute("SELECT p_id FROM users WHERE username = "+'"'+username+'"')
        numPlaylists = len(cursor.fetchall())
        keyword = username + str(numPlaylists) 
        pID = abs(hash(keyword)) % (10 ** 8)
        user = User(username, "0", pID)
        db.session.add(user)
        db.session.commit()
        insertPlaylist = []
        for song in session["output"]:
            songName = song["name"]
            songArtist = song["artist"]
            songID = abs(hash(songName+songArtist)) % (10 ** 8)
            playlistTuple = (pID, songID, session["keyword"])
            insertPlaylist.append(playlistTuple)
        cursor.executemany("INSERT INTO Playlist VALUES (?,?,?)", insertPlaylist)
        conn.commit()
        session["output"] = []
        session["keyword"] = None
    return redirect(url_for('profile'), code = 307) 

def getUserPlaylists():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    username = current_user.username
    if (cursor == None or username == None):
        print("ERROR: unable to retrieve information to get user playlists")
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
    for pid in p_id_arr:
        cursor.execute("SELECT keyword FROM Playlist WHERE p_id ="+str(pid[0]))
        keyword = cursor.fetchone()
        if keyword == None:
            keywordList.append(keyword)
        else:
            keywordList.append(keyword[0].encode("ascii"))
    for pid in p_id_arr:
        cursor.execute("SELECT s_id FROM Playlist WHERE p_id ="+str(pid[0]))
        plLength = len(cursor.fetchall())
        lengthList.append(plLength)
    for index, pid in enumerate(p_id_arr):
        dictList.append({'p_id': p_id_arr[index][0], 'keyword': keywordList[index], 'length': lengthList[index]})
    return dictList
    

def createUserList(cursor, random_s_id):
    output = []   
    if (random_s_id is None or cursor is None):
        print ("ERROR: one or more input used to createUserList does not exist")
    else:
        for s_id in random_s_id:
            cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id[0]))
            song = cursor.fetchone()[0]
            if (song == None):
                print("ERROR: something went wrong with the retrieval of song name")
            else:
                cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
                artist = cursor.fetchone()[0]
                if (artist == None):
                    print("ERROR: something went wrong with the retrieval of song artist")
                else:
                    cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
                    url = cursor.fetchone()[0]
                    if (url == None):
                        print("ERROR: something went wrong with the retrieval of song url")
                    else:
                        song_info = {}
                        song_info["name"] = song
                        song_info["artist"] = artist
                        song_info["url"] = url
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
    cursor.execute("SELECT keyword FROM masterPlaylist WHERE keyword ="+'"'+tag+'"')
    if (tag == None or length == None):
        print("ERROR: one or more inputs to getSongs does not exist")
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
        if (random_SIDS == -1):
            print("ERROR: unable to get Random SIDS")
            return -1
        if type(random_SIDs) != list:
            return random_SIDs
        output = createUserList(cursor, random_SIDs) 
        if (output == -1):
            print("ERROR: unable to create User List")
            return -1 
        else:          
            session["output"] = output
            session["keyword"] = tag
            return output

def insertDBMaster(mPlaylist, keyword):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    insertSongs = []
    insertPlaylist = []
    insertMaster = []
    if (mPlaylist == None or keyword == None):
        print("ERROR: one or more inputs to insertDBMaster does not exist")
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
        cursor.executemany("INSERT INTO Playlist VALUES (?,?,?)", insertPlaylist)
        conn.commit()
        cursor.execute("INSERT INTO masterPlaylist VALUES (" + str(pID) + ", "+"'"+keyword+"'"+", " + str(len(mPlaylist)) + ")")
        conn.commit()
        cursor.execute("SELECT * FROM masterPlaylist WHERE p_id = " + str(pID) + " AND keyword = " + "'"+keyword+"'" + "length = " + str(len(mPlaylist)))
        if (cursor.fetchone() == None):
            print("ERROR: unable to insert Master Playlist entry")

def exportSpotify(pID, keyword, username):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    trackURIs = []
    if (pID == None or keyword == None or username == None):
        print("ERROR: one or more inputs to exportSpotify don't exist")
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
    if (pid == None or songsToDelete == None):
        print("ERROR: one or more inputs to deleteFromSaved does not exist")
        return -1
    else:
        for s_id in songsToDelete:
            cursor.execute('Delete FROM Playlist WHERE p_id =' + str(pid) + " AND s_id = " + str(s_id))
            conn.commit()
            cursor.execute("SELECT FROM Playlist WHERE p_id = " + str(pid) + " AND s_id =" + str(s_id))
            if (cursor.fetchone() != None):
                print("ERROR: did not successfully delete song from desired playlist")
                return -1
    return redirect(url_for('profile')) 

def addToSaved(pid,keyword):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    playlistT = ()
    if (pid == None or keyword == None or cursor == None):
        print("ERROR: one or more inputs to addToSaved does not exist")
        return -1
    else:
        while (true):
            cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+keyword+'"')
            sid = cursor.fetchone()[0]
            if (sid == None):
                print("ERROR: relevant sid unable to be found")
            playlistsid = cursor.execute("SELECT Playlist.s_id FROM Playlist WHERE Playlist.p_id =  " + str(pid) + " AND Playlist.s_id = " + str(sid))
            for sidCompare in playlistsid:
                if (sid != sidCompare):
                    playlistT = (pid, sid, keyword)
                    break
            if (playlistT != None):
                break

        cursor.execute("INSERT INTO Playlist VALUES (?,?,?)", playlistT)
        conn.commit()
        cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(playlistT[0]) + " AND s_id = " + str(playlistT[1]) + " AND keyword = " + str(playlistT[2]))
        if (cursor.fetchone() == None):
            print("ERROR: unable to insert new song into playlist")
            return -1
        return redirect(url_for('profile')) 
# This method pre-stores popular tags for emotion, location, and weather  
#def loadDatabases():
 #   happySongs = getMasterList('happy')
  #  insertDBMaster(happySongs, 'happy')

   # sadSongs = getMasterList('sad')
    #insertDBMaster(sadSongs, 'sad')

    #angrySongs = getMasterList('angry')
    #insertDBMaster(angrySongs, 'angry')

    #nervousSongs = getMasterList('nervous')
    #insertDBMaster(nervousSongs, 'nervous')

   # scaredSongs = get


def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

if (__name__ == "__main__"):
    init_db()
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='localhost', port=3000)

