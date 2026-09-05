import os
from pathlib import Path
import shutil

def get_file_extension(filename: str) -> str:
    """Получить расширение файла"""
    return Path(filename).suffix

def is_valid_filename(filename: str) -> bool:
    """Проверить, является ли имя файла допустимым"""
    invalid_chars = '<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)

def get_sorted_files(folder_path: str, sort_by: str = "name") -> list:
    """Получить отсортированный список файлов"""
    path = Path(folder_path)
    files = [f for f in path.iterdir() if f.is_file()]
    
    if sort_by == "name":
        files.sort(key=lambda x: x.name.lower())
    elif sort_by == "date":
        files.sort(key=lambda x: x.stat().st_mtime)
    elif sort_by == "size":
        files.sort(key=lambda x: x.stat().st_size)
    elif sort_by == "extension":
        files.sort(key=lambda x: x.suffix)
    
    return files

def create_backup(folder_path: str, backup_name: str = "backup"):
    """Создать резервную копию файлов"""
    path = Path(folder_path)
    backup_path = path.parent / backup_name
    
    if backup_path.exists():
        shutil.rmtree(backup_path)
    
    shutil.copytree(path, backup_path)
    return backup_path

def get_folder_size(folder_path: str) -> int:
    """Получить размер папки в байтах"""
    total_size = 0
    for file in Path(folder_path).rglob("*"):
        if file.is_file():
            total_size += file.stat().st_size
    return total_size  
