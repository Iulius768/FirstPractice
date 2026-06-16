import logging
import os
from datetime import datetime

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
log_filename = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y-%m-%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('MainGUI')
