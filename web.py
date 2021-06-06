import datetime
from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify, make_response
from datetime import timedelta
import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import url
from sqlalchemy.orm import backref
import requests
import random

app = Flask(__name__)
app.secret_key = "asdasd213213wqrWQEasdqwe"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class users(db.Model):
    __tablename__ = "Users"

    _id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password
        try:
            newID = max([u._id for u in users.query.all()])
        except:
            newID = None
        self._id = newID + 1 if newID else 1
    

class words(db.Model):
    __tablename__ = "Words"

    _id = db.Column(db.Integer, primary_key = True)
    word = db.Column(db.String(100))
    definition = db.Column(db.String(500))
    owner = db.Column(db.Integer, db.ForeignKey(users._id))
    searched = db.Column(db.Integer)
    practicePoint = db.Column(db.Integer)
    showedInPractice = db.Column(db.Integer)
    power = db.Column(db.Float)

    userR = db.relationship("users", backref=backref("word", cascade="all, delete"))

    def __init__(self, word, definition, owner, searched, practicePoint, showedInPractice, power):
        self.word = word
        self.definition = definition
        self.owner = owner
        self.searched = searched
        self.practicePoint = practicePoint
        self.showedInPractice = showedInPractice
        self.power = power
        try:
            newID = max([w._id for w in words.query.all()])
        except:
            newID = None
        self._id = newID + 1 if newID else 1

# Helper Function
def updateWordPower(id):
    word = words.query.filter_by(_id = id).first()
    word.power = word.searched/2 + word.showedInPractice/4 + word.practicePoint
    db.session.commit()


@app.route("/", methods=["GET"])
def redi():
    return redirect(url_for("login")) 

# Main Page (Page after Log in)
@app.route("/home", methods=["GET"])
def home():
    if("user" in session):
        currentUser = session['user']
        return render_template('home.html', user = currentUser)
    else:
        return redirect(url_for("login"))


# Registering to the Database
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if(username and password):
            if(not users.query.filter_by(username = username).first()):
                newUser = users(username, password)
                db.session.add(newUser)
                db.session.commit()
                flash('Registered Successfuly. Please Log in to continue.')
                return redirect(url_for("login"))
            else:
                flash("Username is taken")
        else:
            flash("Please fill Username&Password fields.")

    return render_template("register.html")

# Logging in to app
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if(not (username and password)):
            flash("Please fill Username&Password")
            return render_template("login.html")
        else:
            currentUser = users.query.filter_by(username = username).first()
            if(currentUser and currentUser.password == password):
                session['user'] = currentUser.username
                return render_template("home.html", user = currentUser.username)
            else:
                flash("Check username&password")
                return render_template("login.html")
    else:
        if "user" in session:
            return redirect(url_for("home"))
        else:
            return render_template("login.html")

    

# Logging out
@app.route("/logout", methods = ["GET"])
def logout():
    if("user" in session):
        session.pop("user", None)
    return redirect(url_for("login"))      

# User Events
# Add new word Page
@app.route("/add", methods = ["GET", "POST"])
def addWord():
    if("user" in session):
        if request.method == "POST":
            newWord = request.form['new-word']
            return newWord
        else:
            return render_template("userEvents/addWord.html", user= session['user'])
    else:
        return redirect(url_for("login"))
# Show my words
@app.route("/mywords", methods = ["GET"])
def showWord():
    if("user" in session):
        return render_template("userEvents/showWord.html", user= session['user'], myWords = words.query.filter_by(owner = users.query.filter_by(username = session['user']).first()._id).all())
    else:
        return redirect(url_for("login"))
# Practice Page
@app.route("/practice", methods = ["GET", "POST"])
def practice():
    if("user" in session):
        myWords = words.query.filter_by(owner = users.query.filter_by(username = session['user']).first()._id).all()
        if not myWords:
            myWords = []
            chosenWord = ''
            choices = []
            others = []
            correctIndex = None
        else:
            random.shuffle(myWords)
            choices = myWords[0:3]
            random.shuffle(choices)
            correctIndex = [c[1].word for c in enumerate(choices)].index(myWords[0].word)
            chosenWord = myWords[0]
            others = [myWords[1]._id, myWords[2]._id]

        return render_template("userEvents/practice.html", user= session['user'], myWords=10 if len(myWords) >= 10 else len(myWords), chosenWord=chosenWord, choices=enumerate(choices), correctIndex=correctIndex, others = others)
    else:
        return redirect(url_for("login"))
# Word searching Page
@app.route("/search", methods = ["GET"])
def search():
    if("user" in session):
        return render_template("userEvents/search.html", user= session['user'])
    else:
        return redirect(url_for("login"))

# To list all items in database, for development purposes
@app.route("/view", methods=["GET"])
def view():
    return render_template('view.html', values=users.query.join(words).all(), w = words.query.all())

@app.route('/get-definition/<word>-<add>')
def getDefinition(word, add):
    try:
        wordExist = words.query.filter_by(word = word, owner = users.query.filter_by(username = session['user']).first()._id).first()
        if(add == "true"):
            if wordExist:
                response = make_response({'error': 'Word allready exist in your dictionary'})
                return response, 409
            else:
                resp = requests.get(f"https://www.wordsapi.com/mashape/words/{word}?when=2021-06-04T07:23:09.621Z&encrypted=8cfdb18be722959bea9507bfe858bcbaaeb0240936fd96b8")
                definition = resp.json()['results'][0]['definition']
                db.session.add(words(word, definition, users.query.filter_by(username = session['user']).first()._id, 0, 0, 0, 0))
                db.session.commit()
        else:
            if wordExist:
                definition = wordExist.definition
                wordExist.searched += 1
                updateWordPower(wordExist._id)
                db.session.commit()
            else:
                resp = requests.get(f"https://www.wordsapi.com/mashape/words/{word}?when=2021-06-04T07:23:09.621Z&encrypted=8cfdb18be722959bea9507bfe858bcbaaeb0240936fd96b8")
                definition = resp.json()['results'][0]['definition']
        

        return jsonify(definition)
    except Exception as e:
        print(e)
        response = make_response({'error': 'Word not found'})
        return response, 400

@app.route('/update-practice-points', methods=["POST"])
def update():
    askedWord = words.query.filter_by(_id = request.get_json()['word']).first()
    wrong1 = request.get_json()['wrong1']
    wrong2 = request.get_json()['wrong2']
    result = request.get_json()['result']

    if(result):        
        askedWord.practicePoint += 1
        for wrong in [wrong1, wrong2]:
            otherWord = words.query.filter_by(_id = wrong).first()
            otherWord.showedInPractice +=1
            updateWordPower(otherWord._id)
    else:
        askedWord.practicePoint -= 2  
        for wrong in [wrong1, wrong2]:
            print(wrong)
            otherWord = words.query.filter_by(_id = wrong).first()
            otherWord.showedInPractice +=1
            otherWord.practicePoint -= 1
            updateWordPower(otherWord._id)

    askedWord.showedInPractice += 1
    updateWordPower(askedWord._id)
    db.session.commit()
    return "", 200

@app.route('/del-word', methods=["POST"])
def delWord():
    word = request.get_json()['word']
    word = words.query.filter_by(_id = word).first()
    db.session.delete(word)
    db.session.commit()
    return "asd"

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
