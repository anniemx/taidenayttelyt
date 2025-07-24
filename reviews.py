import db

def add_review(title, place, time, location, description, evaluation, user_id):
    sql = """INSERT INTO reviews (title, place, time, location, description, evaluation, user_id)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, place, time, location, description, evaluation, user_id])

def get_reviews():
    sql = "SELECT id, title FROM reviews ORDER BY id DESC"
    return db.query(sql)

def get_review(review_id):
    sql = """SELECT reviews.title,
                    reviews.place,
                    reviews.time,
                    reviews.location,
                    reviews.description,
                    reviews.evaluation,
                    users.username
             FROM reviews, users
             WHERE reviews.user_id = users.id AND
                   reviews.id = ?"""
    return db.query(sql, [review_id])[0]