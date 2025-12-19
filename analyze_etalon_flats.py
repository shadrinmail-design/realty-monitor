from playwright.sync_api import sync_playwright
from collections import defaultdict
import re

url = "https://etalongroup.ru/spb/choose/storage/"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)
    
    # Скроллим
    for i in range(5):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
    
    print("="*60)
    print("АНАЛИЗ ЭЛЕМЕНТОВ С КЛАССОМ FLAT")
    print("="*60)
    
    # Ищем все элементы flat
    flat_elements = page.query_selector_all("[class*=flat]")
    print(f"\nНайдено элементов: {len(flat_elements)}\n")
    
    projects = defaultdict(int)
    
    for i, elem in enumerate(flat_elements):
        text = elem.inner_text()
        html = elem.inner_html()
        
        print(f"--- Элемент {i+1} ---")
        print(f"Текст (первые 300 символов):")
        print(text[:300])
        
        # Ищем название проекта
        # Проверяем ссылки внутри элемента
        links = elem.query_selector_all("a[href*=/object/]")
        if links:
            for link in links:
                href = link.get_attribute("href")
                link_text = link.inner_text().strip()
                if link_text and len(link_text) > 2:
                    print(f"  Проект: {link_text}")
                    print(f"  URL: {href}")
                    projects[link_text] += 1
        
        print()
        
        if i >= 4:  # Показываем первые 5
            print(f"... и еще {len(flat_elements) - 5} элементов\n")
            break
    
    print("="*60)
    print("ПОДСЧЕТ ПО ПРОЕКТАМ")
    print("="*60)
    
    for project, count in sorted(projects.items(), key=lambda x: x[1], reverse=True):
        print(f"  {project}: {count} кладовых")
    
    browser.close()
