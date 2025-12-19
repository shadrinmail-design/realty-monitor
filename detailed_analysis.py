from playwright.sync_api import sync_playwright
import time

print("=" * 80)
print("ДЕТАЛЬНЫЙ АНАЛИЗ: Setl Group")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto("https://setlgroup.ru/buildings/storerooms", wait_until="networkidle", timeout=30000)

    # Даем время на динамическую подгрузку
    page.wait_for_timeout(5000)

    # Пробуем скроллить вниз для подгрузки
    for i in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

    # Ищем разные варианты селекторов
    selectors = [
        "div[class*='card']",
        "div[class*='item']",
        "div[class*='project']",
        "div[class*='complex']",
        "a[href*='building']",
        "div[class*='building']"
    ]

    for selector in selectors:
        elements = page.query_selector_all(selector)
        if elements and len(elements) > 2:
            print(f"\n✅ Селектор: {selector} - найдено {len(elements)} элементов")

            # Берем первый элемент для примера
            if elements:
                first = elements[0]
                html = first.inner_html()
                print(f"\nПример HTML (первые 500 символов):")
                print(html[:500])
                break

    # Проверяем общее количество
    text = page.inner_text("body")
    if "233" in text or "кладов" in text:
        print("\n✅ Текст '233 кладов' присутствует на странице")

    browser.close()

print("\n" + "=" * 80)
print("ДЕТАЛЬНЫЙ АНАЛИЗ: Эталон - Кладовые")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto("https://etalongroup.ru/spb/choose/storerooms/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)

    # Скроллим
    for i in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

    # Ищем селекторы
    selectors = [
        "div[class*='card']",
        "div[class*='item']",
        "div[class*='project']",
        "a[class*='card']",
        "div[class*='object']"
    ]

    for selector in selectors:
        elements = page.query_selector_all(selector)
        if elements and len(elements) > 2:
            print(f"\n✅ Селектор: {selector} - найдено {len(elements)} элементов")

            if elements:
                first = elements[0]
                html = first.inner_html()
                print(f"\nПример HTML (первые 500 символов):")
                print(html[:500])

                # Пробуем извлечь текст
                text = first.inner_text()
                print(f"\nТекст карточки (первые 300 символов):")
                print(text[:300])
                break

    browser.close()
