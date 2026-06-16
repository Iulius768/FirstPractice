import sqlite3
import os


def test_database_file_exists():
    assert os.path.exists('data/delivery')


def test_tables_exist(test_db):
    cur = test_db.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    
    assert 'customers' in tables
    assert 'orders' in tables
    assert 'order_items' in tables


def test_customers_columns(test_db):
    cur = test_db.cursor()
    cur.execute("PRAGMA table_info(customers)")
    cols = [row[1] for row in cur.fetchall()]
    assert 'id' in cols and 'name' in cols and 'phone' in cols and 'address' in cols


def test_orders_columns(test_db):
    cur = test_db.cursor()
    cur.execute("PRAGMA table_info(orders)")
    cols = [row[1] for row in cur.fetchall()]
    assert 'id' in cols and 'customer_id' in cols and 'total' in cols
