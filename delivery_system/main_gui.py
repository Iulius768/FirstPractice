from logger_config import logger
from data_export import export_table, import_table
from models import Customer, Order

import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Qt_Designer/orders.ui', self)
        logger.info("Приложение запущено")
        self.orders.triggered.connect(self.show_orders)
        self.clients.triggered.connect(self.show_clients)
        self.reports.triggered.connect(self.show_reports)
        self.exports.triggered.connect(self.show_exports)
        self.show_orders()
        self.orders_filtrs.clicked.connect(self.onClick_orders_filtrs)
        self.add_order.clicked.connect(self.onClick_add_order)
        self.delete_order.clicked.connect(self.onClick_delete_order)
        self.edit_order.clicked.connect(self.onClick_edit_order)
        self.reload_orders.clicked.connect(self.onClick_reload_orders)
        self.reload_clients.clicked.connect(self.onClick_reload_clients)
        self.add_client.clicked.connect(self.onClick_add_client)
        self.delete_client.clicked.connect(self.onClick_delete_client)
        self.edit_client.clicked.connect(self.onClick_edit_client)
        self.countPeriods.clicked.connect(self.onClick_countPeriods)
        self.doexport.clicked.connect(self.onClick_doExport)
        self.doimport.clicked.connect(self.onClick_doImport)

    def onClick_doExport(self):
        tableName = self.exportBox.currentText()
        export_table(tableName)
        QMessageBox.information(self, "Успех", "Успешно экспортировано")

    def onClick_doImport(self):
        tableName = self.importBox.currentText()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите JSON файл", "", "JSON files (*.json)")
        if not file_path:
            return
        result = import_table(tableName, file_path)
        if result != 'ok':
            QMessageBox.critical(self, "Ошибка", result)
        else:
            QMessageBox.information(self, "Успех", "Успешно импортировано")

    def onClick_countPeriods(self):
        logger.info("Считается выручка за определённый срок")
        period = self.period.currentText()
        if period != 'за всё время':
            total = Order.get_revenue(period)
        else:
            total = Order.get_revenue()
        self.periodSumm.setText(str(total))

    def onClick_edit_client(self):
        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
        dialog.label.setText('Введите код клиента которого хотите редактировать')
        result = dialog.exec_()
        if result == 1:
            customer_id = dialog.lineEdit.text()
            client_info = Customer.get_by_id(customer_id)
            
            dialog = uic.loadUi('Qt_Designer/add_client.ui')
            dialog.number.setText(client_info[1])
            dialog.adress.setText(client_info[2])
            dialog.name.setText(client_info[0])
            result = dialog.exec_()
            if result == 1:
                Customer.update(
                    customer_id,
                    dialog.name.text(),
                    dialog.number.text(),
                    dialog.adress.text()
                )

    def onClick_add_client(self):
        dialog = uic.loadUi('Qt_Designer/add_client.ui')
        result = dialog.exec_()
        if result == 1:
            Customer.add(
                dialog.name.text(),
                dialog.number.text(),
                dialog.adress.text()
            )

    def onClick_delete_client(self):
        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
        dialog.label.setText('Введите код клиента которого надо удалить')
        result = dialog.exec_()
        if result == 1:
            customer_id = dialog.lineEdit.text()
            if not Customer.delete(customer_id):
                QMessageBox.critical(self, "Ошибка", "Клиента нельзя удалить, так как у него есть заказы")

    def onClick_reload_orders(self):
        self.show_orders()

    def onClick_reload_clients(self):
        self.show_clients()

    def onClick_edit_order(self):
        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
        dialog.label.setText('Введите код заказа который хотите редактировать')
        result = dialog.exec_()
        if result == 1:
            order_id = dialog.lineEdit.text()
            order_info = Order.get_by_id(order_id)
            
            dialog = uic.loadUi('Qt_Designer/add_order.ui')
            dialog.lineEdit.setText(order_info[0])
            dialog.lineEdit_2.setText(order_info[1])
            dialog.lineEdit_3.setText(order_info[2])
            dialog.lineEdit_4.setText(str(order_info[3]))
            dialog.lineEdit_5.setText(order_info[4])
            dialog.lineEdit_6.setText(order_info[5])
            result = dialog.exec_()
            if result == 1:
                Order.update(
                    order_id,
                    dialog.lineEdit.text(),
                    dialog.lineEdit_2.text(),
                    dialog.lineEdit_3.text().split(','),
                    [int(float(x)) for x in dialog.lineEdit_4.text().split(',')],
                    [int(x) for x in dialog.lineEdit_5.text().split(',')],
                    dialog.lineEdit_6.text()
                )

    def onClick_delete_order(self):
        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
        dialog.label.setText('Введите код заказа которого хотите удалить')
        result = dialog.exec_()
        if result == 1:
            order_id = dialog.lineEdit.text()
            Order.delete(order_id)

    def onClick_add_order(self):
        dialog = uic.loadUi('Qt_Designer/add_order.ui')
        result = dialog.exec_()
        if result == 1:
            Order.add(
                dialog.lineEdit.text(),
                dialog.lineEdit_2.text(),
                dialog.lineEdit_3.text().split(','),
                [int(float(x)) for x in dialog.lineEdit_4.text().split(',')],
                [int(x) for x in dialog.lineEdit_5.text().split(',')],
                dialog.lineEdit_6.text()
            )

    def onClick_orders_filtrs(self):
        filters = {}
        if self.comboBox.currentText() != 'all':
            filters['client'] = self.comboBox.currentText()
        if self.comboBox_2.currentText() != 'all':
            filters['status'] = self.comboBox_2.currentText()
        if self.checkBox_2.isChecked():
            filters['sort_by_date'] = True
        
        orders = Order.get_all(filters)
        self.tableWidget.setRowCount(0)
        
        header = [("Код", "Дата заказа", "Клиент", "Список товаров", "Итоговая сумма", "Статус заказа")]
        orders = header + orders
        
        for x in range(len(orders)):
            self.tableWidget.insertRow(x)
            for y in range(len(orders[x])):
                self.tableWidget.setItem(x, y, QTableWidgetItem(str(orders[x][y])))

    def show_orders(self):
        self.comboBox.clear()
        self.comboBox_2.clear()
        self.tableWidget.setRowCount(0)
        self.stackedWidget.setCurrentIndex(0)
        
        names = Customer.get_names()
        self.comboBox.addItems(['all'] + names)
        self.comboBox_2.addItems(['all', 'новый', 'в доставке', 'выполнен', 'отменён'])
        
        orders = Order.get_all()
        header = [("Код", "Дата заказа", "Клиент", "Список товаров", "Итоговая сумма", "Статус заказа")]
        orders = header + orders
        
        for x in range(len(orders)):
            self.tableWidget.insertRow(x)
            for y in range(len(orders[x])):
                self.tableWidget.setItem(x, y, QTableWidgetItem(str(orders[x][y])))

    def show_clients(self):
        self.tableWidget_2.setRowCount(0)
        self.stackedWidget.setCurrentIndex(1)
        
        clients = Customer.get_all()
        header = [("Код", "Имя", "Номер", "Адрес")]
        clients = header + clients
        
        for x in range(len(clients)):
            self.tableWidget_2.insertRow(x)
            for y in range(len(clients[x])):
                self.tableWidget_2.setItem(x, y, QTableWidgetItem(str(clients[x][y])))

    def show_reports(self):
        logger.info("Отображается статистика")
        self.period.clear()
        self.tableWidget_3.setRowCount(0)
        self.stackedWidget.setCurrentIndex(2)
        
        top = Order.get_top_clients()
        self.Num1.setText(f"1. {top[0][1]} ({top[0][0]})")
        self.Num2.setText(f"2. {top[1][1]} ({top[1][0]})")
        self.Num3.setText(f"3. {top[2][1]} ({top[2][0]})")
        
        total = Order.get_revenue()
        self.periodSumm.setText(str(total))
        self.period.addItems(['за всё время', 'за день', 'за неделю', 'за месяц'])
        
        statuses, counts = Order.get_status_counts()
        items = [statuses, counts]
        for x in range(len(items)):
            self.tableWidget_3.insertRow(x)
            for y in range(len(items[x])):
                self.tableWidget_3.setItem(x, y, QTableWidgetItem(str(items[x][y])))

    def show_exports(self):
        self.exportBox.clear()
        self.importBox.clear()
        self.stackedWidget.setCurrentIndex(3)
        self.exportBox.addItems(['orders', 'customers', 'order_items'])
        self.importBox.addItems(['orders', 'customers', 'order_items'])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())











































##from logger_config import logger
##from data_export import export_table, import_table
##
##import sqlite3
##import json
##import sys
##import os
##from functools import reduce
##from PyQt5 import QtWidgets, uic
##from PyQt5.QtWidgets import QMessageBox
##from PyQt5.QtWidgets import QFileDialog
##from PyQt5.QtWidgets import QTableWidgetItem
##
##
##class MainWindow(QtWidgets.QMainWindow):
##    def __init__(self):
##        super().__init__()
##        print(os.path.exists('data_export.py'))
##        uic.loadUi('Qt_Designer/orders.ui', self)
##        logger.info("Приложение запущено")
##        self.orders.triggered.connect(self.show_orders)
##        self.clients.triggered.connect(self.show_clients)
##        self.reports.triggered.connect(self.show_reports)
##        self.exports.triggered.connect(self.show_exports)
##        self.show_orders()
##        self.orders_filtrs.clicked.connect(self.onClick_orders_filtrs)
##        self.add_order.clicked.connect(self.onClick_add_order)
##        self.delete_order.clicked.connect(self.onClick_delete_order)
##        self.edit_order.clicked.connect(self.onClick_edit_order)
##        self.reload_orders.clicked.connect(self.onClick_reload_orders)
##        self.reload_clients.clicked.connect(self.onClick_reload_clients)
##        self.add_client.clicked.connect(self.onClick_add_client)
##        self.delete_client.clicked.connect(self.onClick_delete_client)
##        self.add_client.clicked.connect(self.onClick_add_client)
##        self.edit_client.clicked.connect(self.onClick_edit_client)
##        self.countPeriods.clicked.connect(self.onClick_countPeriods)
##        self.doexport.clicked.connect(self.onClick_doExport)
##        self.doimport.clicked.connect(self.onClick_doImport)
##
##    def onClick_doExport(self):
##        tableName = self.exportBox.currentText()
##        export_table(tableName)
##        msg.information(self, "Успех", "Успешно экспортировано")
##
##
##    def onClick_doImport(self):
##        tableName = self.importBox.currentText()
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        file_path, _ = QFileDialog.getOpenFileName(self,"Выберите JSON файл", "","JSON files (*.json)")
##        if not file_path:
##            return
##        a = import_table(tableName, file_path)
##        if a != 'ok':
##            QMessageBox.critical(self, "Ошибка", a)
##        else:
##            msg = QMessageBox()
##            msg.information(self, "Успех", "Успешно импортировано")
##    
##
##    def onClick_countPeriods(self):
##        logger.info("Считается выручка за определённый срок")
##        period = self.period.currentText()
##        a = ''
##        if period == 'за день':
##            a = """where order_date >= date('now', '-0 days')"""
##        elif period == 'за неделю':
##            a = """where order_date >= date('now', '-6 days')"""
##        elif period == 'за месяц':
##            a = """where order_date >= date('now', '-30 days')"""
##        stmt = """select sum(total) from orders """+a
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        cur.execute(stmt)
##        period_total = cur.fetchone()[0]
##        self.periodSumm.setText(str(period_total))
##
##
##        
##    def onClick_edit_client(self):
##        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
##        dialog.label.setText('Введите код клиента которого хотите редактировать')
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Редактируется клиент")
##            customer_id = dialog.lineEdit.text()
##            stmt = f"""select name, phone, address from customers where id = {customer_id}"""
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            cur.execute(stmt)
##            client_info = cur.fetchone()
##            dialog = uic.loadUi('Qt_Designer/add_client.ui')
##            dialog.number.setText(client_info[1])
##            dialog.adress.setText(client_info[2])
##            dialog.name.setText(client_info[0])
##            result = dialog.exec_()
##            if result == 1:
##                name = dialog.name.text()
##                number = dialog.number.text()
##                adress = dialog.adress.text()
##                stmt = f"""update customers set name = '{name}', phone = '{number}', address = '{adress}' where id = {customer_id}"""
##                cur.execute(stmt)
##                conn.commit()
##
##    def onClick_add_client(self):
##        dialog = uic.loadUi('Qt_Designer/add_client.ui')
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Добавляется клиент")
##            name = dialog.name.text()
##            number = dialog.number.text()
##            adress = dialog.adress.text()
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            stmt = f"""insert into customers values((select ifnull(max(id), 0) + 1 from customers), '{name}', '{number}', '{adress}')"""
##            cur.execute(stmt)
##            conn.commit()
##
##    def onClick_delete_client(self):
##        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
##        dialog.label.setText('Введите код клиента которого надо удалить')
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Удаляется клиент")
##            customer_id = dialog.lineEdit.text()
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            stmt = f"""select count(*) from orders where customer_id = {customer_id}"""
##            cur.execute(stmt)
##            if cur.fetchone()[0] == 0:
##                stmt = f"""delete from customers where id = {customer_id}"""
##                cur.execute(stmt)
##                conn.commit()
##            else:
##                QMessageBox.critical(self, "Ошибка", "Клиента нельзя удалить, так как у него есть заказы")
##
##
##    def onClick_reload_orders(self):
##        self.show_orders()
##
##    def onClick_reload_clients(self):
##        self.show_clients()
##
##
##    def onClick_edit_order(self):
##        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
##        dialog.label.setText('Введите код заказа который хотите редактировать')
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Редактируется заказ")
##            order_id = dialog.lineEdit.text()
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            stmt = f"""select
##                    orders.order_date,
##                    customers.name,
##                    group_concat(order_items.product_name) as list,
##                    group_concat(order_items.price) as list,
##                    group_concat(order_items.quantity) as list,
##                    orders.status
##                from orders
##                    join order_items on orders.id = order_items.order_id
##                    join customers on orders.customer_id = customers.id where orders.id = """+order_id+  """ group by orders.id"""
##            cur.execute(stmt)
##            order_info = cur.fetchone()
##            dialog = uic.loadUi('Qt_Designer/add_order.ui')
##            dialog.lineEdit.setText(order_info[0])
##            dialog.lineEdit_2.setText(order_info[1])
##            dialog.lineEdit_3.setText(order_info[2])
##            dialog.lineEdit_4.setText(str(order_info[3]))
##            dialog.lineEdit_5.setText(order_info[4])
##            dialog.lineEdit_6.setText(order_info[5])
##            result = dialog.exec_()
##            if result == 1:
##                date = dialog.lineEdit.text()
##                client = dialog.lineEdit_2.text()
##                list_names = dialog.lineEdit_3.text().split(',')
##                list_cost = dialog.lineEdit_4.text().split(',')
##                list_numbers = dialog.lineEdit_5.text().split(',')
##                status = dialog.lineEdit_6.text()
##
##                list_cost = list(map(lambda x: int(float(x)), list_cost))
##                if client != order_info[1]:
##                    stmt = f"""update orders set customer_id = (select id from customers where name = '{client}') where orders.id = {order_id}"""
##                    cur.execute(stmt)
##                    conn.commit()
##                if not(order_info[2].split(',')==list_names and order_info[3].split(',')==list_cost and order_info[4].split(',')==list_numbers):
##                    list_numbers = list(map(int, list_numbers))
##                    total = reduce(lambda x,y: x+y, (list(map(lambda z,u: z*u, list_cost,list_numbers))))
##                    stmt = f"""update orders set total = {total} where orders.id = {order_id}"""
##                    cur.execute(stmt)
##                    stmt = f"""delete from order_items where order_id = {order_id}"""
##                    cur.execute(stmt)
##                    for x in range(len(list_names)):
##                        stmt = f"""insert into order_items values((select ifnull(max(id), 0) + 1 from order_items), {order_id}, '{list_names[x]}', {list_numbers[x]}, {list_cost[x]})"""
##                        cur.execute(stmt)
##                if not(order_info[0]==date and order_info[5]==status):
##                    stmt = f"""update orders set order_date = '{date}', status = '{status}' where orders.id = {order_id}"""
##                    cur.execute(stmt)
##                conn.commit()
##
##        
##    def onClick_delete_order(self):
##        dialog = uic.loadUi('Qt_Designer/delete_order.ui')
##        dialog.label.setText('Введите код заказа которого хотите удалить')
##        
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Удаляется заказ")
##            order_id = dialog.lineEdit.text()
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            stmt = f"""delete from orders where id = {order_id}"""
##            cur.execute(stmt)
##            stmt = f"""delete from order_items where order_id = {order_id}"""
##            cur.execute(stmt)
##            conn.commit()
##
##            
##    def onClick_add_order(self):
##        dialog = uic.loadUi('Qt_Designer/add_order.ui')
##        result = dialog.exec_()
##        if result == 1:
##            logger.info("Добавляется заказ")
##            date = dialog.lineEdit.text()
##            client = dialog.lineEdit_2.text()
##            list_names = dialog.lineEdit_3.text().split(',')
##            list_cost = list(map(lambda x: int(float(x)), dialog.lineEdit_4.text().split(',')))
##            list_numbers = list(map(int, (dialog.lineEdit_5.text()).split(',')))
##            total = reduce(lambda x,y: x+y, (list(map(lambda z,u: z*u, list_cost,list_numbers))))
##            status = dialog.lineEdit_6.text()
##            conn = sqlite3.connect('data/delivery')
##            cur = conn.cursor()
##            stmt = f"""insert into orders values((select count(*) from orders)+1, (select id from customers where name = '{client}'), '{date}', '{status}', {total}) returning id"""
##            cur.execute(stmt)
##            new_order_id = cur.fetchone()[0]
##            for x in range(len(list_names)):
##                stmt = f"""insert into order_items values((select count(*) from order_items)+1, {new_order_id}, '{list_names[x]}', {list_numbers[x]}, {list_cost[x]})"""
##                cur.execute(stmt)
##            conn.commit()
##
##
##        
##    def onClick_orders_filtrs(self):
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        value_client = self.comboBox.currentText()
##        value_status = self.comboBox_2.currentText()
##        
##        self.tableWidget.setRowCount(0)
##        name, status = '', ''
##        s = ''
##        if value_client != 'all':
##            name = f""" where customers.name = '{value_client}' """
##        if value_status != 'all':
##            s = ' where '
##            status = f""" orders.status = '{value_status}' """
##        date_filtr = ''
##        if self.checkBox_2.isChecked():
##            date_filtr = ' order by orders.order_date DESC'
##        if value_client != 'all' and value_status != 'all':
##            s = ' AND '
##        stmt = f"""select
##                    orders.id,
##                    orders.order_date,
##                    customers.name,
##                    group_concat(order_items.product_name) as list,
##                    orders.total,
##                    orders.status
##                from orders
##                    join order_items on orders.id = order_items.order_id
##                    join customers on orders.customer_id = customers.id""" + name + s + status+ """ group by orders.id""" + date_filtr
##        cur.execute(stmt)
##        orders = [("Код", "Дата заказа", "Клиент", "Список товаров", "Итоговая сумма", "Статус заказа")]+ cur.fetchall()
##
##        for x in range(len(orders)):
##            self.tableWidget.insertRow(x)
##            for y in range(len(orders[x])):
##                self.tableWidget.setItem(x, y, QTableWidgetItem(str(orders[x][y])))
##
##    def show_orders(self):
##        self.comboBox.clear()
##        self.tableWidget.setRowCount(0)
##        self.stackedWidget.setCurrentIndex(0)
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##
##        stmt = """select name from customers"""
##        cur.execute(stmt)
##        self.comboBox.addItems(['all']+list(map(lambda x: x[0], cur.fetchall())))
##        self.comboBox_2.addItems(['all', 'новый', 'в доставке', 'выполнен', 'отменён'])
##        stmt = """select
##                    orders.id,
##                    orders.order_date,
##                    customers.name,
##                    group_concat(order_items.product_name) as list,
##                    orders.total,
##                    orders.status
##                from orders
##                    join order_items on orders.id = order_items.order_id
##                    join customers on orders.customer_id = customers.id
##                group by orders.id"""
##        cur.execute(stmt)
##    
##        orders = [("Код", "Дата заказа", "Клиент", "Список товаров", "Итоговая сумма", "Статус заказа")]+ cur.fetchall()
##        for x in range(len(orders)):
##            self.tableWidget.insertRow(x)
##            for y in range(len(orders[x])):
##                self.tableWidget.setItem(x, y, QTableWidgetItem(str(orders[x][y])))
##        
##    def show_clients(self):
##        self.tableWidget_2.setRowCount(0)
##        self.stackedWidget.setCurrentIndex(1)
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        stmt = """select id, name, phone, address from customers"""
##        cur.execute(stmt)
##        clients = [("Код", "Имя", "Номер", "Адрес")]+ cur.fetchall()
##        for x in range(len(clients)):
##            self.tableWidget_2.insertRow(x)
##            for y in range(len(clients[x])):
##                self.tableWidget_2.setItem(x, y, QTableWidgetItem(str(clients[x][y])))
##
##
##    def get_num_of_status(self, status):
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        stmt = f"""select count(*) as num from orders where status = '{status}' group by status"""
##        cur.execute(stmt)
##        num = cur.fetchone()
##        if num:
##            return num[0]
##        return 0
##        
##    def show_reports(self):
##        logger.info("Отображается статистика")
##        self.period.clear()
##        self.tableWidget_3.setRowCount(0)
##        self.stackedWidget.setCurrentIndex(2)
##        conn = sqlite3.connect('data/delivery')
##        cur = conn.cursor()
##        stmt = f"""select sum(total) as sumi, orders.customer_id, customers.name from orders join customers on orders.customer_id = customers.id group by customer_id  order by sumi desc limit 3"""
##        cur.execute(stmt)
##        best = cur.fetchall()
##        self.Num1.setText(f"1. {best[0][2]} ({best[0][0]})")
##        self.Num2.setText(f"2. {best[1][2]} ({best[1][0]})")
##        self.Num3.setText(f"3. {best[2][2]} ({best[2][0]})")
##        stmt = f"""select sum(total) as sumi from orders"""
##        cur.execute(stmt)
##        summ = cur.fetchone()
##        self.periodSumm.setText(str(summ[0]))
##        self.period.addItems(['за всё время', 'за день', 'за неделю', 'за месяц'])
##        items = [["новый", "в доставке", "выполнен", "отменён"]]+ [list(map(self.get_num_of_status, ["новый", "в доставке", "выполнен", "отменён"]))]
##        for x in range(len(items)):
##            self.tableWidget_3.insertRow(x)
##            for y in range(len(items[x])):
##                self.tableWidget_3.setItem(x, y, QTableWidgetItem(str(items[x][y])))
##
##    def show_exports(self):
##        self.exportBox.clear()
##        self.importBox.clear()
##        self.stackedWidget.setCurrentIndex(3)
##        self.exportBox.addItems(['orders', 'customers', 'order_items'])
##        self.importBox.addItems(['orders', 'customers', 'order_items'])
##        
##
##
##if __name__ == "__main__":
##    app = QtWidgets.QApplication(sys.argv)
##    window = MainWindow()
##    window.show()
##    sys.exit(app.exec_())
