import sqlite3
import json
from logger_config import logger
from database import get_connection


def export_table(table_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"select * from {table_name}")
    all_table = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    data = [{col_names[i]: row[i] for i in range(len(col_names))} for row in all_table]
    with open(f'{table_name}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, default=str)
    logger.info(f"Таблица {table_name} экспортирована в {table_name}.json")
    conn.close()


def import_table(table_name, file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "select coalesce(max(id), 0) from " + table_name
    )
    
    max_id = cur.fetchone()[0]
    inserted = 0
    skipped = 0
    for row in data:
        if 'id' in row:
            cur.execute(
                "select id from " + table_name + " where id = ?",
                (row['id'],)
            )
            if cur.fetchone():
                del row['id']
                max_id += 1
                row['id'] = max_id
        if table_name == 'orders':
            cur.execute(
                "select id from customers where id = ?",
                (row['customer_id'],)
            )
            ifid = cur.fetchone()
            if not ifid:
                logger.error(f"Файл {table_name}.json не смог быть импортирован в таблицу {table_name}")
                return "Не можем добавить записи с несуществующим пользователем"
        elif table_name == 'order_items':
            cur.execute(
                "select id from orders where id = ?",
                (row['order_id'],)
            )
            ifid = cur.fetchone()
            if not ifid:
                logger.error(f"Файл {table_name}.json не смог быть импортирован в таблицу {table_name}")
                return "Не можем добавить записи с несуществующим заказом"
        columns = ','.join(row.keys())
        placeholders = ','.join(['?' for _ in row])
        values = list(row.values())
        cur.execute(
            "insert into " + table_name + " (" + columns + ") values (" + placeholders + ")",
            values
        )
        conn.commit()
    logger.info(f"Файл {table_name}.json успешно импортирован в таблицу {table_name}")
    return 'ok'
##    conn = sqlite3.connect('data/delivery')
##    cur = conn.cursor()
##    
##    with open(file_path, 'r', encoding='utf-8') as f:
##        data = json.load(f)
##    
##    cur.execute(f"select coalesce(max(id), 0) from {table_name}")
##    max_id = cur.fetchone()[0]
##    
##    for row in data:
##        if 'id' in row:
##            cur.execute(f"select id from {table_name} where id = {row['id']}")
##            if cur.fetchone():
##                del row['id']
##                max_id += 1
##                row['id'] = max_id
##        
##        columns = ','.join(row.keys())
##        placeholders = ','.join(['?' for _ in row])
##        cur.execute(f"insert into {table_name} ({columns}) values ({placeholders})", list(row.values()))
##    
##    conn.commit()
##    logger.info(f"Данные импортированы в {table_name} из {file_path}")
##    conn.close()
