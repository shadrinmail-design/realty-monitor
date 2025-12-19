#!/usr/bin/env python3
"""
Универсальный парсер кладовых Эталон
Автоматически находит все проекты на странице
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
]

# Маппинг slug -> название проекта
SLUG_TO_NAME = {
    'ldm': 'ЛДМ',
    'domino': 'Domino',
    'novoorlovsky': 'Новоорловский',
    'pulkovskiy-dom': 'Пулковский дом',
    'lastochkino-gnezdo': 'Ласточкино гнездо',
    'tsarskaya-stolitsa': 'Царская столица',
    'moskovskie-vorota': 'Московские ворота',
    'yagodnoe-reka-park': 'Ягодное Река Парк',
    'klyukva_park': 'Клюква.Парк',
    'kvartal-galaktika': 'Квартал «Галактика»',
    'monografiya': 'Монография'
}

def parse_etalon_kladovye():
    """Парсит страницу с кладовыми Эталон - универсально находит все проекты"""
    url = 'https://etalongroup.ru/spb/choose/storage/'

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

            # Случайная задержка 2-4 секунды
            page.wait_for_timeout(random.randint(2000, 4000))

            # Кликаем на все кнопки "Показать еще" для загрузки всех кладовых
            clicks = 0
            max_clicks = 30

            while clicks < max_clicks:
                buttons = page.query_selector_all('button, a')
                show_more = None

                for btn in buttons:
                    try:
                        text = btn.inner_text()
                        if 'Показать еще' in text or 'показать еще' in text.lower():
                            show_more = btn
                            break
                    except:
                        pass

                if not show_more:
                    break

                try:
                    show_more.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    show_more.click()
                    clicks += 1
                    page.wait_for_timeout(random.randint(800, 1500))
                except:
                    break

            # Находим все ссылки на кладовые
            links = page.query_selector_all('a[href*="/storage/"]')

            # Группируем по проектам
            projects_data = defaultdict(lambda: {'count': 0, 'urls': []})

            for link in links:
                href = link.get_attribute('href') or ''
                # Формат: /spb/choose/storage/{slug}/{id}/
                match = re.search(r'/storage/([^/]+)/(\d+)', href)
                if match:
                    slug = match.group(1)
                    projects_data[slug]['count'] += 1
                    if not projects_data[slug]['urls']:
                        projects_data[slug]['urls'].append(href)

            # Формируем результат
            projects = []

            for slug, data in projects_data.items():
                if data['count'] > 0:
                    # Берем название из маппинга или используем slug
                    project_name = SLUG_TO_NAME.get(slug, slug.replace('-', ' ').title())
                    
                    # URL проекта
                    project_url = f'https://etalongroup.ru/spb/object/{slug}/'

                    projects.append({
                        'name': project_name,
                        'url': project_url,
                        'quantity': data['count']
                    })

            browser.close()

            # Сортируем по количеству (больше -> меньше)
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
    projects = parse_etalon_kladovye()

    if projects:
        print(f'Найдено проектов: {len(projects)}')
        total_qty = sum(p['quantity'] for p in projects)
        print(f'Всего кладовых: {total_qty}\n')
        for p in projects:
            print(f"  {p['name']}: {p['quantity']} шт")
            print(f"    URL: {p['url']}")
    else:
        print('Проекты не найдены')
