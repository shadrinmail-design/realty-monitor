from playwright.sync_api import sync_playwright
import random

url = 'https://www.lsr.ru/spb/kladovki/'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={'width': 1920, 'height': 1080},
        locale='ru-RU',
        timezone_id='Europe/Moscow'
    )
    
    # Удаляем признаки автоматизации
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
    """)
    
    page = context.new_page()
    
    try:
        print('Загрузка страницы ЛСР...')
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        page.wait_for_timeout(5000)  # Ждем загрузки
        
        # Проверяем, что получили
        title = page.title()
        print(f'Title: {title}')
        
        content = page.content()
        if 'Forbidden' in content or 'forbidden' in content.lower():
            print('Все еще заблокирован')
        else:
            print('Успешная загрузка!')
            text = page.inner_text('body')
            print(f'Длина текста: {len(text)}')
            print(f'Первые 500 символов:\n{text[:500]}')
        
    except Exception as e:
        print(f'Ошибка: {e}')
    finally:
        browser.close()
