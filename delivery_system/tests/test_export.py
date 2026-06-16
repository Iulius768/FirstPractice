import pytest
import json
import os
from data_export import export_table, import_table


class TestExport:
    def test_export_orders(self, test_db):
        export_table('orders')
        assert os.path.exists('orders.json')
        with open('orders.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 2
        os.remove('orders.json')

    def test_export_customers(self, test_db):
        export_table('customers')
        assert os.path.exists('customers.json')
        with open('customers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 2
        os.remove('customers.json')

    def test_export_order_items(self, test_db):
        export_table('order_items')
        assert os.path.exists('order_items.json')
        with open('order_items.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 3
        os.remove('order_items.json')


class TestImport:
    def test_import_customers(self, test_db):
        json_data = [
            {"name": "Name3", "phone": "+71111111111", "address": "Moscow"}
        ]
        with open('test_import.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False)
        result = import_table('customers', 'test_import.json')
        assert result == 'ok'
        cur = test_db.cursor()
        cur.execute("select count(*) from customers")
        count = cur.fetchone()[0]
        assert count == 3
        os.remove('test_import.json')

    def test_import_orders(self, test_db):
        json_data = [
            {
                "customer_id": 2,
                "order_date": "2026-06-15",
                "status": "новый",
                "total": 1000
            }
        ]
        with open('test_import.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False)
        result = import_table('orders', 'test_import.json')
        assert result == 'ok'
        cur = test_db.cursor()
        cur.execute("select count(*) from orders")
        count = cur.fetchone()[0]
        assert count == 3
        os.remove('test_import.json')
