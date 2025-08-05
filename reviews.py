import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)
    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
    return classes

def add_review(title, place, time, location, description, evaluation, user_id, classes):
    sql = """INSERT INTO reviews (title, place, time, location, description, evaluation, user_id)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, place, time, location, description, evaluation, user_id])

    review_id = db.last_insert_id()
    sql = "INSERT INTO review_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def get_classes(review_id):
    sql = "SELECT title, value FROM review_classes WHERE review_id = ?"
    return db.query(sql, [review_id])

def get_reviews():
    sql = "SELECT id, title FROM reviews ORDER BY id DESC"
    return db.query(sql)

def get_review(review_id):
    sql = """SELECT reviews.id,
                    reviews.title,
                    reviews.place,
                    reviews.time,
                    reviews.location,
                    reviews.description,
                    reviews.evaluation,
                    users.id user_id,
                    users.username
             FROM reviews, users
             WHERE reviews.user_id = users.id AND
                   reviews.id = ?"""
    result = db.query(sql, [review_id])
    return result[0] if result else None

def update_review(review_id, title, place, time, location, description, evaluation, classes):
    sql = """UPDATE reviews SET title = ?,
                                place = ?,
                                time = ?,
                                location = ?,
                                description = ?,
                                evaluation = ?
                            WHERE id = ?"""
    db.execute(sql, [title, place, time, location, description, evaluation, review_id])

    sql = "DELETE FROM review_classes WHERE review_id = ?"
    db.execute(sql, [review_id])

    sql = "INSERT INTO review_classes (review_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [review_id, title, value])

def remove_review(review_id):
    sql = "DELETE FROM review_classes WHERE review_id = ?"
    db.execute(sql, [review_id])
    sql = "DELETE FROM reviews WHERE id = ?"
    db.execute(sql, [review_id])

def find_reviews(query):
    sql = """SELECT id, title
             FROM reviews
             WHERE title LIKE ? OR place LIKE ? OR time LIKE ? OR location LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like, like, like])

def add_comment(content, user_id, evaluation, review_id):
    sql = """INSERT INTO comments (content, sent_at, user_id, evaluation, review_id)
             VALUES (?, datetime('now'), ?, ?, ?)"""
    db.execute(sql, [content, user_id, evaluation, review_id])

def get_comments(review_id):
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    comments.evaluation,
                    comments.review_id,
                    comments.user_id,
                    users.id user_id,
                    users.username
             FROM comments, users
             WHERE comments.review_id = ? AND comments.user_id = users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [review_id])

def get_comment(comment_id):
    sql = """SELECT comments.id,
                    comments.content,
                    comments.sent_at,
                    comments.evaluation,
                    comments.review_id,
                    comments.user_id,
                    users.id user_id,
                    users.username,
                    reviews.id review_id
             FROM comments, users, reviews
             WHERE comments.id = ? """
    result = db.query(sql, [comment_id])
    return result[0] #if result else None

def update_comment(content, evaluation, comment_id):
    sql = "UPDATE comments SET content = ?, evaluation = ? WHERE id = ?"
    db.execute(sql, [content, evaluation, comment_id])

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])