"""Модуль для хранения исторических данных о количестве кладовых"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

class HistoryStorage:
    def __init__(self, data_dir: str = '/root/realty-monitor/data'):
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, 'history.json')
        os.makedirs(data_dir, exist_ok=True)
    
    def load_history(self) -> List[Dict]:
        """Загружает всю историю"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f'Ошибка загрузки истории: {e}')
                return []
        return []
    
    def save_snapshot(self, projects: List[Dict]):
        """Сохраняет снимок текущего состояния"""
        history = self.load_history()
        
        snapshot = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'datetime': datetime.now().isoformat(),
            'projects': []
        }
        
        for project in projects:
            if project.get('quantity') is not None:
                snapshot['projects'].append({
                    'name': project['name'].split('\n')[0],  # Убираем "Смотреть проект"
                    'url': project['url'],
                    'quantity': project['quantity'],
                    'price': project.get('price')
                })
        
        # Проверяем, есть ли уже запись за сегодня
        today = snapshot['date']
        history = [h for h in history if h.get('date') != today]
        
        # Добавляем новый снимок
        history.append(snapshot)
        
        # Сохраняем
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            print(f'Снимок сохранен: {len(snapshot["projects"])} проектов')
        except Exception as e:
            print(f'Ошибка сохранения истории: {e}')
    
    def get_snapshot_by_date(self, date_str: str) -> Dict:
        """Получает снимок по дате (формат YYYY-MM-DD)"""
        history = self.load_history()
        for snapshot in history:
            if snapshot.get('date') == date_str:
                return snapshot
        return None
    
    def get_project_history(self, project_url: str, days: int = 30) -> List[Dict]:
        """Получает историю конкретного проекта за N дней"""
        history = self.load_history()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        project_history = []
        for snapshot in history:
            snapshot_date = datetime.fromisoformat(snapshot['datetime'])
            if snapshot_date >= cutoff_date:
                for project in snapshot['projects']:
                    if project['url'] == project_url:
                        project_history.append({
                            'date': snapshot['date'],
                            'quantity': project['quantity'],
                            'price': project.get('price')
                        })
                        break
        
        return sorted(project_history, key=lambda x: x['date'])
    
    def get_quantity_change(self, project_url: str, days: int = 30) -> int:
        """Возвращает изменение количества кладовых за период (отрицательное = продано)"""
        project_history = self.get_project_history(project_url, days)
        if len(project_history) < 2:
            return 0
        
        oldest = project_history[0]['quantity']
        newest = project_history[-1]['quantity']
        
        return newest - oldest  # Отрицательное значение = продано
    
    def get_latest_quantities(self) -> Dict[str, int]:
        """Возвращает последние известные количества для всех проектов"""
        history = self.load_history()
        if not history:
            return {}
        
        latest = history[-1]
        return {p['url']: p['quantity'] for p in latest.get('projects', [])}
