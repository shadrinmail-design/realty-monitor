from playwright.sync_api import sync_playwright
import random

url = 'https://www.lsr.ru/spb/kladovki/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Прокручиваем вниз для загрузки всех элементов
    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    page.wait_for_timeout(2000)
    
    # Получаем HTML для анализа
    html = page.content()
    
    # Ищем все ссылки на кладовые
    links = page.query_selector_all('a')
    storage_links = []
    for link in links:
        href = link.get_attribute('href') or ''
        text = link.inner_text() or ''
        if '/kladovki/' in href or 'кладов' in text.lower():
            storage_links.append({'href': href, 'text': text[:100]})
    
    print(f'Найдено {len(storage_links)} ссылок на кладовые')
    for i, sl in enumerate(storage_links[:10], 1):
        print(f'{i}. {sl["text"]} -> {sl["href"]}')
    
    # Ищем элементы с ценами и количеством
    print('\n' + '='*60)
    all_text = page.inner_text('body')
    
    # Ищем паттерны
    import re
    prices = re.findall(r'от [\d,.]+ млн', all_text)
    print(f'\nНайдено {len(set(prices))} уникальных цен: {list(set(prices))[:10]}')
    
    browser.close()
