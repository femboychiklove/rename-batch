import os
import json
from pathlib import Path
from datetime import datetime

class FileRenamer:
    """Класс для массового переименования файлов"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.log_file = self.folder_path / "rename_log.json"
        
    def get_files(self, sort_by: str = "name") -> list:
        """Получить список файлов в папке"""
        files = []
        for item in self.folder_path.iterdir():
            if item.is_file():
                files.append(item)
        
        # Сортировка
        if sort_by == "name":
            files.sort(key=lambda x: x.name)
        elif sort_by == "date":
            files.sort(key=lambda x: x.stat().st_mtime)
        elif sort_by == "size":
            files.sort(key=lambda x: x.stat().st_size)
        elif sort_by == "extension":
            files.sort(key=lambda x: x.suffix)
        
        return files
    
    def rename_files(self, new_name: str, start_number: int = 1, sort_by: str = "name") -> int:
        """Переименовать все файлы с номерами"""
        files = self.get_files(sort_by)
        log = []
        
        for index, file_path in enumerate(files, start=start_number):
            # Получаем расширение
            ext = file_path.suffix
            # Создаём новое имя
            new_filename = f"{new_name}_{index}{ext}"
            new_path = self.folder_path / new_filename
            
            # Переименовываем
            file_path.rename(new_path)
            
            # Записываем в лог
            log.append({
                "old": file_path.name,
                "new": new_filename,
                "timestamp": datetime.now().isoformat()
            })
        
        # Сохраняем лог
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=4)
        
        return len(files)
    
    def rename_files_with_filter(self, new_name: str, start_number: int, sort_by: str, files: list) -> int:
        """Переименовать файлы с учётом фильтра (передаём готовый список файлов)"""
        log = []
        
        for index, file_path in enumerate(files, start=start_number):
            # Получаем расширение
            ext = file_path.suffix
            # Создаём новое имя
            new_filename = f"{new_name}_{index}{ext}"
            new_path = self.folder_path / new_filename
            
            # Переименовываем
            old_name = file_path.name
            file_path.rename(new_path)
            
            # Записываем в лог
            log.append({
                "old": old_name,
                "new": new_filename,
                "timestamp": datetime.now().isoformat()
            })
        
        # Сохраняем лог
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=4)
        
        return len(files)
    
    def undo_rename(self) -> int:
        """Отменить последнее переименование"""
        if not self.log_file.exists():
            raise FileNotFoundError("Лог не найден. Отмена невозможна.")
        
        with open(self.log_file, "r", encoding="utf-8") as f:
            log = json.load(f)
        
        # Отменяем в обратном порядке
        for item in reversed(log):
            old_path = self.folder_path / item["new"]
            new_path = self.folder_path / item["old"]
            
            if old_path.exists():
                old_path.rename(new_path)
        
        # Удаляем лог
        self.log_file.unlink()
        
        return len(log)
    
    def preview_rename(self, new_name: str, start_number: int = 1, sort_by: str = "name") -> list:
        """Предпросмотр переименования (без изменений)"""
        files = self.get_files(sort_by)
        preview = []
        
        for index, file_path in enumerate(files, start=start_number):
            ext = file_path.suffix
            new_filename = f"{new_name}_{index}{ext}"
            preview.append({
                "old": file_path.name,
                "new": new_filename
            })
        
        return preview