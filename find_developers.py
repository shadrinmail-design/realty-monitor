from playwright.sync_api import sync_playwright
import json

# Список застройщиков для проверки
developers = [
    {'name': 'Setl Group', 'url': 'https://www.setl.ru', 'search_terms': ['кладов', 'storage']},
    {'name': 'Эталон', 'url': 'https://etalon.ru', 'search_terms': ['кладов', 'storage']},
    {'name': 'ПИК', 'url': 'https://www.pik.ru/spb', 'search_terms': ['кладов', 'storage']},
    {'name': 'ЦДС', 'url': 'https://cds.spb.ru', 'search_terms': ['кладов', 'storage']},
]

results = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    
    for dev in developers:
        try:
            print(f"Проверка {dev['name']}...")
            page = browser.new_page()
            page.goto(dev['url'], wait_until='networkidle', timeout=15000)
            page.wait_for_timeout(2000)
            
            # Получаем весь текст страницы
            content = page.content()
            
            # Ищем упоминания кладовых
            has_storage = any(term in content.lower() for term in dev['search_terms'])
            
            if has_storage:
                # Ищем ссылки с кладовыми
                links = page.query_selector_all('a')
                storage_links = []
                for link in links[:100]:  # Первые 100 ссылок
                    text = link.inner_text().lower() if link.inner_text() else ''
                    href = link.get_attribute('href') or ''
                    if any(term in text or term in href.lower() for term in dev['search_terms']):
                        storage_links.append({'text': text[:50], 'href': href})
                
                results.append({
                    'name': dev['name'],
                    'url': dev['url'],
                    'has_storage': True,
                    'storage_links': storage_links[:5]  # Топ-5 ссылок
                })
                print(f"  ✓ Найдены кладовые!")
            else:
                results.append({'name': dev['name'], 'url': dev['url'], 'has_storage': False})
                print(f"  ✗ Кладовые не найдены")
            
            page.close()
        except Exception as e:
            print(f"  Ошибка: {e}")
            results.append({'name': dev['name'], 'url': dev['url'], 'error': str(e)})
    
    browser.close()

print("\n" + "="*60)
print(json.dumps(results, ensure_ascii=False, indent=2))
