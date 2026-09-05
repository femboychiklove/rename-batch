import sys
import os
from pathlib import Path

# Добавляем пути для импортов
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "gui"))
sys.path.append(str(Path(__file__).parent / "core"))
sys.path.append(str(Path(__file__).parent / "utils"))

# Импортируем главное окно
from gui.main_window import MainWindow

def main():
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()