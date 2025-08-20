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

def add_exhibition(title, place, time, location, description, user_id, classes):
    sql = """INSERT INTO exhibitions (title, place, time, location, description, user_id)
             VALUES (?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, place, time, location, description, user_id])

    exhibition_id = db.last_insert_id()
    sql = "INSERT INTO exhibition_classes (exhibition_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [exhibition_id, class_title, class_value])
    return exhibition_id

def get_classes(exhibition_id):
    sql = "SELECT title, value FROM exhibition_classes WHERE exhibition_id = ?"
    return db.query(sql, [exhibition_id])

def get_exhibitions():
    sql = """SELECT exhibitions.id, exhibitions.title, users.id user_id, users.username
             FROM exhibitions, users
             WHERE exhibitions.user_id = users.id
             ORDER BY exhibitions.id DESC"""
    return db.query(sql)

def get_exhibition(exhibition_id):
    sql = """SELECT exhibitions.id,
                    exhibitions.title,
                    exhibitions.place,
                    exhibitions.time,
                    exhibitions.location,
                    exhibitions.description,
                    users.id user_id,
                    users.username
             FROM exhibitions, users
             WHERE exhibitions.user_id = users.id AND
                   exhibitions.id = ?"""
    result = db.query(sql, [exhibition_id])
    return result[0] if result else None

def update_exhibition(exhibition_id, title, place, time, location, description, classes):
    sql = """UPDATE exhibitions SET title = ?,
                                place = ?,
                                time = ?,
                                location = ?,
                                description = ?
                            WHERE id = ?"""
    db.execute(sql, [title, place, time, location, description, exhibition_id])

    sql = "DELETE FROM exhibition_classes WHERE exhibition_id = ?"
    db.execute(sql, [exhibition_id])

    sql = "INSERT INTO exhibition_classes (exhibition_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [exhibition_id, class_title, class_value])

def remove_exhibition(exhibition_id):
    sql = "DELETE FROM comments WHERE exhibition_id = ?"
    db.execute(sql, [exhibition_id])
    sql = "DELETE FROM exhibition_classes WHERE exhibition_id = ?"
    db.execute(sql, [exhibition_id])
    sql = "DELETE FROM exhibitions WHERE id = ?"
    db.execute(sql, [exhibition_id])

def find_exhibitions(query):
    sql = """SELECT id, title
             FROM exhibitions
             WHERE title LIKE ? OR place LIKE ? OR time LIKE ? OR location LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like, like, like, like])

def check_title(query):
    sql = """SELECT id, title
             FROM exhibitions
             WHERE title LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    result = db.query(sql, [like])
    return result[0] if result else None

def add_comment(title, content, user_id, evaluation, exhibition_id):
    sql = """INSERT INTO comments (title, content, sent_at, user_id, evaluation, exhibition_id)
             VALUES (?, ?, datetime('now'), ?, ?, ?)"""
    db.execute(sql, [title, content, user_id, evaluation, exhibition_id])

def get_comments(exhibition_id):
    sql = """SELECT comments.id,
                    comments.title,
                    comments.content,
                    comments.sent_at,
                    comments.evaluation,
                    comments.exhibition_id,
                    comments.user_id,
                    users.id user_id,
                    users.username
             FROM comments, users
             WHERE comments.exhibition_id = ? AND comments.user_id = users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [exhibition_id])

def get_comment(comment_id):
    sql = """SELECT comments.id,
                    comments.title,
                    comments.content,
                    comments.sent_at,
                    comments.evaluation,
                    comments.exhibition_id,
                    comments.user_id,
                    users.id user_id,
                    users.username,
                    exhibitions.id exhibition_id
             FROM comments, users, exhibitions
             WHERE comments.id = ? """
    result = db.query(sql, [comment_id])
    return result[0]

def update_comment(title, content, evaluation, comment_id):
    sql = "UPDATE comments SET title = ?, content = ?, evaluation = ? WHERE id = ?"
    db.execute(sql, [title, content, evaluation, comment_id])

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])

def average_score(exhibition_id):
    sql = "SELECT AVG(evaluation) FROM comments WHERE exhibition_id = ?"
    score = db.query(sql, [exhibition_id])
    return score[0][0] if score else 0
