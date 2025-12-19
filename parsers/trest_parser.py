#!/usr/bin/env python3
"""
Парсер кладовых ТРЕСТ (версия 2 - через карточки)
"""
import sys
import random
import re
from collections import defaultdict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Список User-Agent для ротации
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
]

def parse_trest_kladovye():
    """Парсит страницу с кладовыми ТРЕСТ"""
    url = 'https://trest-group.ru/catalog/storeroom/'

    try:
        user_agent = random.choice(USER_AGENTS)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            # Переходим на страницу
            response = page.goto(url, wait_until='networkidle', timeout=30000)

            if response.status != 200:
                print(f'Ошибка: HTTP {response.status}', file=sys.stderr)
                return []

            # Случайная задержка 2-5 секунд
            page.wait_for_timeout(random.randint(2000, 5000))

            # Скроллим для подгрузки всех карточек
            for i in range(3):
                page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                page.wait_for_timeout(random.randint(1500, 2500))

            # Ищем все карточки
            cards = page.query_selector_all('div[class*=card]')

            project_counts = defaultdict(int)

            for card in cards:
                try:
                    text = card.inner_text()

                    # Извлекаем название проекта
                    # Проект идет в начале карточки (NEWПИТЕР, Наука, Парусная 1 и т.д.)
                    lines = text.strip().split('\n')

                    project_name = None
                    quantity = None

                    for line in lines:
                        line = line.strip()

                        # Ищем название проекта (обычно первая строка, не пустая)
                        if not project_name and line and len(line) > 2:
                            # Проверяем что это не служебные слова
                            if line not in ['Цена по запросу', 'Дом сдан', 'КВАРТИРА', 'ПАРКИНГ',
                                          'КЛАДОВЫЕ', 'НАЗЕМНЫЙ', 'ПОДЗЕМНЫЙ', 'КЛАДОВАЯ']:
                                # Проверяем формат названия проекта
                                if re.match(r'^[А-ЯЁ]', line) and not line.startswith('Количество'):
                                    project_name = line

                        # Ищем количество
                        if 'Количество мест в продаже:' in line:
                            match = re.search(r'Количество мест в продаже:\s*(\d+)', line)
                            if match:
                                quantity = int(match.group(1))
                                break

                    if project_name and quantity:
                        project_counts[project_name] += quantity

                except Exception as e:
                    continue

            # Формируем результат
            projects = []

            for project_name, quantity in project_counts.items():
                if quantity > 0:
                    project_url = f'https://trest-group.ru/catalog/storeroom/?complex={project_name}'

                    projects.append({
                        'name': f'Строительный трест - {project_name}',
                        'url': project_url,
                        'quantity': quantity
                    })

            browser.close()

            return projects

    except PlaywrightTimeoutError:
        print('Ошибка: Таймаут при загрузке страницы', file=sys.stderr)
        return []
    except Exception as e:
        print(f'Ошибка парсинга: {e}', file=sys.stderr)
        return []

if __name__ == '__main__':
    projects = parse_trest_kladovye()

    if projects:
        print(f'Найдено проектов: {len(projects)}')
        total_qty = sum(p['quantity'] for p in projects)
        print(f'Всего кладовых: {total_qty}')
        for p in projects:
            print(f"  - {p['name']}: {p['quantity']} шт")
            print(f"    URL: {p['url']}")
    else:
        print('Проекты не найдены')
