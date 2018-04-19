app = Flask(__name__)

class Song():

    def __init__(self, songID , songName, songArtist, songURL):
        self.songID = songID
        self.songName = songName
        self.songArtist = songArtist
        self.songURL = songURL
        self.isPlaying = False
 
    def getIsPlaying:
        return isPlaying

    def changeIsPlaying:
        return !isPlaying
    
