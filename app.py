import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import reviews

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_reviews = reviews.get_reviews()
    return render_template("index.html", reviews=all_reviews)

@app.route("/review/<int:review_id>")
def show_review(review_id):
    review = reviews.get_review(review_id)
    return render_template("show_review.html", review=review)

@app.route("/new_review")
def new_review():
    return render_template("new_review.html")

@app.route("/create_review", methods=["POST"])
def create_review():
    title = request.form["title"]
    place = request.form["place"]
    time = request.form["time"]
    location = request.form["location"]
    description = request.form["description"]
    evaluation = request.form["evaluation"]
    user_id = session["user_id"]

    reviews.add_review(title, place, time, location, description, evaluation, user_id)
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")