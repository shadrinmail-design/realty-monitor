import requests
from bs4 import BeautifulSoup
import json
import re

url = 'https://group-akvilon.ru/novostroyki/kladovye/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

scripts = soup.find_all('script')
for script in scripts:
    if script.string and '__NUXT__' in script.string:
        text = script.string
        match = re.search(r'__NUXT__\s*=\s*(\{.*?\});', text, re.DOTALL)
        if match:
            try:
                with open('/root/realty-monitor/data/nuxt_data.txt', 'w', encoding='utf-8') as f:
                    f.write(match.group(1)[:5000])
                print('OK')
            except Exception as e:
                print(f'Error: {e}')
        break

cards = soup.find_all(class_=lambda x: x and 'card' in x.lower() if x else False)
print(f'Cards: {len(cards)}')
