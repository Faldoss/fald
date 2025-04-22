import sqlite3
from datetime import datetime

# Підключення до бази
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Створення таблиці, якщо не існує
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    language TEXT,
    access_granted_at TEXT
)
''')
conn.commit()

# Додати користувача
def add_user(user_id, username, language):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, language, access_granted_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, language, now))
    conn.commit()

# Перевірити, чи є доступ
def has_access(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None
def get_all_users():
    cursor.execute('SELECT user_id, username, language, access_granted_at FROM users ORDER BY access_granted_at DESC')
    return cursor.fetchall()
