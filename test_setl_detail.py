from playwright.sync_api import sync_playwright

url = "https://setlgroup.ru/buildings/storerooms/1301561/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(3000)

    # Заголовок страницы
    title = page.title()
    print(f"Title: {title}")

    # Ищем название ЖК
    h1 = page.query_selector("h1")
    if h1:
        print(f"H1: {h1.inner_text()}")

    # Ищем breadcrumbs
    breadcrumbs = page.query_selector_all("a[href*='building']")
    print(f"\nНайдено breadcrumbs: {len(breadcrumbs)}")
    for bc in breadcrumbs[:5]:
        text = bc.inner_text().strip()
        href = bc.get_attribute("href")
        if text and len(text) > 2:
            print(f"  - {text}: {href}")

    # Ищем мета-данные
    content = page.content()
    if "ЖК" in content:
        import re
        jk_matches = re.findall(r'ЖК\s+[\w\s\-«»]+', content)
        unique_jk = list(set(jk_matches))[:5]
        print(f"\nНайдено упоминаний ЖК: {unique_jk}")

    browser.close()
