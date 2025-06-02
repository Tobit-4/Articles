# lib/db/connection.py

import sqlite3

def get_connection():
    conn = sqlite3.connect('articles.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row 
    return conn
