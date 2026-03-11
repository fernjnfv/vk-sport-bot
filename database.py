import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    age INTEGER,
    sport TEXT
)
""")

conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def get_user_data(user_id):

    user = get_user(user_id)

    if not user:
        return None

    return {
        "user_id": user[0],
        "name": user[1],
        "age": user[2],
        "sport": user[3]
    }

def create_user(user_id, first_name):
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, first_name) VALUES (?,?)",
        (user_id, first_name)
    )
    conn.commit()


def update_name(user_id, name):
    cursor.execute(
        "UPDATE users SET name=? WHERE user_id=?",
        (name, user_id)
    )
    conn.commit()

def update_age(user_id, age):
    cursor.execute(
        "UPDATE users SET age=? WHERE user_id=?",
        (age, user_id)
    )
    conn.commit()

def update_sport(user_id, sport):
    cursor.execute(
        "UPDATE users SET sport=? WHERE user_id=?",
        (sport, user_id)
    )
    conn.commit()