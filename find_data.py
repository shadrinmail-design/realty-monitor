from playwright.sync_api import sync_playwright
import json
import re

print("=" * 80)
print("ПОИСК ДАННЫХ: Setl Group")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto("https://setlgroup.ru/buildings/storerooms", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)

    # Скроллим
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

    # Проверяем Network запросы (может быть API)
    content = page.content()

    # Ищем скрипты с данными JSON
    scripts = page.query_selector_all("script")
    print(f"Найдено script тегов: {len(scripts)}")

    for script in scripts:
        script_content = script.inner_text()
        # Ищем JSON с данными о проектах
        if "building" in script_content.lower() or "storeroom" in script_content.lower():
            if len(script_content) > 100 and "{" in script_content:
                print(f"\n✅ Найден потенциальный JSON с данными (первые 500 символов):")
                print(script_content[:500])
                break

    # Ищем специфичные селекторы для кладовых
    specific_selectors = [
        "div[data-building]",
        "div[data-project]",
        "a[href*='storeroom']",
        "a[href*='building']",
        "[class*='storeroom']",
        "[class*='building-card']"
    ]

    for selector in specific_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"\n✅ Селектор: {selector} - найдено {len(elements)} элементов")

    browser.close()

print("\n" + "=" * 80)
print("ПОИСК ДАННЫХ: Эталон")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto("https://etalongroup.ru/spb/choose/storerooms/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)

    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

    # Ищем карточки проектов
    specific_selectors = [
        "a[href*='object']",
        "a[href*='project']",
        "div[class*='project']",
        "div[class*='complex']",
        "[data-project]",
        "a[href*='/spb/object/']"
    ]

    for selector in specific_selectors:
        elements = page.query_selector_all(selector)
        if elements and len(elements) > 2:
            print(f"\n✅ Селектор: {selector} - найдено {len(elements)} элементов")

            # Показываем первый элемент
            if elements:
                first = elements[0]
                href = first.get_attribute("href")
                text = first.inner_text()
                print(f"  Пример href: {href}")
                print(f"  Текст (первые 200 символов): {text[:200]}")

    # Пробуем найти через текст кнопок/ссылок
    all_links = page.query_selector_all("a")
    project_links = []

    for link in all_links:
        href = link.get_attribute("href")
        if href and "/object/" in href:
            text = link.inner_text().strip()
            if text and len(text) > 3:
                project_links.append({"href": href, "text": text})

    if project_links:
        print(f"\n✅ Найдено ссылок на объекты: {len(project_links)}")
        print("Первые 3 примера:")
        for link in project_links[:3]:
            print(f"  - {link['text']}: {link['href']}")

    browser.close()
