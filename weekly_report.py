#!/usr/bin/env python3
"""Скрипт для отправки еженедельных отчетов по всем застройщикам"""
import sys
import os
from datetime import datetime
import logging

sys.path.insert(0, '/root/realty-monitor')

from notifier import TelegramNotifier
from analytics import Analytics
import config
from parsers.akvilon_parser import parse_akvilon_kladovye
from parsers.etalon_parser import parse_etalon_kladovye
from parsers.trest_parser import parse_trest_kladovye
from parsers.pik_parser import parse_pik_kladovye
from parsers.pik_parking_parser import parse_pik_parking

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

def format_weekly_report_message(all_sources_data):
    """Формирует текст еженедельного отчета для всех застройщиков"""
    
    message = f'📊 <b>Еженедельный отчет по кладовым</b>\n'
    message += f'📅 {datetime.now().strftime("%d.%m.%Y")}\n\n'
    
    # Общая статистика
    total_projects = sum(data['count'] for data in all_sources_data.values())
    total_quantity = sum(data['total_quantity'] for data in all_sources_data.values())
    
    message += f'<b>📈 Общая статистика:</b>\n'
    message += f'• Застройщиков: {len(all_sources_data)}\n'
    message += f'• Всего проектов: {total_projects}\n'
    message += f'• Всего кладовых: {total_quantity}\n\n'
    
    # Детали по каждому застройщику
    for source_name, data in all_sources_data.items():
        message += f'<b>🏢 {source_name}</b>\n'
        message += f'   Проектов: {data["count"]} | Кладовых: {data["total_quantity"]}\n'
        
        # ВСЕ проекты, сортированные по количеству
        all_projects = sorted(
            data['projects'], 
            key=lambda x: x.get('quantity') or 0, 
            reverse=True
        )
        
        for proj in all_projects:
            qty = proj.get('quantity') or 0
            name = proj.get('name', 'Без названия').replace('\nСмотреть проект', '')
            # Обрезаем слишком длинные названия
            if len(name) > 45:
                name = name[:42] + '...'
            message += f'   • {name}: {qty} шт\n'
        
        message += '\n'
    
    message += f'<i>Следующий отчет: в следующий понедельник</i>'
    
    return message

def send_weekly_report():
    """Отправляет еженедельный отчет по всем застройщикам"""
    logger.info('=' * 60)
    logger.info('Формирование еженедельного отчета')
    logger.info('=' * 60)
    
    all_sources_data = {}
    
    # Собираем данные со всех источников
    for source_id, parser_config in config.PARSERS.items():
        if not parser_config.get('enabled', True):
            continue
        
        source_name = parser_config.get('name', source_id)
        logger.info(f'\nСбор данных: {source_name}')
        
        try:
            # Запускаем парсер
            if source_id == 'akvilon_kladovye':
                projects = parse_akvilon_kladovye()
            elif source_id == 'etalon_kladovye':
                projects = parse_etalon_kladovye()
            elif source_id == 'trest_kladovye':
                projects = parse_trest_kladovye()
        elif source_id == 'pik_parking':
            current_projects = parse_pik_parking()
            elif source_id == 'pik_kladovye':
                projects = parse_pik_kladovye()
            else:
                logger.warning(f'Парсер для {source_id} не реализован')
                continue
            
            total_quantity = sum(p.get('quantity') or 0 for p in projects)
            
            all_sources_data[source_name] = {
                'count': len(projects),
                'total_quantity': total_quantity,
                'projects': projects
            }
            
            logger.info(f'✓ {source_name}: {len(projects)} проектов, {total_quantity} кладовых')
            
        except Exception as e:
            logger.error(f'✗ Ошибка при парсинге {source_name}: {e}')
            all_sources_data[source_name] = {
                'count': 0,
                'total_quantity': 0,
                'projects': [],
                'error': str(e)
            }
    
    # Формируем и отправляем отчет
    if all_sources_data:
        message = format_weekly_report_message(all_sources_data)
        
        logger.info('\n' + '=' * 60)
        logger.info('Отправка отчета в Telegram')
        logger.info('=' * 60)
        
        notifier = TelegramNotifier()
        success = notifier.send_message(message)
        
        if success:
            logger.info('✓ Еженедельный отчет успешно отправлен')
        else:
            logger.warning('! Telegram не настроен, отчет выведен в лог')
            logger.info('\n--- Предпросмотр отчета ---')
            logger.info(message.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', ''))
            logger.info('---------------------------')
    else:
        logger.error('Нет данных для отчета')
        sys.exit(1)
    
    logger.info('\n' + '=' * 60)
    logger.info('Еженедельный отчет завершен')
    logger.info('=' * 60)

if __name__ == '__main__':
    send_weekly_report()
