"""Модуль аналитики и алертов"""
from typing import List, Dict, Tuple
from history import HistoryStorage
from alert_state import AlertState

class Analytics:
    def __init__(self):
        self.history = HistoryStorage()
        self.alert_state = AlertState()
    
    def check_low_quantity_alert(self, projects: List[Dict]) -> List[Dict]:
        """
        Проверяет проекты с малым количеством кладовых
        Использует умные пороги: 25, 15, 10, 5, 2
        Уведомляет только при пересечении нового порога
        """
        alerts = []
        
        for project in projects:
            quantity = project.get('quantity')
            if quantity is None:
                continue
            
            name = project['name'].split('\n')[0]
            url = project['url']
            
            # Проверяем, нужен ли алерт
            should_alert, threshold = self.alert_state.should_alert(url, name, quantity)
            
            if should_alert:
                alerts.append({
                    'type': 'low_quantity',
                    'project': name,
                    'url': url,
                    'quantity': quantity,
                    'threshold': threshold,
                    'message': f'⚠️ {name}: осталось {quantity} кладовых (порог {threshold})'
                })
        
        return alerts
    
    def check_high_sales_alert(self, projects: List[Dict], days: int = 30, sold_threshold: int = 20) -> List[Dict]:
        """Проверяет проекты, где за N дней продано больше sold_threshold кладовых"""
        alerts = []
        
        for project in projects:
            url = project['url']
            change = self.history.get_quantity_change(url, days)
            
            # change отрицательное, если продано
            sold_count = abs(change) if change < 0 else 0
            
            if sold_count > sold_threshold:
                name = project['name'].split('\n')[0]
                current_quantity = project.get('quantity', 0)
                
                # Проверяем, не алертили ли мы уже об этом
                alert_key = f'{url}_sales_{days}d'
                
                alerts.append({
                    'type': 'high_sales',
                    'project': name,
                    'url': url,
                    'sold_count': sold_count,
                    'days': days,
                    'current_quantity': current_quantity,
                    'threshold': sold_threshold,
                    'message': f'🔥 {name}: продано {sold_count} кладовых за последние {days} дней (осталось {current_quantity})'
                })
        
        return alerts
    
    def get_weekly_summary(self, projects: List[Dict]) -> Dict:
        """Формирует еженедельную сводку"""
        summary = {
            'total_projects': 0,
            'total_quantity': 0,
            'projects': [],
            'top_sellers': [],
            'low_stock': []
        }
        
        for project in projects:
            quantity = project.get('quantity')
            if quantity is None:
                continue
            
            name = project['name'].split('\n')[0]
            url = project['url']
            price = project.get('price', 'Нет данных')
            
            # Продажи за неделю
            weekly_change = self.history.get_quantity_change(url, days=7)
            weekly_sold = abs(weekly_change) if weekly_change < 0 else 0
            
            # Продажи за месяц
            monthly_change = self.history.get_quantity_change(url, days=30)
            monthly_sold = abs(monthly_change) if monthly_change < 0 else 0
            
            project_data = {
                'name': name,
                'quantity': quantity,
                'price': price,
                'weekly_sold': weekly_sold,
                'monthly_sold': monthly_sold
            }
            
            summary['projects'].append(project_data)
            summary['total_quantity'] += quantity
            summary['total_projects'] += 1
            
            # Топ продаж за неделю
            if weekly_sold > 0:
                summary['top_sellers'].append(project_data)
            
            # Малый остаток
            if quantity < 50:
                summary['low_stock'].append(project_data)
        
        # Сортируем
        summary['top_sellers'].sort(key=lambda x: x['weekly_sold'], reverse=True)
        summary['low_stock'].sort(key=lambda x: x['quantity'])
        
        return summary
