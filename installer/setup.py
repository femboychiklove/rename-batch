import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def clean_build():
    """Очистить старые сборки"""
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

def build_app():
    """Собрать приложение"""
    
    # Определяем корневую папку проекта (на уровень выше installer)
    project_root = Path(__file__).parent.parent
    
    # Очищаем старые сборки
    clean_build()
    
    # Путь к основному скрипту
    main_script = project_root / "assets" / "main.py"
    
    # Проверяем, что файл существует
    if not main_script.exists():
        print(f"❌ Ошибка: Файл {main_script} не существует!")
        return False
    
    # Параметры сборки
    args = [
        str(main_script),                     # Основной скрипт
        "--name=rename-batch",                # Имя приложения
        "--onefile",                          # Один файл
        "--windowed",                         # Без консоли (GUI)
        f"--icon={project_root / 'installer' / 'icon.ico'}",  # Иконка
        f"--add-data={project_root / 'assets'};assets",       # Добавляем файлы
        "--clean",                            # Очистка кэша
        "--noconfirm",                        # Без подтверждений
    ]
    
    # Запускаем PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\n✅ Сборка завершена!")
    print(f"📦 Файл: {Path('dist') / 'rename-batch'}")
    
    # Проверяем результат
    if os.path.exists("dist/rename-batch.exe"):
        print("💻 Windows: dist/rename-batch.exe")
    elif os.path.exists("dist/rename-batch"):
        print("🐧 Linux: dist/rename-batch")
    
    return True

if __name__ == "__main__":
    build_app()