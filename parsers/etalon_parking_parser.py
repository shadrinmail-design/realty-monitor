#!/usr/bin/env python3
"""
Парсер машиномест Эталон
"""
import sys
import random
import re
from collections import defaultdict
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

# Маппинг slug -> название проекта
SLUG_TO_NAME = {
    'ldm': 'ЛДМ',
    'kvartal-galaktika': 'Квартал Галактика',
    'domino': 'Domino',
    'pulkovskiy-dom': 'Пулковский дом',
    'lastochkino-gnezdo': 'Ласточкино гнездо',
    'carskaya-stolica': 'Царская столица',
    'tsarskaya-stolitsa': 'Царская столица',
    'yolki-parkovye': 'Ёлки Парковые',
    'moskovskie-vorota': 'Московские ворота',
    'novoorlovsky': 'Новоорловский',
    'molodezhnyy': 'Молодёжный',
    'orbita': 'Орбита',
    'yubileynyy-kvartal': 'Юбилейный квартал',
    'kvartal-che': 'Квартал Че',
}

def parse_etalon_parking():
    """Парсит страницу машиномест Эталон с подсчетом количества"""
    url = 'https://etalongroup.ru/spb/choose/parking/'

    try:
        user_agent = random.choice(USER_AGENTS)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            response = page.goto(url, wait_until='networkidle', timeout=60000)

            if response.status != 200:
                print(f'Ошибка: HTTP {response.status}', file=sys.stderr)
                return []

            page.wait_for_timeout(random.randint(2000, 4000))

            # Ищем все ссылки на парковки
            links = page.query_selector_all('a[href*="/parking/"]')

            # Собираем данные по проектам (slug -> количество)
            projects_data = defaultdict(lambda: {'count': 0, 'urls': []})

            for link in links:
                href = link.get_attribute('href') or ''
                
                # Извлекаем slug из URL формата /parking/{slug}/{id}/
                match = re.search(r'/parking/([^/]+)/(\d+)', href)
                if match:
                    slug = match.group(1)
                    
                    # Пропускаем служебные URL
                    if slug in ['plan']:
                        continue
                    
                    projects_data[slug]['count'] += 1
                    if href.startswith('http'):
                        projects_data[slug]['urls'].append(href)
                    else:
                        full_url = f'https://etalongroup.ru{href}'
                        projects_data[slug]['urls'].append(full_url)

            # Формируем результат
            projects = []

            for slug, data in projects_data.items():
                if data['count'] > 0:
                    # Получаем название проекта
                    project_name = SLUG_TO_NAME.get(slug, slug.replace('-', ' ').title())
                    
                    # Берем первый URL как представительный
                    project_url = f"https://etalongroup.ru/spb/choose/parking/{slug}/"

                    projects.append({
                        'name': f'Эталон - {project_name}',
                        'url': project_url,
                        'quantity': data['count'],
                        'type': 'parking'  # Маркер что это парковки
                    })

            browser.close()

            # Сортируем по количеству
            projects.sort(key=lambda x: -x['quantity'])

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
    projects = parse_etalon_parking()

    if projects:
        print(f'Найдено проектов с парковками: {len(projects)}')
        total_qty = sum(p['quantity'] for p in projects)
        print(f'Всего машиномест: {total_qty}\n')
        for p in projects:
            print(f"  {p['name']}: {p['quantity']} шт")
    else:
        print('Проекты не найдены')
