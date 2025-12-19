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

    # Проверим весь body текст
    body_text = page.inner_text("body")

    # Ищем все упоминания ЖК
    jk_pattern = r'ЖК\s+([А-ЯЁа-яё\s\-«»\.]+?)(?=\n|\.|,|$|ЖК|от|Площадь|\d+\s*кладов)'
    jk_matches = re.findall(jk_pattern, body_text)

    unique_jk = list(set([m.strip() for m in jk_matches]))

    print(f"Найдено уникальных ЖК: {len(unique_jk)}\n")
    for jk in unique_jk[:15]:
        print(f"  - ЖК {jk}")

    # Теперь попробуем найти связь ЖК с количеством
    print("\n" + "=" * 60)
    print("Поиск связи ЖК -> количество")
    print("=" * 60 + "\n")

    # Разбиваем на блоки по "кладов"
    blocks = re.split(r'(\d+\s*кладов[ыа]*)', body_text, flags=re.IGNORECASE)

    for i in range(0, len(blocks)-1, 2):
        if i+1 < len(blocks):
            before_text = blocks[i][-200:] if len(blocks[i]) > 200 else blocks[i]  # 200 символов до
            qty_text = blocks[i+1]  # Само количество

            # Ищем ЖК в тексте до
            jk_match = re.search(r'ЖК\s+([А-ЯЁа-яё\s\-«»\.]+?)$', before_text.strip(), re.MULTILINE)

            if jk_match:
                jk_name = jk_match.group(1).strip()
                qty_match = re.search(r'(\d+)', qty_text)
                qty = qty_match.group(1) if qty_match else '?'

                print(f"ЖК {jk_name}: {qty} кладовых")

    browser.close()
