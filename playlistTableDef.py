from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
import os
 
path = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///test.db', echo=True)
Base = declarative_base()
 
########################################################################
class User(Base):     cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (p_id integer, s_id integer, keyword text, FOREIGN KEY(keyword) REFERENCES masterPlaylist(keyword), FOREIGN KEY(s_id) REFERENCES Song(s_id)) ''')

    """"""
    __tablename__ = "Playlist"
 
    p_id = Column(Integer)
    s_id = Column(String, ForeignKey("song.s_id"), nullable=False)
    keyword = Column(String, ForeignKey("masterPlaylist.keyword"), nullable=False)

    #----------------------------------------------------------------------
    def __init__(self, s_id, name, artist, url):
        """"""
        self.s_id = s_id
        self.name = name
        self.artist = artist
        self.url = url
 
# create tables
Base.metadata.create_all(engine)