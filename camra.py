from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import urllib2, json, requests, spotipy, sqlite3, os
from sqlite3 import Error
from spotipy.oauth2 import SpotifyClientCredentials
from flask_login import LoginManager, login_user, logout_user
import sys, random
from User import User
from flask_sqlalchemy import SQLAlchemy

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
    cursor.execute('''CREATE TABLE IF NOT EXISTS Song (s_id integer, name text, artist text, url text)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS masterPlaylist (mp_id integer, keyword text, length integer, FOREIGN KEY(mp_id) REFERENCES Playlist(p_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Account (a_id integer, playlist, FOREIGN KEY(playlist) REFERENCES Playlist(p_id))''')
    conn.commit()
    #conn.close()

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
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        print(form)
        selection = form["category"]
        mood = form["moodoption"]
        length = form["length"]
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

@app.route("/save", methods=["GET", "POST"])
def save():
    if request.method == "GET":
        return redirect(url_for('index'))
    else:
        #Code to create a new user database
        #returns userpage, but for now returns results
        #return redirect(url_for('userpage'))
        return render_template('results.html', songs=session["output"])

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
        
@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html') 
    user = User(request.form['username'] , request.form['password'])
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
    return weather

def getWeatherSongs(length):
    tag = getWeather()
    return getSongs(tag, length)

def getMasterList(tag):
    url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json&limit=100"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    songlist = []
    for song in r["tracks"]["track"]:
        print(song)
        results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
        #print(results["tracks"]["items"][0]["preview_url"])
        if (results["tracks"]["items"] != []):
            if (results["tracks"]["items"][0]["preview_url"] != None):
                song["url"] = results["tracks"]["items"][0]["preview_url"]
                songlist.append(song)
    return songlist

def getRandomSIDs(cursor, tag, length):
    s_id_arr = []
    cursor.execute("SELECT s_id FROM masterPlaylist, Playlist WHERE mp_id = p_id AND keyword="+'"'+tag+'"')
    sid = cursor.fetchone()
    while (sid != None):
        s_id_arr.append(sid)
        sid = cursor.fetchone()
    if (len(s_id_arr) < int(length)):
        return render_template("index.html", message = "You requested for too many songs. The maximum number of songs for this category is " + str(len(s_id_arr)))
    return random.sample(s_id_arr, int(length))

# Inserts the song into the playlist database
# def insertUserPlaylist(name, artist, url):

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
    output = createUserList(cursor, random_SIDs)
    session['output'] = output
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
        songArtist = song["artist"]["name"]
        songURL = song["url"]
        songID = abs(hash(songName+songArtist)) % (10 ** 8)
        songTuple = (songID, songName, songArtist, songURL)
        playlistTuple = (pID, songID)
        insertPlaylist.append(playlistTuple)
        insertSongs.append(songTuple)
    cursor.executemany("INSERT INTO Song VALUES (?,?,?,?)", insertSongs)
    conn.commit()
    
    for row in cursor.execute("SELECT * FROM Song"):
       print(row)
    #conn.close()
    #create a playlist entry with all the songs in mPlaylist (some for loop)
    cursor.executemany("INSERT INTO Playlist VALUES (?,?)", insertPlaylist)
    conn.commit()
    #then using that id, create a masterplaylist doc with the same id, and then keyword , and playlist.length() field
    cursor.execute("INSERT INTO masterPlaylist VALUES (" + str(pID) + ", "+"'"+keyword+"'"+", " + str(len(mPlaylist)) + ")")
    conn.commit()

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

if (__name__ == "__main__"):
    init_db()
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='localhost', port=3000)

