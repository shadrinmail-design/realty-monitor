from playwright.sync_api import sync_playwright
import json
import random
import re
from datetime import datetime

# Список реальных User-Agent различных браузеров
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

def extract_quantity(text):
    """Извлекает число из строки типа '145 кладовых'"""
    if not text:
        return None
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else None

def parse_akvilon_kladovye():
    """Парсит страницу кладовых Аквилон с количеством кладовых"""
    url = 'https://group-akvilon.ru/novostroyki/kladovye/'

    # Выбираем случайный User-Agent
    user_agent = random.choice(USER_AGENTS)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        try:
            # Загружаем страницу с ожиданием полной загрузки сети
            page.goto(url, wait_until='networkidle', timeout=30000)

            # Случайная задержка 2-5 секунд (эмуляция человека)
            page.wait_for_timeout(random.randint(2000, 5000))

            # Ждем появления карточек проектов в DOM (не обязательно видимых)
            # Увеличиваем timeout и меняем state на 'attached'
            page.wait_for_selector('[class*="card"]', state='attached', timeout=20000)

            # Дополнительное ожидание для JS, который может скрывать/показывать элементы
            page.wait_for_timeout(2000)

            # Извлекаем все карточки
            cards = page.query_selector_all('[class*="card"]')

            projects = []
            for card in cards:
                try:
                    # Извлекаем название проекта
                    name_elem = card.query_selector('h3, h2, h4, [class*="title"]')
                    name = name_elem.inner_text().strip() if name_elem else None

                    # Извлекаем ссылку
                    link_elem = card.query_selector('a')
                    link = link_elem.get_attribute('href') if link_elem else None

                    if link and not link.startswith('http'):
                        link = f'https://group-akvilon.ru{link}'

                    # Извлекаем цену
                    price_elem = card.query_selector('[class*="price"]')
                    price = price_elem.inner_text().strip() if price_elem else None

                    # Извлекаем количество кладовых
                    quantity_elem = card.query_selector('[class*="flats"]')
                    quantity_text = quantity_elem.inner_text().strip() if quantity_elem else None
                    quantity = extract_quantity(quantity_text)

                    if name and link:
                        project = {
                            'name': name,
                            'url': link,
                            'price': price,
                            'quantity': quantity,
                            'quantity_text': quantity_text,
                            'found_at': datetime.now().isoformat(),
                            'source': 'akvilon_kladovye'
                        }
                        projects.append(project)

                except Exception as e:
                    print(f'Ошибка при обработке карточки: {e}')
                    continue

            # Фильтруем проекты:
            # 1. Убираем записи с quantity = None или 0
            # 2. Убираем записи с названием "Кладовая X м²"
            filtered_projects = []
            for project in projects:
                # Проверяем quantity
                if project.get('quantity') is None or project.get('quantity') == 0:
                    continue

                # Проверяем название - исключаем паттерн "Кладовая X м²"
                name = project.get('name', '')
                if re.match(r'^Кладовая\s+[\d.]+\s*м²', name):
                    continue

                filtered_projects.append(project)

            projects = filtered_projects

            browser.close()
            return projects

        except Exception as e:
            browser.close()
            raise Exception(f'Ошибка при парсинге: {e}')

if __name__ == '__main__':
    try:
        projects = parse_akvilon_kladovye()
        print(json.dumps(projects, ensure_ascii=False, indent=2))
        print(f'\n\nВсего найдено проектов: {len(projects)}')

        total_quantity = sum(p['quantity'] for p in projects if p.get('quantity'))
        print(f'Всего кладовых: {total_quantity}')
    except Exception as e:
        print(f'ОШИБКА: {e}')
        exit(1)
