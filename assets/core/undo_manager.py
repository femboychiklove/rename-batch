import json
from pathlib import Path
from datetime import datetime

class UndoManager:
    """Класс для управления отменой операций"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.history_file = self.folder_path / "rename_history.json"
    
    def add_to_history(self, operation: dict):
        """Добавить операцию в историю"""
        history = self.load_history()
        history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation
        })
        
        # Сохраняем максимум 10 операций
        if len(history) > 10:
            history = history[-10:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    
    def load_history(self) -> list:
        """Загрузить историю операций"""
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def clear_history(self):
        """Очистить историю"""
        if self.history_file.exists():
            self.history_file.unlink()
    
    def get_last_operation(self) -> dict | None:
        """Получить последнюю операцию"""
        history = self.load_history()
        if history:
            return history[-1]
        return None  
