from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    username = db.Column('username', db.String(20), unique=True , index=True, primary_key= True)
    password = db.Column('password' , db.String(10))
 
    def __init__(self, username ,password):
        self.username = username
        self.password = password
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.username)
 
    def __repr__(self):
        return '<User %r>' % (self.username)