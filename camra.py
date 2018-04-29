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
    if (cursor is None):
        print "error in creating playlist"
    cursor.execute('''CREATE TABLE IF NOT EXISTS Song (s_id integer PRIMARY KEY, name text, artist text, url text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, keyword text, FOREIGN KEY(keyword) REFERENCES masterPlaylist(keyword), FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS masterPlaylist (mp_id integer, keyword text PRIMARY KEY, length integer, FOREIGN KEY(mp_id) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Account (a_id integer PRIMARY KEY, playlist integer, p_id integer, FOREIGN KEY(playlist) REFERENCES Playlist(p_id))''')
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

try:
    path = os.path.dirname(os.path.abspath(__file__))
    if (path is None):
        print ("Wrong file path")
    conn = sqlite3.connect(path + '/test.db')
    if (conn is None):
        print ("nonexistant database")
    cursor = conn.cursor()
    if (cursor is None):
        print ("error in creating playlist")
    cursor.execute('SELECT SQLITE_VERSION() ')
    data = cursor.fetchone()
    if (data is None):
        print ("noDataFetched")
    createPlaylist()
    print ("SQLite version: %s" % data )
except sqlite3.Error, e:
    print ("Error %s:" % e.args[0])
    sys.exit(1)

@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()

@app.route("/", methods=["GET", "POST"])
def index():
    length = request.form.get("length")
    if (length is None):
        return render_template("index.html")#print on screen that you need a length
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        if (form is None):
            print("No form found")
        category = form["category"]
        if (category is None):
            print("No category")
        length = form["length"]
        if (length is None):
            print("No length")
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
        else:
            return redirect(url_for('index'))#redirect to 404 screen
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
        return render_template('modify.html', songs=session["output"])

@app.route("/submitmodify", methods=["GET", "POST"])
def submitmodify():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        newoutput = []
        form = request.form
        if form is None:
            return redirect(url_for('index'))#404 page
        newlist = form.getlist("songnames")
        if newlist is None:
            return redirect(url_for('index'))#404 page
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
            if userPlaylists == -1:
                return redirect(url_for('index'))#404 page
            return render_template('profile.html', userPlaylists=userPlaylists)
        else:
            return redirect(url_for('index'))
    else:
        userPlaylists = getUserPlaylists()
        if userPlaylists == -1:
            return redirect(url_for('index'))#404 page
        print(userPlaylists)
        return render_template('profile.html', userPlaylists=userPlaylists)
    
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
"""
@app.route('/addsongsfrommaster', methods=['GET','POST'])
def addsongsfrommaster():
    if request.method == 'GET':
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = request.form
        if form is None:
            return redirect(url_for('index'))
        p_id = form["p_id"]
        if p_id is None:
            return redirect(url_for('index'))
        keyword = form["keyword"]
        if keyword is None:
            return redirect(url_for('index'))
        songsAddedStatus = addSongsToSaved(p_id, keyword)
        if songsAddedStatus != -1:
            return redirect(url_for('index'))
        return redirect(url_for('profile'))
    else:
        return -1
"""

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

#check to make sure that tag isnt null
def getWeatherSongs(length):
    tag = getWeather()
    if tag == -1:
        return -1
    return getSongs(tag, length)

def getSpotifySongs(results):
    if (results != None):
        for playlist in results["playlists"]["items"]:
            if (playlist["id"] != None):
                playlistid = playlist["id"]
            else:
                playlistid = "PlaylistID does not exist"
            if (playlist["owner"]["id"] != None):
                playlistuser = playlist["owner"]["id"]
            else:
                playlistuser = "PlaylistUser does not exist"
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
                print("song: " + tInfo["track"]["name"])
                print("artist: " + tInfo["track"]["artists"][0]["name"])
                print("url:" + tInfo["track"]["preview_url"])
                songlist.append(song)
        return songlist
    else:
        return -1

def createLastFMSongs(r):
    if (r != None):
        songlist = []
        for song in r["tracks"]["track"]:
            if (song != None):
                results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
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
                        print("url does not exist")
                    if ((Nsong["name"] != "Name Does Not Exist") and
                        (Nsong["artist"] != "Artist Does Not Exist") and
                        (Nsong["url"] != "URL Does Not Exist")):
                        print("everything ok")
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
                      "Johnny Cash", "Kenny Rogers", "Dolly Parton", "Toby Keith"
                      "Randy Travis", "Ray Price", "Rascal Flatts", "Keith Urban",
                      "The Judds", "Blake Shelton", "Faith Hill", "Bill Anderson",
                      "Lynn Anderson", "Charlie Rich", "Connie Smith", "Sugarland",
                      "Tracy Lawrence", "Sawyer Brown", "Lonestar", "Eric Church",
                      "Clay Walker", "Miranda Lambert"]
    selectedPlaylistNum = random.randint(0, 3)
    if selectedPlaylistNum == 0:
        artistLength = len(artists)
        selectedArtist = []
        selectedArtistSongs = []
        for x in range(5):
            selectedArtist.append(random.randint(0, artistLength - 1))
        if not selectedArtist:
            print("list is empty")
        for song in selectedArtist:
            selectedArtistSongs.extend(getSongs(song, length))
        if not selectedArtistSongs:
            print("list is empty")
        return selectedArtistSongs
    elif selectedPlaylistNum == 1:
        popularArtistLength = len(currentPopularArtists)
        selectedPopularArtist = []
        selectedPopularArtistSongs = []
        for x in range(5):
            selectedPopularArtist.append(random.randint(0, popularArtistLength - 1))
        if not selectedPopularArtist:
            print("list is empty")
        for song in selectedPopularArtist:
            selectedPopularArtistSongs.extend(getSongs(song, length))
        if not selectedPopularArtistSongs:
            print("list is empty")
        return selectedPopularArtistSongs
    elif selectedPlaylistNum == 2:
        instrumentalArtistLength = len(instrumentalArtists)
        selectedInstrumentalArtist = []
        selectedInstrumentalArtistSongs = []
        for x in range(5):
            selectedInstrumentalArtist.append(random.randint(0, instrumentalArtistLength - 1))
        if not selectedInstrumentalArtist:
            print("list is empty")
        for song in selectedInstrumentalArtist:
            selectedInstrumentalArtistSongs.extend(getSongs(song, length))
        if not selectedInstrumentalArtistSongs:
            print("list is empty")
        return selectedInstrumentalArtistSongs
    elif selectedPlaylistNum == 3:
        countryArtistLength = len(countryArtists)
        selectedCountryArtist = []
        selectedCountryArtistSongs = []
        for x in range(5):
            selectedCountryArtist.append(random.randint(0, countryArtistLength - 1))
        if not selectedCountryArtist:
            print("list is empty")
        for song in selectedCountryArtist:
            selectedCountryArtistSongs.extend(getSongs(song, length))
        if not selectedCountryArtistSongs:
            print("list is empty")
        return selectedCountryArtistSongs
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
        song = cursor.fetchone()
        if (song != None):
            song = song[0]
        cursor.execute("SELECT Song.artist FROM Song WHERE s_id="+str(s_id[0]))
        artist = cursor.fetchone()
        if (artist != None):
            artist = artist[0]
        cursor.execute("SELECT Song.url FROM Song WHERE s_id="+str(s_id[0]))
        url = cursor.fetchone()
        if (url != None):
            url = url[0]
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
def insertUserPlaylist():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
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
        playlistInserted = cursor.fetchone()
        if (playlistInserted == None):
            return redirect(url_for('index'))
        insertPlaylist = []
        for song in session["output"]:
            if ((song["name"] != None) and (song["artist"] != None)):
                songName = song["name"]
                songArtist = song["artist"]
                songID = abs(hash(songName+songArtist)) % (10 ** 8)
                playlistTuple = (pID, songID, session["keyword"])
                insertPlaylist.append(playlistTuple)
        cursor.executemany("INSERT INTO Playlist VALUES (?,?,?)", insertPlaylist)
        conn.commit()
        for song in session["output"]:
            if ((song["name"] != None) and (song["artist"] != None)):
                songName = song["name"]
                songArtist = song["artist"]
                songID = abs(hash(songName+songArtist)) % (10 ** 8)
                cursor.execute("SELECT * FROM Playlist WHERE p_id="+str(pID)+" AND s_id="+str(songID)+" AND keyword="+'"'+session["keyword"]+'"')
                songInserted = cursor.fetchone()
                print(songInserted)
                if (songInserted == None):
                    return redirect(url_for(index))
        session["output"] = []
        session["keyword"] = None
        return redirect(url_for('profile'), code = 307)
    else:
        return redirect(url_for('index'))    

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
            cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(pid) + " AND s_id =" + str(s_id))
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
        while (playlistT == ()):
            cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND masterPlaylist.keyword="+'"'+keyword+'"')
            sids = cursor.fetchall()
            sid = random.choice(sids)[0]
            if (sid == None):
                print("ERROR: relevant sid unable to be found")
            cursor.execute("SELECT Playlist.s_id FROM Playlist WHERE Playlist.p_id =  " + str(pid) + " AND Playlist.s_id = " + str(sid))
            playlistsid = cursor.fetchone()
            if (playlistsid == None):
                playlistT = (pid, sid, keyword)

        cursor.execute("INSERT INTO Playlist VALUES (?,?,?)", playlistT)
        print("inserting")
        conn.commit()
        cursor.execute("SELECT * FROM Playlist WHERE p_id = " + str(playlistT[0]) + " AND s_id = " + str(playlistT[1]) + " AND keyword = " +'"'+ str(playlistT[2]) + '"')
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

