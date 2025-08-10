import sqlite3
from flask import Flask, flash
from flask import abort, redirect, render_template, request, session
import config
import reviews
import re
import users
import db

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_reviews = reviews.get_reviews()
    return render_template("index.html", reviews=all_reviews)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    reviews = users.get_reviews(user_id)
    comments = users.get_comments(user_id)
    return render_template("show_user.html", user=user, reviews=reviews, comments=comments)

@app.route("/find_review")
def find_review():
    query = request.args.get("query")
    if query:
        results = reviews.find_reviews(query)
    else:
        query = ""
        results = []
    return render_template("find_review.html", query=query, results=results)

@app.route("/review/<int:review_id>")
def show_review(review_id):
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    classes = reviews.get_classes(review_id)
    comments = reviews.get_comments(review_id)
    return render_template("show_review.html", review=review, classes=classes, comments=comments)

@app.route("/new_review")
def new_review():
    require_login()
    classes = reviews.get_all_classes()
    return render_template("new_review.html", classes=classes)

@app.route("/create_review", methods=["POST"])
def create_review():
    require_login()
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    place = request.form["place"]
    if not place or len(place) > 50:
        abort(403)
    time = request.form["time"]
    date_format = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}-(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$"
    if not re.search(date_format, time):
        abort(403)
    location = request.form["location"]
    if not location or len(location) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)
    user_id = session["user_id"]

    all_classes = reviews.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    review_id = reviews.add_review(title, place, time, location, description, evaluation, user_id, classes)
    return redirect("/review/" + str(review_id))

@app.route("/edit_review/<int:review_id>")
def edit_review(review_id):
    require_login()
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    all_classes = reviews.get_all_classes()
    classes = {}
    for class1 in all_classes:
        classes[class1] = ""
    for entry in reviews.get_classes(review_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_review.html", review=review, classes=classes,
    all_classes=all_classes)

@app.route("/update_review", methods=["POST"])
def update_review():
    review_id = request.form["review_id"]
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    place = request.form["place"]
    if not place or len(place) > 50:
        abort(403)
    time = request.form["time"]
    date_format = r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}-(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$"
    if not re.search(date_format, time):
        abort(403)
    location = request.form["location"]
    if not location or len(location) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)

    all_classes = reviews.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    reviews.update_review(review_id, title, place, time, location, description, evaluation, classes)
    return redirect("/review/" + str(review_id))

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    require_login()
    review = reviews.get_review(review_id)
    if not review:
        abort(404)
    if review["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("remove_review.html", review=review)
    if request.method == "POST":
        if "remove" in request.form:
            reviews.remove_review(review_id)
            return redirect("/")
        else:
            return redirect("/review/" + str(review_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    content = request.form["content"]
    user_id = session["user_id"]
    review_id = request.form["review_id"]
    if not content or len(content) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)

    reviews.add_comment(content, user_id, evaluation, review_id)
    return redirect("/review/" + str(review_id))

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = reviews.get_comment(comment_id)

    if request.method == "GET":
        return render_template("edit_comment.html", comment=comment)

    if request.method == "POST":
        return update_comment()

@app.route("/update_comment", methods=["POST"])
def update_comment():
    comment_id = request.form["comment_id"]
    comment = reviews.get_comment(comment_id)
    if comment["user_id"] != session["user_id"]:
        abort(403)
    content = request.form["content"]
    if not content or len(content) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)
    reviews.update_comment(content, evaluation, comment_id)
    return redirect("/review/" + str(comment["review_id"]))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()
    comment = reviews.get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)
    if request.method == "POST":
        if "continue" in request.form:
            reviews.remove_comment(comment["id"])
            return redirect("/review/" + str(comment["review_id"]))
        else:
            return redirect("/review/" + str(comment["review_id"]))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")

    flash("Tunnus luotu")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            flash("VIRHE: väärä tunnus tai salasana")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")