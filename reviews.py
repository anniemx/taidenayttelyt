import db

def add_review(title, place, time, location, description, evaluation, user_id):
    sql = """INSERT INTO reviews (title, place, time, location, description, evaluation, user_id)
             VALUES (?, ?, ?, ?, ?, ?, ?)"""
    db.execute(sql, [title, place, time, location, description, evaluation, user_id])