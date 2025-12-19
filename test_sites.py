from playwright.sync_api import sync_playwright

sites = [
    {"name": "Setl Group", "url": "https://setlgroup.ru/buildings/storerooms"},
    {"name": "Эталон", "url": "https://etalongroup.ru/spb/choose/parking/"},
    {"name": "ПИК", "url": "https://www.pik.ru/search/spb/storehouse"}
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()
    
    for site in sites:
        try:
            print("=" * 60)
            print(f"Проверка: {site['name']}")
            print(f"URL: {site['url']}")
            print("=" * 60)
            
            response = page.goto(site["url"], wait_until="networkidle", timeout=30000)
            print(f"Статус: {response.status}")
            
            title = page.title()
            print(f"Заголовок: {title}")
            
            content = page.content()
            if "forbidden" in content.lower() or "access denied" in content.lower():
                print("⚠️ БЛОКИРОВКА: Обнаружена защита от ботов")
            elif len(content) < 1000:
                print(f"⚠️ ПОДОЗРИТЕЛЬНО: Слишком мало контента ({len(content)} байт)")
            else:
                print(f"✅ OK: Контент загружен ({len(content)} байт)")
                
                if "кладов" in content.lower() or "storage" in content.lower() or "склад" in content.lower():
                    print("✅ Найдены упоминания кладовых на странице")
                
        except Exception as e:
            print(f"❌ ОШИБКА: {e}")
        
        print()
    
    browser.close()
