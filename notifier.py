"""Модуль для отправки уведомлений в Telegram"""
import requests
import html
from typing import List, Dict
import config

class TelegramNotifier:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}'
    
    def escape_html(self, text: str) -> str:
        """Экранирует HTML символы"""
        if not text:
            return ''
        return html.escape(str(text))
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """Отправляет сообщение в Telegram"""
        if not self.bot_token or not self.chat_id:
            print('Telegram не настроен. Пропускаем отправку уведомления.')
            print(f'Сообщение: {text}')
            return False
        
        url = f'{self.base_url}/sendMessage'
        data = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': False
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200:
                print('Уведомление отправлено в Telegram')
                return True
            else:
                print(f'Ошибка отправки в Telegram: {response.status_code} - {response.text}')
                return False
        except Exception as e:
            print(f'Ошибка при отправке в Telegram: {e}')
            return False
    
    def notify_new_projects(self, source_name: str, new_projects: List[Dict]) -> bool:
        """Формирует и отправляет уведомление о новых проектах"""
        if not new_projects:
            return False
        
        count = len(new_projects)
        message = f'🏢 <b>Новые объекты на {self.escape_html(source_name)}!</b>\n\n'
        message += f'Найдено новых ЖК: <b>{count}</b>\n\n'
        
        for i, project in enumerate(new_projects, 1):
            name = project.get('name', 'Без названия').replace('\nСмотреть проект', '')
            url = project.get('url', '')
            price = project.get('price', 'Цена не указана')
            quantity = project.get('quantity')
            
            message += f'{i}. <b>{self.escape_html(name)}</b>\n'
            if quantity:
                # Определяем тип объекта по project.get('type') или по названию
                is_parking = project.get('type') == 'parking' or 'паркинг' in name.lower()
                unit_name = 'машиномест' if is_parking else 'кладовых'
                message += f'   📦 {quantity} {unit_name}\n'
            if price:
                message += f'   💰 {self.escape_html(price)}\n'
            if url:
                message += f'   🔗 <a href="{url}">Подробнее</a>\n'
            message += '\n'
        
        return self.send_message(message)
    
    def notify_alerts(self, alerts: List[Dict]) -> bool:
        """Отправляет алерты"""
        if not alerts:
            return False
        
        message = f'⚠️ <b>АЛЕРТЫ</b>\n\n'
        
        for alert in alerts:
            # Экранируем сообщение алерта
            alert_msg = alert['message']
            # Сохраняем эмодзи и экранируем остальное
            parts = alert_msg.split(' ', 1)
            if len(parts) == 2:
                emoji, rest = parts
                message += f'{emoji} {self.escape_html(rest)}\n'
            else:
                message += self.escape_html(alert_msg) + '\n'
        
        message += f'\n<i>Всего алертов: {len(alerts)}</i>'
        
        return self.send_message(message)
    
    def notify_weekly_summary(self, summary: Dict) -> bool:
        """Отправляет еженедельную сводку"""
        message = f'📊 <b>Еженедельный отчет по кладовым Аквилон</b>\n\n'
        
        message += f'<b>Общая статистика:</b>\n'
        message += f'• ЖК с кладовыми: {summary["total_projects"]}\n'
        message += f'• Всего кладовых: {summary["total_quantity"]}\n\n'
        
        # Малый остаток
        if summary['low_stock']:
            message += f'⚠️ <b>Малый остаток (меньше 50):</b>\n'
            for p in summary['low_stock'][:5]:  # Топ-5
                message += f'• {self.escape_html(p["name"])}: <b>{p["quantity"]}</b> шт\n'
            message += '\n'
        
        # Топ продаж за неделю
        if summary['top_sellers']:
            message += f'🔥 <b>Топ продаж за неделю:</b>\n'
            for p in summary['top_sellers'][:5]:  # Топ-5
                if p['weekly_sold'] > 0:
                    message += f'• {self.escape_html(p["name"])}: продано <b>{p["weekly_sold"]}</b> (осталось {p["quantity"]})\n'
            message += '\n'
        
        # Все проекты
        message += f'<b>Все проекты:</b>\n'
        for p in sorted(summary['projects'], key=lambda x: x['quantity'], reverse=True):
            message += f'• {self.escape_html(p["name"])}: {p["quantity"]} шт'
            if p['monthly_sold'] > 0:
                message += f' (-{p["monthly_sold"]}/мес)'
            message += '\n'
        
        return self.send_message(message)
    
    def notify_error(self, source_name: str, error: str) -> bool:
        """Отправляет уведомление об ошибке"""
        message = f'⚠️ <b>Ошибка мониторинга</b>\n\n'
        message += f'Источник: {self.escape_html(source_name)}\n'
        message += f'Ошибка: {self.escape_html(error)}'
        
        return self.send_message(message)
