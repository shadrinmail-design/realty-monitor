from playwright.sync_api import sync_playwright

url = 'https://group-akvilon.ru/novostroyki/kladovye/'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='networkidle', timeout=30000)
    page.wait_for_selector('[class*="card"]', timeout=10000)
    
    # Получаем первую карточку и выводим ее HTML
    cards = page.query_selector_all('[class*="card"]')
    if cards:
        print('=== HTML первой карточки ===')
        print(cards[0].inner_html())
        print('\n=== Текст первой карточки ===')
        print(cards[0].inner_text())
    
    browser.close()
