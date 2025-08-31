import re
import secrets
import sqlite3
import math
import time

from flask import Flask, flash
from flask import g
from flask import abort, make_response, redirect, render_template, request, session
import markupsafe

import config
import exhibitions
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    page_size = 10
    exhibition_count = exhibitions.exhibition_count()
    page_count = math.ceil(exhibition_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/1")
    if page > page_count:
        return redirect("/" + str(page_count))

    all_exhibitions = exhibitions.get_exhibitions(page, page_size)
    return render_template("index.html", page=page, page_count=page_count, exhibitions=all_exhibitions)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_exhibitions = users.get_exhibitions(user_id)
    comments = users.get_comments(user_id)
    return render_template("show_user.html", user=user, exhibitions=user_exhibitions,
                            comments=comments)

@app.route("/find_exhibition")
def find_exhibition():
    query = request.args.get("query")
    if query:
        results = exhibitions.find_exhibitions(query)
    else:
        query = ""
        results = []
    return render_template("find_exhibition.html", query=query, results=results)

@app.route("/exhibition/<int:exhibition_id>")
@app.route("/exhibition/<int:exhibition_id>/<int:page>")
def show_exhibition(exhibition_id, page=1):
    exhibition = exhibitions.get_exhibition(exhibition_id)
    if not exhibition:
        abort(404)
    classes = exhibitions.get_classes(exhibition_id)

    page_size = 10
    comment_count = exhibitions.comment_count(exhibition_id)
    page_count = math.ceil(comment_count / page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect("/exhibition/"+ str(exhibition_id) + "/1")
    if page > page_count:
        return redirect("/exhibition/"+ str(exhibition_id) + "/" + str(page_count))

    comments = exhibitions.get_comments(exhibition_id, page, page_size)
    score = exhibitions.average_score(exhibition_id)
    if score is not None:
        score = f"{score:.2f}"
    else:
        score = 0
    return render_template("show_reviews.html", exhibition=exhibition, classes=classes,
                           comments=comments, score=score, page=page, page_count=page_count)

@app.route("/new_exhibition")
def new_exhibition():
    require_login()
    classes = exhibitions.get_all_classes()
    return render_template("new_exhibition.html", classes=classes)

@app.route("/create_exhibition", methods=["POST"])
def create_exhibition():
    require_login()
    check_csrf()
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    check = exhibitions.check_title(title)
    if check:
        flash("Näyttely on jo lisätty. Anna oma arviosi täällä.")
        return redirect("/exhibition/"+ str(check["id"]))
    place = request.form["place"]
    if not place or len(place) > 50:
        abort(403)
    time = request.form["time"]
    date_format = (
        r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}-"
        r"(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$"
    )
    if not re.search(date_format, time):
        abort(403)
    location = request.form["location"]
    if not location or len(location) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)
    user_id = session["user_id"]

    all_classes = exhibitions.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    exhibition_id = exhibitions.add_exhibition(title, place, time, location,
                                                description, user_id, classes)
    return redirect("/exhibition/" + str(exhibition_id))

@app.route("/edit_exhibition/<int:exhibition_id>")
def edit_exhibition(exhibition_id):
    require_login()
    exhibition = exhibitions.get_exhibition(exhibition_id)
    if not exhibition:
        abort(404)
    if exhibition["user_id"] != session["user_id"]:
        abort(403)
    all_classes = exhibitions.get_all_classes()
    classes = {}
    for class1 in all_classes:
        classes[class1] = ""
    for entry in exhibitions.get_classes(exhibition_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_exhibition.html", exhibition=exhibition, classes=classes,
    all_classes=all_classes)

@app.route("/update_exhibition", methods=["POST"])
def update_exhibition():
    check_csrf()
    exhibition_id = request.form["exhibition_id"]
    exhibition = exhibitions.get_exhibition(exhibition_id)
    if not exhibition:
        abort(404)
    if exhibition["user_id"] != session["user_id"]:
        abort(403)
    title_check = exhibition["title"]
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    check = exhibitions.check_title(title)
    if check and check["title"] != title_check:
        flash("Näyttely on jo lisätty. Anna oma arviosi täällä.")
        return redirect("/exhibition/"+ str(check["id"]))
    place = request.form["place"]
    if not place or len(place) > 50:
        abort(403)
    time = request.form["time"]
    date_format = (
        r"^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}-"
        r"(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.\d{4}$"
    )
    if not re.search(date_format, time):
        abort(403)
    location = request.form["location"]
    if not location or len(location) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 1000:
        abort(403)

    all_classes = exhibitions.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    exhibitions.update_exhibition(exhibition_id, title, place, time, location, description, classes)
    return redirect("/exhibition/" + str(exhibition_id))

@app.route("/remove_exhibition/<int:exhibition_id>", methods=["GET", "POST"])
def remove_exhibition(exhibition_id):
    require_login()
    exhibition = exhibitions.get_exhibition(exhibition_id)
    if not exhibition:
        abort(404)
    if exhibition["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("remove_exhibition.html", exhibition=exhibition)
    if request.method == "POST":
        if "remove" in request.form:
            check_csrf()
            exhibitions.remove_exhibition(exhibition_id)
            return redirect("/")
        return redirect("/exhibition/" + str(exhibition_id))

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    content = request.form["content"]
    user_id = session["user_id"]
    exhibition_id = request.form["exhibition_id"]
    if not content or len(content) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)

    exhibitions.add_comment(title, content, user_id, evaluation, exhibition_id)
    return redirect("/exhibition/" + str(exhibition_id))

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = exhibitions.get_comment(comment_id)

    if request.method == "GET":
        return render_template("edit_comment.html", comment=comment)

    if request.method == "POST":
        return update_comment()

@app.route("/update_comment", methods=["POST"])
def update_comment():
    require_login()
    check_csrf()
    comment_id = request.form["comment_id"]
    comment = exhibitions.get_comment(comment_id)
    if comment["user_id"] != session["user_id"]:
        abort(403)
    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    content = request.form["content"]
    if not content or len(content) > 1000:
        abort(403)
    evaluation = request.form["evaluation"]
    if not evaluation:
        abort(403)
    exhibitions.update_comment(title, content, evaluation, comment_id)
    return redirect("/exhibition/" + str(comment["exhibition_id"]))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
def remove_comment(comment_id):
    require_login()
    comment = exhibitions.get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)
    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)
    if request.method == "POST":
        check_csrf()
        if "continue" in request.form:
            exhibitions.remove_comment(comment["id"])
            return redirect("/exhibition/" + str(comment["exhibition_id"]))
        return redirect("/exhibition/" + str(comment["exhibition_id"]))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    if len(username) < 4 or len(username) > 50:
        flash("VIRHE: käyttäjätunnus on liian lyhyt tai pitkä")
        return redirect("/register")
    username_error = re.search(r"[a-z]", username) is None
    if username_error:
        flash("VIRHE: käyttäjätunnuksessa on oltava kirjaimia")
        return redirect("/register")

    password1 = request.form["password1"]
    if not password1:
        flash("VIRHE: salasana ei voi olla tyhjä")
        return redirect("/register")

    if len(password1) < 8 or len(password1) > 50:
        flash("VIRHE: Salasanan pituus ei täytä vaatimuksia")
        return redirect("/register")

    digit = re.search(r"\d", password1) is None
    uppercase = re.search(r"[A-Z]", password1) is None
    lowercase = re.search(r"[a-z]", password1) is None
    symbol = re.search(r"[ !#$%&'()*+,\-./\[\]^_`{}~\"]", password1) is None

    if digit or uppercase or lowercase or symbol:
        flash("VIRHE: Salasana on liian heikko")
        return redirect("/register")

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
    return redirect("/login")

@app.route("/add_image", methods=["GET", "POST"])
def add_image():
    require_login()

    if request.method == "GET":
        return render_template("add_image.html")

    if request.method == "POST":
        check_csrf()
        file = request.files["image"]
        if not file.filename.endswith(".jpg"):
            flash("VIRHE: väärä tiedostomuoto")
            return redirect("/add_image")

        image = file.read()
        if len(image) > 100 * 1024:
            flash("VIRHE: liian suuri kuva")
            return redirect("/add_image")

        user_id = session["user_id"]
        users.update_image(user_id, image)
        return redirect("/user/" + str(user_id))

@app.route("/image/<int:user_id>")
def show_image(user_id):
    image = users.get_image(user_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", username="")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        flash("VIRHE: väärä tunnus tai salasana")
        return render_template("login.html", username=username)

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
