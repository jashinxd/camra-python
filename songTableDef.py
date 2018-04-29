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
 
    m_id = Column(Integer, ForeignKey("playlist.p_id"), nullable=False)
    keyword = Column(String, primary_key=True)
    length = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, m_id, keyword, length):
        """"""
        self.m_id = m_id
        self.keyword = keyword
        self.length = length
 
# create tables
Base.metadata.create_all(engine)
