import sqlite3
from functools import reduce
from logger_config import logger
from database import get_connection


class Customer:
    @staticmethod
    def get_all():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("select id, name, phone, address from customers")
        clients = cur.fetchall()
        conn.close()
        return clients
    
    @staticmethod
    def get_names():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("select name from customers")
        names = [row[0] for row in cur.fetchall()]
        conn.close()
        return names
    
    @staticmethod
    def add(name, phone, address):
        logger.info("Добавляется клиент")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "insert into customers values((select ifnull(max(id), 0) + 1 from customers), ?, ?, ?)",
            (name, phone, address)
        )
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(customer_id):
        logger.info("Удаляется клиент")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("select count(*) from orders where customer_id = ?", (customer_id,))
        if cur.fetchone()[0] > 0:
            conn.close()
            return False
        cur.execute("delete from customers where id = ?", (customer_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_by_id(customer_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("select name, phone, address from customers where id = ?", (customer_id,))
        client = cur.fetchone()
        conn.close()
        return client
    
    @staticmethod
    def update(customer_id, name, phone, address):
        logger.info("Редактируется клиент")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "update customers set name = ?, phone = ?, address = ? where id = ?",
            (name, phone, address, customer_id)
        )
        conn.commit()
        conn.close()


class Order:
    @staticmethod
    def get_all(filters=None):
        conn = get_connection()
        cur = conn.cursor()
        
        query = """select
                    orders.id,
                    orders.order_date,
                    customers.name,
                    group_concat(order_items.product_name) as list,
                    orders.total,
                    orders.status
                from orders
                    join order_items on orders.id = order_items.order_id
                    join customers on orders.customer_id = customers.id"""
        
        conditions = []
        params = []
        
        if filters:
            if filters.get('client'):
                conditions.append("customers.name = ?")
                params.append(filters['client'])
            if filters.get('status'):
                conditions.append("orders.status = ?")
                params.append(filters['status'])
        
        if conditions:
            query += " where " + " AND ".join(conditions)
        
        query += " group by orders.id"
        
        if filters and filters.get('sort_by_date'):
            query += " order by orders.order_date DESC"
        
        cur.execute(query, params)
        orders = cur.fetchall()
        conn.close()
        return orders
    
    @staticmethod
    def add(date, client_name, product_names, prices, quantities, status):
        logger.info("Добавляется заказ")
        total = reduce(lambda x, y: x + y, [p * q for p, q in zip(prices, quantities)])
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "insert into orders values((select count(*) from orders)+1, (select id from customers where name = ?), ?, ?, ?) returning id",
            (client_name, date, status, total)
        )
        new_order_id = cur.fetchone()[0]
        
        for i in range(len(product_names)):
            cur.execute(
                "insert into order_items values((select count(*) from order_items)+1, ?, ?, ?, ?)",
                (new_order_id, product_names[i], quantities[i], prices[i])
            )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(order_id):
        logger.info("Удаляется заказ")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("delete from orders where id = ?", (order_id,))
        cur.execute("delete from order_items where order_id = ?", (order_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_by_id(order_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""select
                    orders.order_date,
                    customers.name,
                    group_concat(order_items.product_name) as list,
                    group_concat(order_items.price) as list,
                    group_concat(order_items.quantity) as list,
                    orders.status
                from orders
                    join order_items on orders.id = order_items.order_id
                    join customers on orders.customer_id = customers.id
                where orders.id = ?
                group by orders.id""", (order_id,))
        order = cur.fetchone()
        conn.close()
        return order
    
    @staticmethod
    def update(order_id, date, client_name, product_names, prices, quantities, status):
        logger.info("Редактируется заказ")
        conn = get_connection()
        cur = conn.cursor()
        
        old_order = Order.get_by_id(order_id)
        
        if client_name != old_order[1]:
            cur.execute(
                "update orders set customer_id = (select id from customers where name = ?) where id = ?",
                (client_name, order_id)
            )
        
        old_names = old_order[2].split(',')
        old_prices = old_order[3].split(',')
        old_quantities = old_order[4].split(',')
        
        if not (product_names == old_names and 
                [str(p) for p in prices] == old_prices and 
                [str(q) for q in quantities] == old_quantities):
            
            total = reduce(lambda x, y: x + y, [p * q for p, q in zip(prices, quantities)])
            cur.execute("update orders set total = ? where id = ?", (total, order_id))
            cur.execute("delete from order_items where order_id = ?", (order_id,))
            
            for i in range(len(product_names)):
                cur.execute(
                    "insert into order_items values((select ifnull(max(id), 0) + 1 from order_items), ?, ?, ?, ?)",
                    (order_id, product_names[i], quantities[i], prices[i])
                )
        
        if date != old_order[0] or status != old_order[5]:
            cur.execute(
                "update orders set order_date = ?, status = ? where id = ?",
                (date, status, order_id)
            )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_revenue(period=None):
        conn = get_connection()
        cur = conn.cursor()
        
        query = "select sum(total) from orders"
        if period:
            periods = {'за день': '-0 days', 'за неделю': '-6 days', 'за месяц': '-30 days'}
            query += f" where order_date >= date('now', '{periods[period]}')"
        
        cur.execute(query)
        total = cur.fetchone()[0]
        conn.close()
        return total or 0
    
    @staticmethod
    def get_top_clients(limit=3):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""select sum(total) as sumi, customers.name 
                    from orders 
                    join customers on orders.customer_id = customers.id 
                    group by customer_id 
                    order by sumi desc 
                    limit ?""", (limit,))
        top = cur.fetchall()
        conn.close()
        return top
    
    @staticmethod
    def get_status_counts():
        conn = get_connection()
        cur = conn.cursor()
        statuses = ["новый", "в доставке", "выполнен", "отменён"]
        counts = []
        for status in statuses:
            cur.execute("select count(*) from orders where status = ?", (status,))
            count = cur.fetchone()[0]
            counts.append(count)
        conn.close()
        return statuses, counts
