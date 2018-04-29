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
class User(Base): 
    """"""
    __tablename__ = "masterPlaylist"
 
    s_id = Column(Integer, primary_key=True)
    name = Column(String)
    artist = Column(String)
    url = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, s_id, name, artist, url):
        """"""
        self.s_id = s_id
        self.name = name
        self.artist = artist
        self.url = url
 
# create tables
Base.metadata.create_all(engine)