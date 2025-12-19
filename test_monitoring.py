#!/usr/bin/env python3
"""Тестовый запуск парсеров без задержки"""
import sys
sys.path.insert(0, '/root/realty-monitor')

from parsers.akvilon_parser import parse_akvilon_kladovye
from parsers.etalon_parser import parse_etalon_kladovye
from parsers.trest_parser import parse_trest_kladovye
from parsers.pik_parser import parse_pik_kladovye
import config

print('='*60)
print('ТЕСТОВЫЙ ЗАПУСК ПАРСЕРОВ')
print('='*60)

for source_id, parser_config in config.PARSERS.items():
    if not parser_config.get('enabled', True):
        continue

    source_name = parser_config.get('name', source_id)
    print(f'\n{source_name}:')
    print('-'*60)

    try:
        if source_id == 'akvilon_kladovye':
            projects = parse_akvilon_kladovye()
        elif source_id == 'etalon_kladovye':
            projects = parse_etalon_kladovye()
        elif source_id == 'trest_kladovye':
            projects = parse_trest_kladovye()
        elif source_id == 'pik_kladovye':
            projects = parse_pik_kladovye()
        else:
            print(f'  Парсер не реализован')
            continue

        print(f'  Найдено проектов: {len(projects)}')

        total_qty = sum(p.get('quantity', 0) or 0 for p in projects)
        print(f'  Общее количество кладовых: {total_qty}')

        for p in projects[:5]:
            qty_str = str(p.get('quantity', 'н/д'))
            print(f'    - {p["name"]}: {qty_str} шт')

        if len(projects) > 5:
            print(f'    ... и еще {len(projects)-5} проектов')

    except Exception as e:
        print(f'  ❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '='*60)
print('ТЕСТ ЗАВЕРШЕН')
print('='*60)
