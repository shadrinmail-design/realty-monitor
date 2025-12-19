"""Конфигурация системы мониторинга"""
import os

# Telegram настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Пути
DATA_DIR = '/root/realty-monitor/data'
LOGS_DIR = '/root/realty-monitor/logs'

# Настройки парсеров
PARSERS = {
    'akvilon_kladovye': {
        'enabled': True,
        'url': 'https://group-akvilon.ru/novostroyki/kladovye/',
        'name': 'Аквилон - Кладовые',
        'parser_module': 'parsers.akvilon_parser',
        'parser_function': 'parse_akvilon_kladovye'
    },
    'etalon_kladovye': {
        'enabled': True,
        'url': 'https://etalongroup.ru/spb/choose/storage/',
        'name': 'Эталон - Кладовые',
        'parser_module': 'parsers.etalon_parser',
        'parser_function': 'parse_etalon_kladovye'
    },
    'etalon_parking': {
        'enabled': True,
        'url': 'https://etalongroup.ru/spb/choose/parking/',
        'name': 'Эталон - Парковки',
        'parser_module': 'parsers.etalon_parking_parser',
        'parser_function': 'parse_etalon_parking'
    },
    'trest_kladovye': {
        'enabled': True,
        'url': 'https://trest-group.ru/catalog/storeroom/',
        'name': 'Строительный трест - Кладовые',
        'parser_module': 'parsers.trest_parser',
        'parser_function': 'parse_trest_kladovye'
    },
    'pik_kladovye': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/storehouse',
        'name': 'ПИК - Кладовые',
        'parser_module': 'parsers.pik_parser',
        'parser_function': 'parse_pik_kladovye'
    }
}

# Расписание (для справки, используется cron)
SCHEDULE = {
    'times': ['10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],  # МСК
    'timezone': 'Europe/Moscow'
}
