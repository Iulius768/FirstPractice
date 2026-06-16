import pytest
import sqlite3
from models import Customer, Order


class TestCustomer:
    def test_get_all(self, test_db):
        clients = Customer.get_all()
        assert len(clients) == 2
        assert clients[0][1] == 'Name1'
        assert clients[1][1] == 'Name2'

    def test_get_names(self, test_db):
        names = Customer.get_names()
        assert 'Name1' in names
        assert 'Name2' in names
        assert len(names) == 2

    def test_add(self, test_db):
        Customer.add('Сидоров', '+79991112233', 'Казань')
        cur = test_db.cursor()
        cur.execute("select * from customers where name = 'Сидоров'")
        client = cur.fetchone()
        assert client is not None
        assert client[1] == 'Сидоров'
        assert client[2] == '+79991112233'
        assert client[3] == 'Казань'

    def test_get_by_id(self, test_db):
        client = Customer.get_by_id(1)
        assert client is not None
        assert client[0] == 'Name1'
        assert client[1] == '+79001234567'

    def test_get_by_id_not_found(self, test_db):
        client = Customer.get_by_id(999)
        assert client is None

    def test_update(self, test_db):
        Customer.update(1, 'Иванов Иван', '+79990000000', 'Сочи')
        client = Customer.get_by_id(1)
        assert client[0] == 'Иванов Иван'
        assert client[1] == '+79990000000'
        assert client[2] == 'Сочи'

    def test_delete_without_orders(self, test_db):
        Customer.add('Удаляемый', '+70000000000', 'Где-то')
        cur = test_db.cursor()
        cur.execute("select id from customers where name = 'Удаляемый'")
        new_id = cur.fetchone()[0]
        result = Customer.delete(new_id)
        assert result == True
        client = Customer.get_by_id(new_id)
        assert client is None

    def test_delete_with_orders(self, test_db):
        result = Customer.delete(1)
        assert result == False
        client = Customer.get_by_id(1)
        assert client is not None


class TestOrder:
    def test_get_all(self, test_db):
        orders = Order.get_all()
        assert len(orders) == 2

    def test_get_all_with_client_filter(self, test_db):
        orders = Order.get_all({'client': 'Name1'})
        assert len(orders) == 1
        assert orders[0][2] == 'Name1'

    def test_get_all_with_status_filter(self, test_db):
        orders = Order.get_all({'status': 'новый'})
        assert len(orders) == 1
        assert orders[0][5] == 'новый'

    def test_get_all_with_sort(self, test_db):
        orders = Order.get_all({'sort_by_date': True})
        assert len(orders) == 2
        assert orders[0][1] == '2026-06-10'

    def test_add(self, test_db):
        Order.add(
            '2026-06-14',
            'Name2',
            ['Бургер', 'Картошка'],
            [300, 150],
            [2, 1],
            'новый'
        )
        orders = Order.get_all()
        assert len(orders) == 3

    def test_get_by_id(self, test_db):
        order = Order.get_by_id(1)
        assert order is not None
        assert order[0] == '2026-06-01'
        assert order[1] == 'Name1'

    def test_get_by_id_not_found(self, test_db):
        order = Order.get_by_id(999)
        assert order is None

    def test_delete(self, test_db):
        Order.delete(1)
        order = Order.get_by_id(1)
        assert order is None
        cur = test_db.cursor()
        cur.execute("select count(*) from order_items where order_id = 1")
        count = cur.fetchone()[0]
        assert count == 0

    def test_update(self, test_db):
        Order.update(
            1,
            '2026-06-15',
            'Name1',
            ['Пицца обновлённая'],
            [600],
            [1],
            'в доставке'
        )
        order = Order.get_by_id(1)
        assert order[0] == '2026-06-15'
        assert order[5] == 'в доставке'

    def test_get_revenue_all_time(self, test_db):
        total = Order.get_revenue()
        assert total == 3500.0

    def test_get_revenue_period(self, test_db):
        total = Order.get_revenue('за месяц')
        assert total == 3500.0

    def test_get_top_clients(self, test_db):
        top = Order.get_top_clients()
        assert len(top) == 2
        assert top[0][1] == 'Name2'
        assert top[0][0] == 2000.0

    def test_get_status_counts(self, test_db):
        statuses, counts = Order.get_status_counts()
        assert len(statuses) == 4
        assert len(counts) == 4
        assert counts[statuses.index('выполнен')] == 1
        assert counts[statuses.index('новый')] == 1
        assert counts[statuses.index('в доставке')] == 0
        assert counts[statuses.index('отменён')] == 0
