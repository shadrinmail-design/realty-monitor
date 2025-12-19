from playwright.sync_api import sync_playwright
import re

url = "https://setlgroup.ru/buildings/storerooms"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)

    # Скроллим
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(3000)

    # Ищем все элементы с href storeroom
    links = page.query_selector_all("a[href*='storeroom']")

    print(f"Найдено ссылок: {len(links)}\n")

    for i, link in enumerate(links, 1):
        href = link.get_attribute("href")

        # Ищем родительский элемент с полной информацией
        parent = link.evaluate_handle("el => el.closest('div[class*=\"card\"], div[class*=\"item\"], article')")

        if parent:
            parent_elem = parent.as_element()
            parent_text = parent_elem.inner_text()
            parent_html = parent_elem.inner_html()

            print(f"=== Элемент {i} ===")
            print(f"URL: {href}")
            print(f"Текст (первые 300 символов):\n{parent_text[:300]}")
            print()

            # Ищем название ЖК в тексте
            jk_match = re.search(r'ЖК\s+([\w\s\-«»]+)', parent_text)
            if jk_match:
                print(f"  Найдено ЖК: {jk_match.group(1)}")

            # Ищем количество
            qty_match = re.search(r'(\d+)\s*кладов', parent_text, re.IGNORECASE)
            if qty_match:
                print(f"  Количество: {qty_match.group(1)}")

            print()

            if i >= 3:  # Показываем только первые 3
                break

    browser.close()
