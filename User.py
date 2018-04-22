from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    username = db.Column('username', db.String(20))
    password = db.Column('password' , db.String(10))
    p_id = db.Column('p_id', db.Integer, index=True, primary_key=True)
 
    def __init__(self, username ,password, p_id):
        self.username = username
        self.password = password
        self.p_id = p_id
 
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
