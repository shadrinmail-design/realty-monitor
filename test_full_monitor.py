#!/usr/bin/env python3
"""Полный тест мониторинга с аналитикой (без задержки)"""
import sys
import os
sys.path.insert(0, '/root/realty-monitor')

from storage import Storage
from notifier import TelegramNotifier
from history import HistoryStorage
from analytics import Analytics
import config
from parsers.akvilon_parser import parse_akvilon_kladovye
from parsers.etalon_parser import parse_etalon_kladovye

print('='*60)
print('ПОЛНЫЙ ТЕСТ СИСТЕМЫ МОНИТОРИНГА')
print('='*60)

storage = Storage(config.DATA_DIR)
history = HistoryStorage(config.DATA_DIR)
analytics = Analytics()

for source_id, parser_config in config.PARSERS.items():
    if not parser_config.get('enabled', True):
        continue

    source_name = parser_config.get('name', source_id)
    print(f'\n{source_name}:')
    print('-'*60)

    try:
        if source_id == 'akvilon_kladovye':
            current_projects = parse_akvilon_kladovye()
        elif source_id == 'etalon_kladovye':
            current_projects = parse_etalon_kladovye()
        else:
            continue

        print(f'Найдено проектов: {len(current_projects)}')

        # Сохраняем в историю
        history.save_snapshot(current_projects)
        print('✅ Снимок сохранен в историю')

        # Проверяем алерты
        print('\nПроверка алертов...')

        # Алерт 1: малое количество
        low_qty_alerts = analytics.check_low_quantity_alert(current_projects)
        if low_qty_alerts:
            print(f'  ⚠️ Алертов по малому остатку: {len(low_qty_alerts)}')
            for alert in low_qty_alerts[:3]:
                print(f"    - {alert['project_name']}: {alert['quantity']} шт (порог {alert.get('threshold', '?')})")
        else:
            print('  ✅ Алертов по малому остатку нет')

        # Алерт 2: большие продажи
        high_sales_alerts = analytics.check_high_sales_alert(current_projects, days=30, sold_threshold=20)
        if high_sales_alerts:
            print(f'  ⚠️ Алертов по высоким продажам: {len(high_sales_alerts)}')
        else:
            print('  ✅ Алертов по высоким продажам нет')

    except Exception as e:
        print(f'❌ Ошибка: {e}')
        import traceback
        traceback.print_exc()

print('\n' + '='*60)
print('ТЕСТ ЗАВЕРШЕН УСПЕШНО')
print('='*60)
