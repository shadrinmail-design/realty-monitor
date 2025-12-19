#!/usr/bin/env python3
"""Тест системы умных алертов"""
import sys
sys.path.insert(0, '/root/realty-monitor')

from alert_state import AlertState

# Создаем тестовые данные
alert_state = AlertState()

# Тестируем разные сценарии
test_cases = [
    ('url1', 'ЖК Тест 1', 24),  # Первый раз < 25
    ('url1', 'ЖК Тест 1', 23),  # Стабильно, не алертим
    ('url1', 'ЖК Тест 1', 14),  # Порог 15 - алертим
    ('url1', 'ЖК Тест 1', 13),  # Стабильно, не алертим
    ('url2', 'ЖК Тест 2', 30),  # Выше порога, не алертим
    ('url2', 'ЖК Тест 2', 9),   # Сразу < 10 - алертим с порогом 10
]

print('=== ТЕСТ УМНЫХ АЛЕРТОВ ===\n')
for url, name, quantity in test_cases:
    should_alert, threshold = alert_state.should_alert(url, name, quantity)
    status = '🚨 АЛЕРТ' if should_alert else '✓ Тишина'
    threshold_msg = f'(порог {threshold})' if threshold else ''
    print(f'{status} | {name}: {quantity} кладовых {threshold_msg}')

print('\n=== СОСТОЯНИЕ ПОСЛЕ ТЕСТОВ ===')
import json
state = alert_state.load_state()
print(json.dumps(state, ensure_ascii=False, indent=2))
