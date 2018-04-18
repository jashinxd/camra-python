from flask import Flask, render_template, request, jsonify
import urllib2, json, requests, spotipy, sqlite3, os
from sqlite3 import Error
from spotipy.oauth2 import SpotifyClientCredentials
import sys 

client_credentials_manager = SpotifyClientCredentials(client_id = '0b4d677f62e140ee8532bed91951ae52', client_secret = 'cc1e617a9c064aa982e8eeaf65626a94')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app = Flask(__name__)


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

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
    
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



def getSongs(tag,length):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/test.db')
    cursor = conn.cursor()
    #term = "'" + tag + "'"
   # print(tag)
    cursor.execute("SELECT keyword FROM masterPlaylist WHERE keyword ="+'"'+tag+'"')
   #print("this is the checking of stuff")
   # print(cursor.fetchone())

    if (cursor.fetchone() == None):
        url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json&limit=100"
        requested = urllib2.urlopen(url)
        result = requested.read()
        r = json.loads(result)
        songlist = []
        for song in r["tracks"]["track"]:
            print(song["name"])
            results = sp.search(q='track:' + song["name"] + ' artist:' + song["artist"]["name"], type='track', limit=1)
            #print(results["tracks"]["items"][0]["preview_url"])
            if (results["tracks"]["items"] == []):
                break
            if (results["tracks"]["items"][0]["preview_url"] != None):
                song["url"] = results["tracks"]["items"][0]["preview_url"]
                songlist.append(song)
        insertDBMaster(songlist, tag)
        conn.commit()
    #conn.close()
    output = []
    counter = 0
    #lookup the entire playlist, pick however many songs they want, create a user playlist, insert it into the db, and then render
    for row in cursor.execute("SELECT Song.name, Song.artist, Song.url FROM Song, masterPlaylist, Playlist WHERE mp_id = p_id AND Playlist.s_id = Song.s_id AND keyword = keyword ="+'"'+tag+'"'):
        output.append(row)
        print(row)
        counter += 1
        if (counter == length):
            break
    return render_template("results.html", songs = output)

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
        songTuple = (songName, songArtist, songURL, songID)
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

if (__name__ == "__main__"):
    app.debug = True
    app.run(host='localhost', port=3000)
