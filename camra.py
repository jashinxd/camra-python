from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import urllib2, json, requests, spotipy, sqlite3, os
from sqlite3 import Error
from spotipy.oauth2 import SpotifyClientCredentials
import spotify.util as util
from flask_login import LoginManager, login_user, logout_user, current_user
import sys, random
from User import User
from flask_sqlalchemy import SQLAlchemy
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
    """song = Table('song', metadata, 
        Column('s_id', Integer, primary_key = True),
        Column('artist', String(25)),
        Column('url', String(200)))"""
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, keyword text, FOREIGN KEY(keyword) REFERENCES masterPlaylist(keyword), FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')
    """playlist = Table('playlist', metadata, 
        Column('p_id', Integer),
        Column('s_id', Integer, ),
        Column('url', String(200))) """
    cursor.execute('''CREATE TABLE IF NOT EXISTS masterPlaylist (mp_id integer, keyword text PRIMARY KEY, length integer, FOREIGN KEY(mp_id) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Account (a_id integer PRIMARY KEY, playlist integer, p_id integer, FOREIGN KEY(playlist) REFERENCES Playlist(p_id))''')
    conn.commit()
    #conn.close()

try:
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SQLITE_VERSION() ')
    data = cursor.fetchone()
    print("DO IT")
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
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        #print(form)
        selection = form["category"]
        mood = form["moodoption"]
        length = form["length"]
        print(length)
        if selection == "weather":
            return getWeatherSongs(length)
        elif selection == "location":
            return getLocationSongs(length)
        elif selection == "mood":
            return getSongs(mood,length)

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
        output = viewPlaylist(p_id)
        return render_template('view.html', songs=output)
"""
@app.route("/save", methods=["GET", "POST"])
def save():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        #Code to create a new user database
        #returns userpage, but for now returns results
        #return redirect(url_for('userpage'))
        return render_template('results.html', songs=session["output"])
"""

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
        #Code to create a new user database
        #returns userpage, but for now returns results
        #return redirect(url_for('userpage')
        newoutput = []
        form = request.form
        newlist = form.getlist("songnames")
        print(newlist)
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
            #playlists = getUserPlaylists()
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

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html') 
    user = User(request.form['username'] , request.form['password'], 0)
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
        #session["user"] = registered_user
        return redirect(request.args.get('next') or url_for('index'))

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

def getWeatherSongs(length):
    tag = getWeather()
    return getSongs(tag, length)

def getMasterList(tag):
    print("IN THE MASTER")
   
    songlist = []
    songCounter = 0
    sOffset = 0
    print ("thar she blows")
    
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
  # print("this is result " + result)
    for song in r["tracks"]["track"]:
       # print("first one in ")
        results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
        #print("now here")
        #print(results["tracks"]["items"][0]["preview_url"])
        if (results["tracks"]["items"] != []):
            if (results["tracks"]["items"][0]["preview_url"] != None):
                Nsong = {}
                Nsong["name"] = song["name"]
                Nsong["artist"] = song["artist"]["name"]
                Nsong["url"] = results["tracks"]["items"][0]["preview_url"]
                songlist.append(Nsong)
      #  print("iteration done")
    
   # for playlist in results:

    print("we about to return")
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
        #print(song_info["name"])
        song_info["artist"] = artist
        song_info["url"] = url
        song_info_json = json.loads(json.dumps(song_info))
        #print(song_info_json)
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
    print(keywordList)
    for pid in p_id_arr:
        cursor.execute("SELECT s_id FROM Playlist WHERE p_id ="+str(pid[0]))
        plLength = len(cursor.fetchall())
        lengthList.append(plLength)
    print(lengthList)
    for index, pid in enumerate(p_id_arr):
        dictList.append({'p_id': p_id_arr[index][0], 'keyword': keywordList[index], 'length': lengthList[index]})
    print(dictList)
    return dictList
    

def createUserList(cursor, random_s_id):
    output = []    
    for s_id in random_s_id:
        cursor.execute("SELECT Song.name FROM Song WHERE s_id="+str(s_id[0]))
        song = cursor.fetchone()[0]
        cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
        artist = cursor.fetchone()[0]
        cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
        url = cursor.fetchone()[0]
        song_info = {}
        song_info["name"] = song
        #print(song_info["name"])
        song_info["artist"] = artist
        song_info["url"] = url
        song_info_json = json.loads(json.dumps(song_info))
        #print(song_info_json)
        output.append(song_info_json)
    return output


def getSongs(tag,length):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM masterPlaylist WHERE keyword ="+'"'+tag+'"')
    if (cursor.fetchone() == None):
        songlist = getMasterList(tag)
        insertDBMaster(songlist, tag)
        conn.commit()
    random_SIDs = getRandomSIDs(cursor, tag, length)
    if type(random_SIDs) != list:
        return random_SIDs
    output = createUserList(cursor, random_SIDs)            
    session["output"] = output
    session["keyword"] = tag
    return redirect(url_for("results"), code = 307)
    #return render_template("results.html", songs = output)

def insertDBMaster(mPlaylist, keyword):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    print("should be entering this only once tbh")
    #iterate over the master playlist creating/inserting the songs
    insertSongs = []
    insertPlaylist = []
    insertMaster = []
    pID = abs(hash(keyword)) % (10 ** 8)
    for song in mPlaylist:
        #create the hash for the song
        songName = song["name"]
        songArtist = song["artist"]
        songURL = song["url"]
        songID = abs(hash(songName+songArtist)) % (10 ** 8)
        songTuple = (songID, songName, songArtist, songURL)
        playlistTuple = (pID, songID, keyword)
        insertPlaylist.append(playlistTuple)
        insertSongs.append(songTuple)
    #print("this is insertSongs" + str(insertSongs))
    cursor.executemany("INSERT OR REPLACE INTO Song VALUES (?,?,?,?)", insertSongs)
    conn.commit()
    
    for row in cursor.execute("SELECT * FROM Song"):
       print(row)
    #conn.close()
    #create a playlist entry with all the songs in mPlaylist (some for loop)
    cursor.executemany("INSERT INTO Playlist VALUES (?,?,?)", insertPlaylist)
    conn.commit()
    #then using that id, create a masterplaylist doc with the same id, and then keyword , and playlist.length() field
    cursor.execute("INSERT INTO masterPlaylist VALUES (" + str(pID) + ", "+"'"+keyword+"'"+", " + str(len(mPlaylist)) + ")")
    conn.commit()

def exportSpotify(pID, keyword):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    trackIDs = []
    for row in cursor.execute("Select Song.name, Song.artist FROM Song, Playlist WHERE Playlist.s_id = Song.s_id AND Playlist.p_id = " + str(pID)):
         results = sp.search(q='track:' + row[1] + ' artist:' + row[2], type='track', limit=1)
         trackId = results["id"]
         trackIDs.append(trackIDs)

    scope = 'playlist-modify-private'
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print "Usage: %s username" % (sys.argv[0],)
        sys.exit()
    token = util.prompt_for_user_token(username, scope)
    if token:
        uSpot = spotipy.Spotify(auth=token)
        playlist = uSpot.user_playist_create(username, keyword, public = False, description = "imported from CAMRA")
        result = uSpot.user_playlist_add_tracks(username, playlist, trackIDs)
        print(result)

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

if (__name__ == "__main__"):
    init_db()
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='localhost', port=3000)

