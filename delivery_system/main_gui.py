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




































