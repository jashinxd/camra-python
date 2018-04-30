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
class Friends(Base): 
    """"""
    __tablename__ = "Friends"
    myUsername = Column(String, primary_key=True)
    friend = Column(String, ForeignKey("users.username"), nullable=False)
 
    #----------------------------------------------------------------------
    def __init__(self, myUsername, friend):
        """"""
        self.myUsername = myUsername
        self.friend = friend
 
# create tables
Base.metadata.create_all(engine)
