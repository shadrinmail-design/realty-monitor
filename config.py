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
    'akvilon_parking': {
        'enabled': True,
        'url': 'https://group-akvilon.ru/novostroyki/parkingi/',
        'name': 'Аквилон - Парковки',
        'parser_module': 'parsers.akvilon_parking_parser',
        'parser_function': 'parse_akvilon_parking'
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
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
        'enabled': True,
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
        'url': 'https://www.pik.ru/search/spb/storehouse',
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
        'name': 'ПИК - Кладовые',
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
        'parser_module': 'parsers.pik_parser',
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
        'parser_function': 'parse_pik_kladovye'
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
    }
    'pik_parking': {
        'enabled': True,
        'url': 'https://www.pik.ru/search/spb/cars',
        'name': 'ПИК - Парковки',
        'parser_module': 'parsers.pik_parking_parser',
        'parser_function': 'parse_pik_parking'
    },
}

# Расписание (для справки, используется cron)
SCHEDULE = {
    'times': ['10:00', '12:00', '14:00', '16:00', '18:00', '20:00'],  # МСК
    'timezone': 'Europe/Moscow'
}
