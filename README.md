Быстрая доставка
Приложение для учёта заказов компании
Функции приложения
1. Управление клиентами
- Имя, телефон, адрес.
- CRUD (создание, чтение, редактирование, удаление).
- Клиента нельзя удалить, если есть заказы.
2. Управление заказами
- Дата заказа, клиент (выбор из списка), список товаров, итоговая сумма.
- Статус заказа: «новый», «в доставке», «выполнен», «отменён».
- CRUD + фильтрация заказов по статусу и дате.
3. Отчёты и аналитика
- Количество заказов по статусам.
- Топ-3 клиента по сумме заказов.
- Общая выручка за период (день/неделя/месяц).
4. Экспорт / импорт
- Экспорт всех заказов в JSON (на выбор).
- Импорт заказов из JSON (с проверкой корректности).
5. Режимы работы
- CLI-режим (через argparse)
- GUI-режим (Tkinter)
Используемые технологии
•	Python 3.8+
•	SQLite
•	PyQt5
•	argparse
•	pytest
Структура проекта
delivery_system/
├── main_cli.py            # CLI-точка входа (argparse)
├── main_gui.py            # GUI-точка входа 
├── database.py            # Работа с БД (SQLite)
├── models.py              # Классы Customer, Order
├── data_export.py         # Экспорт/импорт JSON
├── logger_config.py       # Настройка логирования
|----- Qt_Designer/
|   |----- add_client.ui
|   |-----add_order.ui
|   |-----delete_order.ui
|   |-----orders.ui
├── tests/
│   ├── test_database.py
│   ├── test_models.py
│   |── test_export.py
|   |----- conftest.py
├── logs/                  # Папка для логов
├── data/
│   ├── delivery        # SQLite-файл
├── requirements.txt       
├── README.md            #(этот файлик)

Установка
pip install -r requirements.txt
Запуск визуального приложения
python main_gui.py
Работа с приложением через консоль
main_cli.py report --period day           # отчёт выручки за период(day/week/month)
main_cli.py export --table orders        # экспорт (orders – название таблицы)                       
main_cli.py import --table orders --file orders.json     #импорт(orders – название таблицы, а orders.json – файл из которого надо импортировать)
Тестирование
pytest tests/ -v
pytest --cov=models --cov=data_export --cov-report=term tests/
База данных
customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT
)
orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE RESTRICT,
    order_date TEXT NOT NULL,
    status TEXT CHECK(status IN ('новый','в доставке','выполнен','отменён')),
    total REAL NOT NULL
)

order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_name TEXT,
    quantity INTEGER,
    price REAL
)
