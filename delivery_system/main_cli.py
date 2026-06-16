#argparse
import sqlite3
import json
import sys
from functools import reduce
import argparse
import sys
from logger_config import logger
from data_export import export_table, import_table 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Управление заказами')
    subparsers = parser.add_subparsers(dest='command')
    
    # Подкоманда export
    export_parser = subparsers.add_parser('export', help='Экспорт таблицы в JSON/XML')
    export_parser.add_argument('--table', choices=['orders', 'customers', 'order_items'], 
                          help='Таблица для экспорта')

    # Подкоманда import
    import_parser = subparsers.add_parser('import', help='Импорт из JSON/XML')
    import_parser.add_argument('--table', choices=['orders', 'customers', 'order_items'], 
                          required=True, help='Таблица для импорта')
    import_parser.add_argument('--file', required=True, 
                          help='Путь к файлу (.json или .xml)')
    
    # Подкоманда report
    report_parser = subparsers.add_parser('report', help='Отчёт по выручке')
    report_parser.add_argument('--period', choices=['day', 'week', 'month'], required=True)
    
    args = parser.parse_args()
    
    if args.command == 'export':
        export_table(args.table)
        sys.exit(0)
    
    if args.command == 'import':
        import_table(args.table, args.file)
        sys.exit(0)
    
    if args.command == 'report':
        periods = {'day': '-0 days', 'week': '-6 days', 'month': '-30 days'}
        conn = sqlite3.connect('data/delivery')
        cur = conn.cursor()
        cur.execute(f"select sum(total) from orders where order_date >= date('now', '{periods[args.period]}')")
        print(f"Выручка за период: {cur.fetchone()[0]}")
        conn.close()
        sys.exit(0)
 
