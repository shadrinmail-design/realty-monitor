from playwright.sync_api import sync_playwright

url = 'https://www.lsr.ru/spb/kladovki/'

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        proxy={'server': 'socks5://localhost:9050'},
        args=['--disable-blink-features=AutomationControlled']
    )
    
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    
    try:
        print('Подключение через TOR...')
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        page.wait_for_timeout(5000)
        
        title = page.title()
        print(f'Title: {title}')
        
        content = page.content()
        if 'Forbidden' in content:
            print('Все еще заблокирован')
        else:
            print('УСПЕХ! Доступ получен через TOR')
            text = page.inner_text('body')
            print(f'Длина текста: {len(text)} символов')
            print(f'Первые 500 символов:\n{text[:500]}')
            
            # Сохраним HTML
            with open('/root/realty-monitor/data/lsr_tor.html', 'w') as f:
                f.write(content)
            print('HTML сохранен')
        
    except Exception as e:
        print(f'Ошибка: {e}')
    finally:
        browser.close()
