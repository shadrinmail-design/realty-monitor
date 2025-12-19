import requests
from bs4 import BeautifulSoup
import json

url = 'https://group-akvilon.ru/novostroyki/kladovye/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Ищем карточки проектов
cards = soup.find_all(class_=lambda x: x and 'card' in x.lower() if x else False)
print(f'Найдено карточек: {len(cards)}')

# Ищем все элементы с текстом, похожим на названия ЖК
all_text = soup.get_text()
print(f'\nДлина HTML: {len(response.text)} символов')
print(f'Длина текста: {len(all_text)} символов')

# Проверяем, есть ли JavaScript-загрузка данных
scripts = soup.find_all('script')
print(f'\nНайдено скриптов: {len(scripts)}')

# Ищем JSON данные в скриптах
for script in scripts:
    if script.string and 'kladovye' in script.string.lower():
        print('Найдены данные о кладовых в скрипте!')
        break

# Выводим первые 2000 символов HTML для анализа
print('\n=== Начало HTML ===')
print(response.text[:2000])
