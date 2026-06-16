import pytest
import sqlite3
import os
import sys

    
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FakeConnection:
    def __init__(self, conn):
        self._conn = conn
    
    def __getattr__(self, name):
        return getattr(self._conn, name)
    
    def close(self):
        pass


@pytest.fixture
def test_db(monkeypatch):
    import models
    import data_export
    real_conn = sqlite3.connect(':memory:')
    cur = real_conn.cursor()
    
    cur.executescript('''
        create table customers (
            id integer primary key,
            name text,
            phone text,
            address text
        );
        
        create table orders (
            id integer primary key,
            customer_id integer,
            order_date text,
            status text,
            total real,
            foreign key (customer_id) references customers(id)
        );
        
        create table order_items (
            id integer primary key,
            order_id integer,
            product_name text,
            quantity integer,
            price real,
            foreign key (order_id) references orders(id)
        );
        
        insert into customers values (1, 'Name1', '+79001234567', 'Москва');
        insert into customers values (2, 'Name2', '+79007654321', 'Питер');
        
        insert into orders values (1, 1, '2026-06-01', 'выполнен', 1500.0);
        insert into orders values (2, 2, '2026-06-10', 'новый', 2000.0);
        
        insert into order_items values (1, 1, 'Голубика 1 ягода', 2, 500.0);
        insert into order_items values (2, 1, 'Черешня 50 грамм', 1, 500.0);
        insert into order_items values (3, 2, 'Малина 100г', 1, 2000.0);
    ''')
    
    real_conn.commit()
    
    fake_conn = FakeConnection(real_conn)
    
    def fake_connect(*args, **kwargs):
        return fake_conn
    
    monkeypatch.setattr(sqlite3, 'connect', fake_connect)
    monkeypatch.setattr(models.sqlite3, 'connect', fake_connect)
    monkeypatch.setattr(data_export.sqlite3, 'connect', fake_connect)
    
    yield real_conn
    
    real_conn.close()
