from flask import Flask, render_template, request, jsonify, flash, redirect, render_template, request, session, abort
from flask import url_for
from flask_login import LoginManager, login_user, login_required, logout_user
from forms import SignupForm
from models import db
from flask_sqlalchemy import SQLAlchemy
import urllib2, json, requests
import os

app = Flask(__name__)
app.secret_key = 'poop'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

def init_db():
    db.init_app(app)
    db.app = app
    db.create_all()

@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email = email).first()

@app.route('/protected')
@login_required
def protected():
    return "protected area"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if not session.get('logged_in'):
            return render_template('login.html')
        else:
            return render_template("index.html")
    elif request.method == "POST":
        form = request.form
        print(form)
        selection = form["category"]
        if selection == "weather":
            getWeatherSongs()
        elif selection == "location":
            getLocationSongs()
        elif selection == "mood":
            getMoodSongs()

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=User.query.filter_by(email=form.email.data).first()
            if user:
                if user.password == form.password.data:
                    login_user(user)
                    return "User logged in"                
                else:
                    return "Wrong password"            
            else:
                return "user doesn't exist"        
    else:
            return "form not validated"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if request.method == 'GET':
        return render_template('signup.html', form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if 'user already exist in database':
                return "Email address already exists"
            else:
                newuser = User(form.email.data, form.password.data)
                db.session.add(newuser)
                db.session.commit()

                login_user(newuser)
                return "User created!!!" 
        else:
            return "Form didn't validate"

@app.route('/logout')
def logout():
    logout_user()
    return index()

def getLocationSongs():
    url = "http://ipinfo.io/"
    results = requests.get(url).json()
    city = results["city"]
    getSongs(city)

def getWeatherSongs():
    print("weather")

def getMoodSongs():
    print("mood")

def getSongs(tag):
    url = "http://ws.audioscrobbler.com/2.0/?method=tag.gettoptracks&tag=" + tag + "&api_key=eaa991e4c471a7135879ba14652fcbe5&format=json"
    requested = urllib2.urlopen(url)
    result = requested.read()
    r = json.loads(result)
    songlist = []
    for song in r["tracks"]["track"]:
        print(song["name"])
        songlist.append(song)

if (__name__ == "__main__"):
    app.init_db()
    app.debug = True
    app.run(host='localhost', port=3000)
