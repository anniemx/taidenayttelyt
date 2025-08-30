import random
import sqlite3

db = sqlite3.connect("database.db")

db.execute("DELETE FROM users")
db.execute("DELETE FROM exhibitions")
db.execute("DELETE FROM comments")

user_count = 1000
exhibition_count = 10**6
comment_count = 10**7

for i in range(1, user_count + 1):
    db.execute("INSERT INTO users (username) VALUES (?)",
               ["user" + str(i)], )

for i in range(1, exhibition_count + 1):
    user_id = random.randint(1, user_count)
    db.execute("""INSERT INTO exhibitions (title, place, time, location, description, user_id) 
                  VALUES (?, ?, ?, ?, ?, ?)""",
               ["exhibition" + str(i), "place"+ str(i), "25.05.2025", 
                "location"+ str(i), "description"+ str(i), user_id])


for i in range(1, comment_count + 1):
    user_id = random.randint(1, user_count)
    exhibition_id = random.randint(1, exhibition_count)
    evaluation = random.randint(1, 5)
    db.execute("""INSERT INTO comments (title, content, sent_at, user_id, evaluation, exhibition_id)
                  VALUES (?, ?, datetime("now"), ?, ?, ?)""",
               ["title"+ str(i), "comment" + str(i), user_id, evaluation, exhibition_id])

db.commit()
db.close()
