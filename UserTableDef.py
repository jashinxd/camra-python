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
    __tablename__ = "users"
 
    username = Column(String, primary_key=True)
    password = Column(String)
    p_id = Column(Integer, primary_key=True)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password, p_id):
        """"""
        self.username = username
        self.password = password
        self.p_id = p_id
 
# create tables
Base.metadata.create_all(engine)
