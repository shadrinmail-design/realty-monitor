from playwright.sync_api import sync_playwright

sites = [
    {'name': 'ТРЕСТ', 'url': 'https://trest-group.ru/catalog/storeroom/'},
    {'name': 'GloraX', 'url': 'https://glorax.com/storage'},
    {'name': 'ПСК', 'url': 'https://psk-info.ru/storages'},
    {'name': 'ЦДС', 'url': 'https://www.cds.spb.ru/complex/gorod-pervyh/storage/'},
    {'name': 'Северная долина', 'url': 'https://sevdol.ru/pantry'}
]

print('='*60)
print('ПРОВЕРКА ДОСТУПНОСТИ НОВЫХ ЗАСТРОЙЩИКОВ')
print('='*60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )

    for site in sites:
        print(f"\n{site['name']}:")
        print(f"  URL: {site['url']}")

        try:
            response = page.goto(site['url'], wait_until='networkidle', timeout=20000)
            print(f'  Статус: {response.status}')

            if response.status == 200:
                print('  ✅ Доступен')

                page.wait_for_timeout(3000)
                body_text = page.inner_text('body')

                # Проверяем размер контента
                if len(body_text) > 500:
                    print(f'  ✅ Достаточно контента ({len(body_text)} символов)')

                    # Проверяем наличие кладовых
                    if 'кладов' in body_text.lower():
                        print('  ✅ Есть упоминания кладовых')

                    # Показываем начало
                    print(f'  Начало текста: {body_text[:150]}')
                else:
                    print(f'  ⚠️ Мало контента ({len(body_text)} символов)')
            else:
                print(f'  ⚠️ Статус: {response.status}')

        except Exception as e:
            print(f'  ❌ Ошибка: {str(e)[:100]}')

    browser.close()
