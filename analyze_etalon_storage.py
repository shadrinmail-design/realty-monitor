from playwright.sync_api import sync_playwright
from collections import defaultdict
import re
import json

url = "https://etalongroup.ru/spb/choose/storage/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)
    
    # Скроллим для подгрузки всех карточек
    for i in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
    
    print("="*60)
    print("АНАЛИЗ СТРАНИЦЫ КАТАЛОГА КЛАДОВЫХ ЭТАЛОН")
    print("="*60)
    
    # Ищем все элементы data-id (обычно карточки имеют уникальный ID)
    cards_with_id = page.query_selector_all("[data-id]")
    print(f"\nЭлементов с data-id: {len(cards_with_id)}")
    
    # Проверяем первые несколько
    if cards_with_id:
        for i, card in enumerate(cards_with_id[:3]):
            data_id = card.get_attribute("data-id")
            text = card.inner_text()[:200]
            print(f"\n  Карточка {i+1} (data-id={data_id}):")
            print(f"    Текст: {text}")
    
    # Ищем элементы с классами содержащими storage, flat, card
    for selector in ["[class*=storage]", "[class*=flat]", "[data-flat]"]:
        try:
            elements = page.query_selector_all(selector)
            if elements and len(elements) > 5:
                print(f"\nСелектор {selector}: {len(elements)} элементов")
        except:
            pass
    
    # Проверяем сетевые запросы - ищем API
    print("\n" + "="*60)
    print("ПОИСК API ЗАПРОСОВ")
    print("="*60)
    
    # Сохраним HTML для анализа
    content = page.content()
    
    # Ищем JSON данные в скриптах
    scripts = page.query_selector_all("script")
    for script in scripts:
        try:
            script_text = script.inner_text()
            if "storage" in script_text.lower() and "{" in script_text:
                # Пробуем найти JSON
                if len(script_text) > 100 and len(script_text) < 50000:
                    print(f"\nНайден скрипт с данными (размер: {len(script_text)} символов)")
                    # Ищем паттерны JSON
                    json_matches = re.findall(r"\{[^{}]*storage[^{}]*\}", script_text, re.IGNORECASE)
                    if json_matches:
                        print(f"  Найдено JSON объектов: {len(json_matches)}")
                        print(f"  Пример: {json_matches[0][:200]}")
        except:
            pass
    
    browser.close()
