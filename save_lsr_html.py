from playwright.sync_api import sync_playwright

url = 'https://www.lsr.ru/spb/kladovki/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(5000)
    
    # Прокрутка
    for i in range(3):
        page.evaluate('window.scrollBy(0, 1000)')
        page.wait_for_timeout(1000)
    
    html = page.content()
    with open('/root/realty-monitor/data/lsr_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'HTML сохранен ({len(html)} байт)')
    
    # Попробуем найти все div и article
    divs = page.query_selector_all('div')
    articles = page.query_selector_all('article')
    sections = page.query_selector_all('section')
    
    print(f'Найдено: {len(divs)} div, {len(articles)} article, {len(sections)} section')
    
    # Ищем элементы, которые могут быть карточками
    potential_cards = page.query_selector_all('[class*="complex"], [class*="project"], [class*="object"]')
    print(f'Потенциальных карточек: {len(potential_cards)}')
    
    if potential_cards:
        print('\nПервая карточка:')
        print(potential_cards[0].inner_text()[:200])
    
    browser.close()
