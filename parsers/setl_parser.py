#!/usr/bin/env python3
"""
Парсер кладовых Setl Group
"""
import sys
import random
import re
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

def extract_quantity(text):
    """Извлекает количество из текста типа '145 кладовых'"""
    if not text:
        return None
    # Ищем число перед словом "кладов"
    match = re.search(r'(\d+)\s*кладов', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Просто число
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else None

def extract_price(text):
    """Извлекает цену из текста"""
    if not text:
        return None
    # Убираем пробелы и неразрывные пробелы
    text_clean = text.replace(' ', '').replace('\xa0', '')
    # Ищем число перед "руб" или "₽"
    match = re.search(r'(\d+)', text_clean)
    return match.group(1) if match else None

def parse_setl_kladovye():
    """Парсит страницу с кладовыми Setl Group"""
    url = 'https://setlgroup.ru/buildings/storerooms'

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

            # Скроллим для подгрузки контента
            page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            page.wait_for_timeout(2000)

            # Ищем все ссылки на кладовые
            links = page.query_selector_all('a[href*="storeroom"]')

            projects = []
            seen_urls = set()

            for link in links:
                try:
                    href = link.get_attribute('href')
                    if not href:
                        continue

                    # Делаем полный URL
                    if href.startswith('/'):
                        full_url = f'https://setlgroup.ru{href}'
                    else:
                        full_url = href

                    # Пропускаем дубликаты
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)

                    # Извлекаем текст
                    text = link.inner_text().strip()

                    # Пробуем найти название ЖК и количество
                    # Формат может быть: "ЖК Название\n145 кладовых"
                    lines = text.split('\n')

                    name = lines[0] if lines else text
                    quantity = None

                    # Ищем количество в тексте
                    for line in lines:
                        qty = extract_quantity(line)
                        if qty:
                            quantity = qty
                            break

                    # Если не нашли количество, пробуем в полном тексте ссылки
                    if not quantity:
                        full_text = link.inner_text()
                        quantity = extract_quantity(full_text)

                    if name:
                        project = {
                            'name': name.strip(),
                            'url': full_url,
                            'quantity': quantity
                        }
                        projects.append(project)

                except Exception as e:
                    print(f'Ошибка обработки ссылки: {e}', file=sys.stderr)
                    continue

            browser.close()

            return projects

    except PlaywrightTimeoutError:
        print('Ошибка: Таймаут при загрузке страницы', file=sys.stderr)
        return []
    except Exception as e:
        print(f'Ошибка парсинга: {e}', file=sys.stderr)
        return []

if __name__ == '__main__':
    projects = parse_setl_kladovye()

    if projects:
        print(f'Найдено проектов: {len(projects)}')
        for p in projects:
            qty_str = f"{p['quantity']} шт" if p['quantity'] else 'н/д'
            print(f"  - {p['name']}: {qty_str}")
            print(f"    URL: {p['url']}")
    else:
        print('Проекты не найдены')
