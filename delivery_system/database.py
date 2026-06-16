#все работы с БДшками
import sqlite3

DATABASE_PATH = 'data/delivery'

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
