#!/usr/bin/env python3
"""Парсер машиномест ПИК"""
import sys
import random
import re
from collections import defaultdict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def parse_pik_parking():
    """Парсит страницу с машиноместами ПИК"""
    url = 'https://www.pik.ru/search/spb/cars'

    try:
        user_agent = random.choice(USER_AGENTS)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            
            page = context.new_page()
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)

            if response.status != 200:
                print(f'Ошибка: HTTP {response.status}', file=sys.stderr)
                return []

            page.wait_for_timeout(random.randint(3000, 5000))

            # Скроллим для загрузки всех карточек
            for _ in range(5):
                page.evaluate('window.scrollBy(0, window.innerHeight)')
                page.wait_for_timeout(1000)

            # Получаем текст
            text = page.inner_text('body')
            
            # Парсим проекты
            projects_data = defaultdict(int)
            
            lines = text.split('\n')
            current_project = None
            in_project_block = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Начало блока проекта
                if line == "Быстрый просмотр":
                    in_project_block = True
                    current_project = None
                    continue
                
                # Ищем название проекта
                if in_project_block and current_project is None:
                    if not line:
                        continue
                    if (len(line) > 2 and len(line) < 60 and 
                        'мин' not in line and 
                        'От' not in line and 
                        '₽' not in line and
                        not line.isdigit() and
                        not re.match(r'^\d+\s*м', line)):
                        current_project = line
                        continue
                
                # Считаем машиноместа
                if current_project and re.match(r'Машино-место,\s*[\d.]+\s*м²', line):
                    projects_data[current_project] += 1
                
                # Конец блока проекта
                if current_project and (line == "Показать все" or line.startswith("Показать ещё")):
                    in_project_block = False

            # Формируем результат
            projects = []

            for project_name, quantity in projects_data.items():
                if quantity > 0:
                    projects.append({
                        'name': f'ПИК - {project_name}',
                        'url': f'https://www.pik.ru/search/spb/cars?project={project_name.replace(" ", "-").lower()}',
                        'quantity': quantity,
                        'type': 'parking'
                    })

            browser.close()

            projects.sort(key=lambda x: -x['quantity'])

            print(f'Найдено проектов с паркингами: {len(projects)}')
            for p in projects:
                print(f"  {p['name']}: {p['quantity']} машиномест")

            return projects

    except PlaywrightTimeoutError:
        print('Ошибка: Таймаут при загрузке страницы', file=sys.stderr)
        return []
    except Exception as e:
        print(f'Ошибка парсинга: {e}', file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []

if __name__ == '__main__':
    projects = parse_pik_parking()
    if projects:
        total_qty = sum(p['quantity'] for p in projects)
        print(f'\nВсего машиномест: {total_qty}')
