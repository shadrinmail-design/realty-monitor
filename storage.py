"""Модуль для хранения и сравнения данных"""
import json
import os
from datetime import datetime
from typing import List, Dict, Set

class Storage:
    def __init__(self, data_dir: str = '/root/realty-monitor/data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def get_storage_file(self, source: str) -> str:
        """Возвращает путь к файлу хранилища для источника"""
        return os.path.join(self.data_dir, f'{source}.json')
    
    def load_previous_state(self, source: str) -> List[Dict]:
        """Загружает предыдущее состояние"""
        file_path = self.get_storage_file(source)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f'Ошибка загрузки данных из {file_path}: {e}')
                return []
        return []
    
    def save_current_state(self, source: str, projects: List[Dict]):
        """Сохраняет текущее состояние"""
        file_path = self.get_storage_file(source)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'Ошибка сохранения данных в {file_path}: {e}')
    
    def find_new_projects(self, source: str, current_projects: List[Dict]) -> List[Dict]:
        """Находит новые проекты, сравнивая с предыдущим состоянием"""
        previous = self.load_previous_state(source)
        
        # Создаем множество URL предыдущих проектов
        previous_urls = {p.get('url') for p in previous if p.get('url')}
        
        # Находим новые проекты
        new_projects = []
        for project in current_projects:
            url = project.get('url')
            if url and url not in previous_urls:
                new_projects.append(project)
        
        return new_projects
    
    def get_project_count(self, source: str) -> int:
        """Возвращает количество проектов в предыдущем состоянии"""
        previous = self.load_previous_state(source)
        return len(previous)
