#!/usr/bin/env python3
"""Основной скрипт мониторинга недвижимости с аналитикой"""
import sys
import os
import time
import random
from datetime import datetime
import logging

# Добавляем текущую директорию в путь
sys.path.insert(0, '/root/realty-monitor')

from storage import Storage
from parsers.pik_parser import parse_pik_kladovye
from parsers.pik_parking_parser import parse_pik_parking
from notifier import TelegramNotifier
from history import HistoryStorage
from analytics import Analytics
import config
from parsers.akvilon_parser import parse_akvilon_kladovye
from parsers.etalon_parser import parse_etalon_kladovye
from parsers.etalon_parking_parser import parse_etalon_parking
from parsers.akvilon_parking_parser import parse_akvilon_parking
from parsers.trest_parser import parse_trest_kladovye

# Настройка логирования
os.makedirs(config.LOGS_DIR, exist_ok=True)
log_file = os.path.join(config.LOGS_DIR, f'monitor_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_monitoring():
    """Запускает процесс мониторинга с аналитикой"""

    # Случайная задержка 0-15 минут перед началом (можно отключить через NO_DELAY=1)
    no_delay = os.environ.get('NO_DELAY', '0') == '1'

    if no_delay:
        delay_seconds = 0
        logger.info('=' * 60)
        logger.info('Запуск мониторинга недвижимости (БЕЗ ЗАДЕРЖКИ)')
        logger.info('=' * 60)
    else:
        delay_seconds = random.randint(0, 900)  # 0-15 минут
        delay_minutes = delay_seconds / 60

        logger.info('=' * 60)
        logger.info('Запуск мониторинга недвижимости')
        logger.info(f'Случайная задержка: {delay_minutes:.1f} минут')
        logger.info('=' * 60)

        if delay_seconds > 0:
            logger.info(f'Ожидание {delay_minutes:.1f} мин для естественности...')
            time.sleep(delay_seconds)

    logger.info('Начало работы')

    storage = Storage(config.DATA_DIR)
    notifier = TelegramNotifier()
    history = HistoryStorage(config.DATA_DIR)
    analytics = Analytics()

    total_new = 0
    all_alerts = []

    # Проходим по всем настроенным парсерам
    for source_id, parser_config in config.PARSERS.items():
        if not parser_config.get('enabled', True):
            logger.info(f'Парсер {source_id} отключен, пропускаем')
            continue

        source_name = parser_config.get('name', source_id)
        logger.info(f'\nОбработка источника: {source_name}')

        try:
            # Запускаем парсер
            logger.info(f'Запуск парсера {source_id}...')

            if source_id == 'akvilon_kladovye':
                current_projects = parse_akvilon_kladovye()
            elif source_id == 'akvilon_parking':
                current_projects = parse_akvilon_parking()
            elif source_id == 'etalon_kladovye':
                current_projects = parse_etalon_kladovye()
            elif source_id == 'etalon_parking':
                current_projects = parse_etalon_parking()
            elif source_id == 'trest_kladovye':
                current_projects = parse_trest_kladovye()
            elif source_id == 'pik_parking':
                current_projects = parse_pik_parking()
            elif source_id == 'pik_kladovye':
                current_projects = parse_pik_kladovye()
            else:
                logger.warning(f'Парсер для {source_id} не реализован')
                continue

            logger.info(f'Найдено проектов: {len(current_projects)}')

            # Сохраняем снимок в историю
            history.save_snapshot(current_projects)

            # Проверяем алерты (только для кладовых, не для парковок)
            if source_id not in ['etalon_parking', 'akvilon_parking', 'pik_parking']:
                logger.info('Проверка алертов...')

                # Алерт 1: малое количество (умные пороги: 25, 15, 10, 5, 2)
                low_qty_alerts = analytics.check_low_quantity_alert(current_projects)
                if low_qty_alerts:
                    logger.warning(f'Найдено {len(low_qty_alerts)} алертов по малому остатку')
                    all_alerts.extend(low_qty_alerts)

                # Алерт 2: большие продажи за 30 дней (>20)
                high_sales_alerts = analytics.check_high_sales_alert(current_projects, days=30, sold_threshold=20)
                if high_sales_alerts:
                    logger.warning(f'Найдено {len(high_sales_alerts)} алертов по высоким продажам')
                    all_alerts.extend(high_sales_alerts)
            else:
                logger.info('Проверка алертов пропущена (только отслеживание новых проектов для парковок)')

            # Проверяем наличие новых проектов
            new_projects = storage.find_new_projects(source_id, current_projects)

            if new_projects:
                logger.info(f'🎉 Найдено новых проектов: {len(new_projects)}')
                for project in new_projects:
                    name = project.get('name', 'Без названия').replace('\nСмотреть проект', '')
                    logger.info(f'  - {name}')

                # Отправляем уведомление
                notifier.notify_new_projects(source_name, new_projects)
                total_new += len(new_projects)
            else:
                logger.info('Новых проектов не найдено')

            # Сохраняем текущее состояние
            # Защита от ошибок парсинга: не сохраняем пустое состояние если раньше были проекты
            previous_count = storage.get_project_count(source_id)
            if len(current_projects) == 0 and previous_count > 0:
                logger.warning(f'⚠️ Парсер вернул 0 проектов, но раньше было {previous_count}. Пропускаем сохранение для защиты от ошибок парсинга.')
            else:
                storage.save_current_state(source_id, current_projects)
                logger.info(f'Состояние сохранено: {len(current_projects)} проектов')

        except Exception as e:
            logger.error(f'Ошибка при обработке {source_name}: {e}', exc_info=True)
            notifier.notify_error(source_name, str(e))

    # Отправляем все алерты одним сообщением
    if all_alerts:
        logger.info(f'\n🚨 Отправка {len(all_alerts)} алертов')
        notifier.notify_alerts(all_alerts)

    logger.info(f'\n' + '=' * 60)
    logger.info(f'Мониторинг завершен. Новых объектов: {total_new}, Алертов: {len(all_alerts)}')
    logger.info('=' * 60)

if __name__ == '__main__':
    try:
        run_monitoring()
    except Exception as e:
        logger.critical(f'Критическая ошибка: {e}', exc_info=True)
        sys.exit(1)
