import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def parse_akvilon():
    url = 'https://group-akvilon.ru/novostroyki/kladovye/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем все ссылки на проекты
    projects = []
    links = soup.find_all('a', href=lambda x: x and '/novostroyki/' in x and '/kladovye' in x)
    
    seen = set()
    for link in links:
        href = link.get('href', '')
        # Извлекаем название проекта из URL
        if '/novostroyki/' in href and href not in seen:
            seen.add(href)
            # Получаем текст из ссылки или родительского элемента
            text = link.get_text(strip=True)
            parent_text = link.parent.get_text(strip=True) if link.parent else ''
            
            if text and len(text) > 3:  # Фильтруем короткие тексты
                projects.append({
                    'name': text,
                    'url': f'https://group-akvilon.ru{href}' if not href.startswith('http') else href,
                    'found_at': datetime.now().isoformat()
                })
    
    # Убираем дубликаты
    unique_projects = {}
    for p in projects:
        key = p['url']
        if key not in unique_projects:
            unique_projects[key] = p
    
    result = list(unique_projects.values())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result

if __name__ == '__main__':
    parse_akvilon()
