from playwright.sync_api import sync_playwright
import re

# Анализ Setl Group
print("=" * 80)
print("АНАЛИЗ: Setl Group")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto("https://setlgroup.ru/buildings/storerooms", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    # Ищем карточки
    cards = page.query_selector_all("div.card, div.item, article")
    print(f"Найдено возможных карточек: {len(cards)}")

    content = page.content()

    # Ищем упоминания ЖК
    jk_pattern = r'ЖК\s+[\w\s\-]+'
    jk_matches = re.findall(jk_pattern, content)
    print(f"\nНайдено упоминаний ЖК: {len(set(jk_matches))}")
    print("Примеры:", list(set(jk_matches))[:5])

    # Ищем количество
    qty_pattern = r'\d+\s*кладов'
    qty_matches = re.findall(qty_pattern, content, re.IGNORECASE)
    print(f"Найдено упоминаний количества кладовых: {len(qty_matches)}")
    print("Примеры:", qty_matches[:5])

    browser.close()

# Анализ Эталон
print("\n" + "=" * 80)
print("АНАЛИЗ: Эталон")
print("=" * 80)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Проверяем основную страницу паркинга
    page.goto("https://etalongroup.ru/spb/choose/parking/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    content = page.content()

    # Проверяем есть ли упоминание кладовых
    if "кладов" in content.lower():
        print("✅ На странице паркинга есть упоминания кладовых")

        # Ищем количество
        qty_pattern = r'\d+\s*кладов'
        qty_matches = re.findall(qty_pattern, content, re.IGNORECASE)
        print(f"Найдено упоминаний количества: {len(qty_matches)}")
        print("Примеры:", qty_matches[:5])
    else:
        print("⚠️ На странице паркинга нет кладовых")

    # Проверяем есть ли отдельная страница для кладовых
    try:
        page.goto("https://etalongroup.ru/spb/choose/storerooms/", wait_until="networkidle", timeout=15000)
        print(f"\n✅ Найдена отдельная страница кладовых: /spb/choose/storerooms/")

        content2 = page.content()
        qty_matches2 = re.findall(qty_pattern, content2, re.IGNORECASE)
        print(f"Найдено упоминаний количества кладовых: {len(qty_matches2)}")
        print("Примеры:", qty_matches2[:5])
    except Exception as e:
        print(f"❌ Отдельной страницы кладовых нет: {e}")

    browser.close()

print("\n" + "=" * 80)
print("ВЫВОД")
print("=" * 80)
