#!/usr/bin/env python3
"""Скрипт для отправки еженедельных отчетов"""
import sys
import os
import json
from datetime import datetime
import logging

sys.path.insert(0, '/root/realty-monitor')

from notifier import TelegramNotifier
import config

# Настройка логирования
os.makedirs(config.LOGS_DIR, exist_ok=True)
log_file = os.path.join(config.LOGS_DIR, f'weekly_report_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def load_data_from_files():
    """Загружает данные из сохраненных файлов"""
    data_files = {
        'Аквилон - Кладовые': 'data/akvilon_kladovye.json',
        'Аквилон - Парковки': 'data/akvilon_parking.json',
        'Эталон - Кладовые': 'data/etalon_kladovye.json',
        'Эталон - Парковки': 'data/etalon_parking.json',
        'ПИК - Кладовые': 'data/pik_kladovye.json',
        'ПИК - Парковки': 'data/pik_parking.json',
        'Строительный трест - Кладовые': 'data/trest_kladovye.json'
    }
    
    sources = {}
    for name, filepath in data_files.items():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                sources[name] = json.load(f)
            logger.info(f'Загружено {len(sources[name])} проектов из {name}')
        except FileNotFoundError:
            logger.warning(f'Файл не найден: {filepath}')
            sources[name] = []
        except Exception as e:
            logger.error(f'Ошибка загрузки {filepath}: {e}')
            sources[name] = []
    
    return sources

def format_report(sources):
    """Формирует развернутый отчет"""
    msg = '📊 <b>Еженедельный отчет по недвижимости</b>\n'
    msg += f'<i>{datetime.now().strftime("%d.%m.%Y")}</i>\n\n'
    
    # ПАРКОВКИ
    msg += '━━━━━━━━━━━━━━━━━━━━\n'
    msg += '<b>🚗 ПАРКОВКИ</b>\n'
    msg += '━━━━━━━━━━━━━━━━━━━━\n\n'
    
    parking_sources = [(k, v) for k, v in sources.items() if 'Парковки' in k]
    for source_name, projects in parking_sources:
        if projects:
            total = sum(p.get('quantity', 0) for p in projects)
            msg += f'<b>{source_name}</b>\n'
            msg += f'Всего: {len(projects)} проектов, {total} машиномест\n\n'
            
            for p in sorted(projects, key=lambda x: -x.get('quantity', 0)):
                name = p.get('name', 'Без названия').replace('Аквилон - ', '').replace('ПИК - ', '').replace('Эталон - ', '')
                qty = p.get('quantity', 0)
                msg += f'  • {name}: {qty} шт\n'
            msg += '\n'
    
    # КЛАДОВЫЕ  
    msg += '━━━━━━━━━━━━━━━━━━━━\n'
    msg += '<b>📦 КЛАДОВЫЕ</b>\n'
    msg += '━━━━━━━━━━━━━━━━━━━━\n\n'
    
    storage_sources = [(k, v) for k, v in sources.items() if 'Кладовые' in k]
    for source_name, projects in storage_sources:
        if projects:
            total = sum(p.get('quantity', 0) for p in projects)
            msg += f'<b>{source_name}</b>\n'
            msg += f'Всего: {len(projects)} проектов, {total} кладовых\n\n'
            
            for p in sorted(projects, key=lambda x: -x.get('quantity', 0)):
                name = p.get('name', 'Без названия').replace('ПИК - ', '')
                qty = p.get('quantity', 0)
                msg += f'  • {name}: {qty} шт\n'
            msg += '\n'
    
    msg += '<i>Автоматический еженедельный отчет</i>'
    
    return msg

def send_weekly_report():
    """Отправляет еженедельный отчет"""
    logger.info('=' * 60)
    logger.info('Формирование еженедельного отчета')
    logger.info('=' * 60)
    
    # Загружаем данные из файлов
    sources = load_data_from_files()
    
    # Формируем отчет
    message = format_report(sources)
    
    # Отправляем в Telegram
    notifier = TelegramNotifier()
    logger.info('Отправка отчета в Telegram...')
    
    result = notifier.send_message(message)
    
    if result:
        logger.info('✓ Отчет успешно отправлен!')
    else:
        logger.error('✗ Ошибка отправки отчета')
    
    logger.info('=' * 60)
    
    return result

if __name__ == '__main__':
    send_weekly_report()
