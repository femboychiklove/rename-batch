import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog
import sys
import os
import re
import json
import shutil
import time
from pathlib import Path
from datetime import datetime

# Добавляем пути для импортов
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from core.renamer import FileRenamer
from utils.file_ops import get_sorted_files

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Настройки окна
        self.title("Rename Batch — Всё в одном окне")
        self.geometry("1100x800")
        self.resizable(True, True)
        self.minsize(900, 700)
        
        # Тема - СВЕТЛАЯ
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Переменные
        self.current_path = Path.home()
        self.renamer = None
        self.file_checkboxes = {}
        self.history = []
        self.stats = {
            "renamed": 0,
            "deleted": 0,
            "created": 0
        }
        
        # Создаём интерфейс
        self.create_widgets()
        self.update_folder_contents()
    
    def create_widgets(self):
        # ========== ЗАГОЛОВОК ==========
        self.header_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        self.header_frame.pack(pady=10, padx=20, fill="x")
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🔢 Rename Batch",
            font=("Arial", 28, "bold"),
            text_color="#0066cc"
        )
        self.title_label.pack(pady=8)
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Профессиональный инструмент для работы с файлами",
            font=("Arial", 13),
            text_color="#666666"
        )
        self.subtitle_label.pack(pady=(0, 8))
        
        # ========== ОСНОВНОЙ КОНТЕЙНЕР (2 колонки) ==========
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Левая колонка - папки
        self.left_column = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0", width=280)
        self.left_column.pack(side="left", fill="y", padx=(0, 10))
        self.left_column.pack_propagate(False)
        
        # Правая колонка - файлы и настройки
        self.right_column = ctk.CTkFrame(self.main_container, corner_radius=12, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0")
        self.right_column.pack(side="right", fill="both", expand=True)
        
        # ========== ЛЕВАЯ КОЛОНКА (ПАПКИ) ==========
        self.left_title = ctk.CTkLabel(
            self.left_column,
            text="📁 Папки",
            font=("Arial", 16, "bold"),
            text_color="#333333"
        )
        self.left_title.pack(pady=10)
        
        self.path_label = ctk.CTkLabel(
            self.left_column,
            text="",
            font=("Arial", 11),
            text_color="#666666",
            wraplength=250
        )
        self.path_label.pack(pady=5, padx=10)
        
        self.path_entry = ctk.CTkEntry(
            self.left_column,
            placeholder_text="Введите путь...",
            width=240,
            height=32,
            font=("Arial", 11),
            fg_color="#ffffff",
            text_color="#333333",
            border_color="#cccccc"
        )
        self.path_entry.pack(pady=5, padx=10)
        self.path_entry.bind("<Return>", lambda e: self.go_to_path())
        
        self.back_btn = ctk.CTkButton(
            self.left_column,
            text="⬅ Назад",
            command=self.go_up,
            width=100,
            height=30,
            font=("Arial", 12, "bold"),
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        self.back_btn.pack(pady=5)
        
        # Список папок (прокручиваемый)
        self.folders_scroll = ctk.CTkScrollableFrame(
            self.left_column,
            fg_color="#ffffff",
            corner_radius=8
        )
        self.folders_scroll.pack(padx=10, pady=10, fill="both", expand=True)
        
        # ========== ПРАВАЯ КОЛОНКА (ФАЙЛЫ + НАСТРОЙКИ) ==========
        # Секция настроек
        self.settings_section = ctk.CTkFrame(self.right_column, corner_radius=12, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        self.settings_section.pack(pady=10, padx=10, fill="x")
        
        # Имя файла
        self.name_label = ctk.CTkLabel(
            self.settings_section,
            text="✏️ Новое имя:",
            font=("Arial", 13, "bold"),
            text_color="#333333"
        )
        self.name_label.pack(side="left", padx=10, pady=10)
        
        self.name_entry = ctk.CTkEntry(
            self.settings_section,
            placeholder_text="Например: фото_отпуск",
            width=200,
            height=32,
            font=("Arial", 12),
            fg_color="#ffffff",
            text_color="#333333",
            border_color="#cccccc"
        )
        self.name_entry.pack(side="left", padx=10, pady=10)
        
        # Номер
        self.number_label = ctk.CTkLabel(
            self.settings_section,
            text="🔢 Начать с:",
            font=("Arial", 13, "bold"),
            text_color="#333333"
        )
        self.number_label.pack(side="left", padx=10, pady=10)
        
        self.start_number_entry = ctk.CTkEntry(
            self.settings_section,
            width=50,
            height=32,
            font=("Arial", 13, "bold"),
            fg_color="#ffffff",
            text_color="#333333",
            border_color="#cccccc",
            justify="center"
        )
        self.start_number_entry.insert(0, "1")
        self.start_number_entry.pack(side="left", padx=10, pady=10)
        
        # Фильтр
        self.filter_label = ctk.CTkLabel(
            self.settings_section,
            text="🔍 Фильтр:",
            font=("Arial", 13, "bold"),
            text_color="#333333"
        )
        self.filter_label.pack(side="left", padx=10, pady=10)
        
        self.filter_entry = ctk.CTkEntry(
            self.settings_section,
            placeholder_text="jpg, png",
            width=100,
            height=32,
            font=("Arial", 12),
            fg_color="#ffffff",
            text_color="#333333",
            border_color="#cccccc"
        )
        self.filter_entry.pack(side="left", padx=10, pady=10)
        
        # Кнопки действий
        self.actions_buttons = ctk.CTkFrame(self.right_column, corner_radius=12, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        self.actions_buttons.pack(pady=10, padx=10, fill="x")
        
        self.preview_btn = ctk.CTkButton(
            self.actions_buttons,
            text="👁 Предпросмотр",
            command=self.preview_rename,
            font=("Arial", 13, "bold"),
            height=35,
            fg_color="#ff9800",
            hover_color="#f57c00",
            corner_radius=8
        )
        self.preview_btn.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        
        self.rename_btn = ctk.CTkButton(
            self.actions_buttons,
            text="🔄 Переименовать",
            command=self.rename_files,
            font=("Arial", 13, "bold"),
            height=35,
            fg_color="#4caf50",
            hover_color="#388e3c",
            corner_radius=8
        )
        self.rename_btn.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        
        self.undo_btn = ctk.CTkButton(
            self.actions_buttons,
            text="↩️ Отменить",
            command=self.undo_rename,
            font=("Arial", 13, "bold"),
            height=35,
            fg_color="#f44336",
            hover_color="#d32f2f",
            corner_radius=8
        )
        self.undo_btn.pack(side="left", padx=5, pady=10, expand=True, fill="x")
        
        # Список файлов
        self.files_section = ctk.CTkFrame(self.right_column, corner_radius=12, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        self.files_section.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.files_header = ctk.CTkFrame(self.files_section, fg_color="transparent")
        self.files_header.pack(fill="x", padx=10, pady=10)
        
        self.files_label = ctk.CTkLabel(
            self.files_header,
            text="📄 Файлы (отметьте нужные):",
            font=("Arial", 15, "bold"),
            text_color="#333333"
        )
        self.files_label.pack(side="left")
        
        self.select_all_btn = ctk.CTkButton(
            self.files_header,
            text="Выбрать все",
            command=self.select_all_files,
            width=80,
            height=25,
            font=("Arial", 11),
            fg_color="#0066cc",
            hover_color="#0052a3"
        )
        self.select_all_btn.pack(side="right", padx=5)
        
        self.deselect_all_btn = ctk.CTkButton(
            self.files_header,
            text="Снять все",
            command=self.deselect_all_files,
            width=80,
            height=25,
            font=("Arial", 11),
            fg_color="#cccccc",
            hover_color="#b3b3b3"
        )
        self.deselect_all_btn.pack(side="right", padx=5)
        
        # Прокручиваемый список файлов
        self.files_scroll = ctk.CTkScrollableFrame(
            self.files_section,
            fg_color="#ffffff",
            corner_radius=8
        )
        self.files_scroll.pack(padx=10, pady=10, fill="both", expand=True)
        
        # ========== ДОПОЛНИТЕЛЬНЫЕ ДЕЙСТВИЯ ==========
        self.extra_actions = ctk.CTkFrame(self, corner_radius=12, fg_color="#ffffff", border_width=1, border_color="#e0e0e0")
        self.extra_actions.pack(pady=10, padx=20, fill="x")
        
        self.extra_label = ctk.CTkLabel(
            self.extra_actions,
            text="🛠️ Дополнительные действия:",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        self.extra_label.pack(pady=5)
        
        self.delete_btn = ctk.CTkButton(
            self.extra_actions,
            text="🗑️ Удалить выбранные",
            command=self.delete_selected_files,
            font=("Arial", 12, "bold"),
            height=32,
            fg_color="#f44336",
            hover_color="#d32f2f",
            corner_radius=8
        )
        self.delete_btn.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        self.create_btn = ctk.CTkButton(
            self.extra_actions,
            text="📄 Создать файл",
            command=self.create_file,
            font=("Arial", 12, "bold"),
            height=32,
            fg_color="#4caf50",
            hover_color="#388e3c",
            corner_radius=8
        )
        self.create_btn.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        self.copy_btn = ctk.CTkButton(
            self.extra_actions,
            text="📋 Копировать выбранные",
            command=self.copy_selected_files,
            font=("Arial", 12, "bold"),
            height=32,
            fg_color="#2196f3",
            hover_color="#1976d2",
            corner_radius=8
        )
        self.copy_btn.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        self.move_btn = ctk.CTkButton(
            self.extra_actions,
            text="📦 Переместить выбранные",
            command=self.move_selected_files,
            font=("Arial", 12, "bold"),
            height=32,
            fg_color="#9c27b0",
            hover_color="#7b1fa2",
            corner_radius=8
        )
        self.move_btn.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        # ========== СТАТИСТИКА ==========
        self.stats_frame = ctk.CTkFrame(self, corner_radius=12, fg_color="#f8f9fa", border_width=1, border_color="#e0e0e0")
        self.stats_frame.pack(pady=10, padx=20, fill="x")
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="📊 Статистика: переименовано: 0 | удалено: 0 | создано: 0",
            font=("Arial", 13),
            text_color="#333333"
        )
        self.stats_label.pack(side="left", padx=10, pady=8)
        
        self.history_btn = ctk.CTkButton(
            self.stats_frame,
            text="📜 История",
            command=self.show_history,
            width=90,
            height=30,
            font=("Arial", 12),
            fg_color="#607d8b",
            hover_color="#455a64"
        )
        self.history_btn.pack(side="right", padx=10, pady=8)
        
        # ========== СТАТУС ==========
        self.status_label = ctk.CTkLabel(
            self,
            text="✅ Готов к работе",
            font=("Arial", 13),
            text_color="#666666"
        )
        self.status_label.pack(pady=5)
    
    # ============================================================
    #  МЕТОДЫ ДЛЯ РАБОТЫ С ПАПКАМИ
    # ============================================================
    def update_folder_contents(self):
        """Обновить содержимое папки"""
        self.path_label.configure(text=str(self.current_path))
        self.path_entry.delete(0, "end")
        self.path_entry.insert(0, str(self.current_path))
        
        # Очищаем список папок
        for widget in self.folders_scroll.winfo_children():
            widget.destroy()
        
        # Показываем папки
        try:
            folders = [d for d in self.current_path.iterdir() if d.is_dir()]
            folders.sort(key=lambda x: x.name.lower())
            
            for folder in folders:
                folder_btn = ctk.CTkButton(
                    self.folders_scroll,
                    text=f"📁 {folder.name}",
                    anchor="w",
                    font=("Arial", 12),
                    fg_color="transparent",
                    text_color="#333333",
                    hover_color="#e0e0e0",
                    command=lambda f=folder: self.navigate_to(f)
                )
                folder_btn.pack(fill="x", pady=2, padx=5)
        except PermissionError:
            pass
        
        # Обновляем файлы
        self.show_files()
    
    def navigate_to(self, folder_path):
        """Перейти в выбранную папку"""
        self.current_path = folder_path
        self.update_folder_contents()
        self.status_label.configure(text=f"✅ Выбрана папка: {folder_path}", text_color="#0066cc")
    
    def go_up(self):
        """Перейти на уровень выше"""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
            self.update_folder_contents()
    
    def go_to_path(self):
        """Перейти по введённому пути"""
        path_str = self.path_entry.get().strip()
        try:
            new_path = Path(path_str)
            if new_path.exists() and new_path.is_dir():
                self.current_path = new_path
                self.update_folder_contents()
            else:
                messagebox.showerror("Ошибка", "Путь не существует или не является папкой!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось перейти: {str(e)}")
    
    def show_files(self):
        """Показать файлы в текущей папке с чекбоксами"""
        # Очищаем список файлов
        for widget in self.files_scroll.winfo_children():
            widget.destroy()
        
        # Получаем файлы с учётом сортировки
        files = get_sorted_files(self.current_path, "name")
        
        # Применяем фильтр по расширениям
        filter_exts = self.get_filter_extensions()
        if filter_exts:
            files = [f for f in files if f.suffix.lower().lstrip('.') in filter_exts]
        
        # Создаём чекбоксы для файлов
        self.file_checkboxes = {}
        
        for i, file in enumerate(files, 1):
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                self.files_scroll,
                text=f"{i}. 📄 {file.name}",
                variable=var,
                font=("Arial", 12),
                fg_color="#0066cc",
                hover_color="#0052a3",
                text_color="#333333"
            )
            checkbox.pack(fill="x", pady=2, padx=5)
            
            self.file_checkboxes[file] = var
    
    def get_filter_extensions(self) -> list:
        """Получить список расширений"""
        filter_text = self.filter_entry.get().strip()
        if not filter_text:
            return []
        
        extensions = [ext.strip().lower().lstrip('.') for ext in filter_text.split(',')]
        return extensions
    
    # ============================================================
    #  МЕТОДЫ ДЛЯ ВЫБОРА ФАЙЛОВ
    # ============================================================
    def get_selected_files(self) -> list:
        """Получить файлы, выбранные через чекбоксы"""
        selected = []
        for file, var in self.file_checkboxes.items():
            if var.get():
                selected.append(file)
        return selected
    
    def select_all_files(self):
        """Выбрать все файлы"""
        for var in self.file_checkboxes.values():
            var.set(True)
    
    def deselect_all_files(self):
        """Снять выбор со всех файлов"""
        for var in self.file_checkboxes.values():
            var.set(False)
    
    # ============================================================
    #  МЕТОДЫ ДЛЯ ПЕРЕИМЕНОВАНИЯ
    # ============================================================
    def preview_rename(self):
        """Предпросмотр переименования"""
        files = self.get_selected_files()
        if not files:
            messagebox.showerror("Ошибка", "Нет выбранных файлов!")
            return
        
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror("Ошибка", "Введите новое имя!")
            return
        
        try:
            start_number = int(self.start_number_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Начальный номер должен быть числом!")
            return
        
        preview_items = []
        for index, file in enumerate(files, start=start_number):
            ext = file.suffix
            new_filename = f"{new_name}_{index}{ext}"
            preview_items.append({"old": file.name, "new": new_filename})
        
        self.show_preview_window(preview_items)
    
    def show_preview_window(self, preview_items):
        """Показать окно предпросмотра"""
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("👁 Предпросмотр переименования")
        preview_window.geometry("600x500")
        preview_window.attributes("-topmost", True)
        
        header = ctk.CTkLabel(
            preview_window,
            text="Предпросмотр переименования",
            font=("Arial", 20, "bold"),
            text_color="#0066cc"
        )
        header.pack(pady=15)
        
        preview_text = ctk.CTkTextbox(
            preview_window,
            font=("Consolas", 11),
            fg_color="#ffffff",
            text_color="#333333"
        )
        preview_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        for item in preview_items:
            preview_text.insert("end", f"📄 {item['old']}\n")
            preview_text.insert("end", f"   → {item['new']}\n\n")
        
        preview_text.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            preview_window,
            text="Закрыть",
            command=preview_window.destroy,
            font=("Arial", 13, "bold"),
            fg_color="#0066cc",
            hover_color="#0052a3",
            width=100,
            height=35
        )
        close_btn.pack(pady=15)
    
    def rename_files(self):
        """Переименовать выбранные файлы"""
        files = self.get_selected_files()
        if not files:
            messagebox.showerror("Ошибка", "Нет выбранных файлов!")
            return
        
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror("Ошибка", "Введите новое имя!")
            return
        
        try:
            start_number = int(self.start_number_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Начальный номер должен быть числом!")
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            f"Переименовать {len(files)} выбранных файлов в:\n{self.current_path}\n\n"
            f"Новое имя: {new_name}\n"
            f"Начиная с номера: {start_number}\n\n"
            "Продолжить?"
        )
        
        if not result:
            return
        
        try:
            count = self.renamer.rename_files_with_filter(new_name, start_number, "name", files)
            
            self.stats["renamed"] += count
            self.update_stats()
            self.status_label.configure(
                text=f"✅ Переименовано {count} файлов!",
                text_color="#4caf50"
            )
            messagebox.showinfo("Успех", f"Переименовано {count} файлов!")
            
            # Обновляем список файлов
            self.show_files()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    def undo_rename(self):
        """Отменить переименование"""
        if not self.renamer:
            messagebox.showerror("Ошибка", "Сначала выберите папку!")
            return
        
        result = messagebox.askyesno(
            "Подтверждение",
            "Отменить последнее переименование?\n\n"
            "Все файлы будут возвращены к исходным именам."
        )
        
        if not result:
            return
        
        try:
            count = self.renamer.undo_rename()
            
            self.status_label.configure(
                text=f"↩️ Отменено {count} переименований!",
                text_color="#ff9800"
            )
            messagebox.showinfo("Успех", f"Отменено {count} переименований!")
            
            # Обновляем список файлов
            self.show_files()
            
        except FileNotFoundError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
    
    # ============================================================
    #  МЕТОДЫ ДЛЯ УДАЛЕНИЯ, СОЗДАНИЯ, КОПИРОВАНИЯ, ПЕРЕМЕЩЕНИЯ
    # ============================================================
    def delete_selected_files(self):
        """Удалить выбранные файлы"""
        files = self.get_selected_files()
        if not files:
            messagebox.showerror("Ошибка", "Нет выбранных файлов!")
            return
        
        result = messagebox.askyesno(
            "Удаление файлов",
            f"Удалить {len(files)} файлов?\n\n"
            "Это действие нельзя отменить!"
        )
        
        if result:
            deleted = 0
            for file in files:
                try:
                    if file.exists() and file.is_file():
                        file.unlink()
                        deleted += 1
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось удалить {file.name}: {str(e)}")
            
            self.stats["deleted"] += deleted
            self.update_stats()
            self.status_label.configure(text=f"🗑️ Удалено файлов: {deleted}", text_color="#f44336")
            messagebox.showinfo("Готово", f"Удалено файлов: {deleted}")
            
            # Обновляем список
            self.show_files()
    
    def create_file(self):
        """Создать новый файл"""
        filename = simpledialog.askstring("Создать файл", "Введите имя файла:")
        
        if filename:
            try:
                new_file = self.current_path / filename
                if new_file.exists():
                    messagebox.showwarning("Предупреждение", "Файл с таким именем уже существует!")
                    return
                
                new_file.touch()
                self.stats["created"] += 1
                self.update_stats()
                self.status_label.configure(text=f"📄 Создан файл: {filename}", text_color="#4caf50")
                self.show_files()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать файл: {str(e)}")
    
    def copy_selected_files(self):
        """Копировать выбранные файлы в другую папку"""
        files = self.get_selected_files()
        if not files:
            messagebox.showerror("Ошибка", "Нет выбранных файлов!")
            return
        
        target_folder = filedialog.askdirectory(title="Выберите папку для копирования")
        if not target_folder:
            return
        
        copied = 0
        try:
            for file in files:
                if file.exists() and file.is_file():
                    shutil.copy2(file, Path(target_folder) / file.name)
                    copied += 1
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось копировать: {str(e)}")
        
        self.status_label.configure(text=f"📋 Скопировано файлов: {copied}", text_color="#2196f3")
        messagebox.showinfo("Готово", f"Скопировано файлов: {copied}")
    
    def move_selected_files(self):
        """Переместить выбранные файлы в другую папку"""
        files = self.get_selected_files()
        if not files:
            messagebox.showerror("Ошибка", "Нет выбранных файлов!")
            return
        
        target_folder = filedialog.askdirectory(title="Выберите папку для перемещения")
        if not target_folder:
            return
        
        moved = 0
        try:
            for file in files:
                if file.exists() and file.is_file():
                    shutil.move(file, Path(target_folder) / file.name)
                    moved += 1
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось переместить: {str(e)}")
        
        self.status_label.configure(text=f"📦 Перемещено файлов: {moved}", text_color="#9c27b0")
        messagebox.showinfo("Готово", f"Перемещено файлов: {moved}")
        
        # Обновляем список
        self.show_files()
    
    # ============================================================
    #  МЕТОДЫ ДЛЯ СТАТИСТИКИ И ИСТОРИИ
    # ============================================================
    def update_stats(self):
        """Обновить статистику"""
        self.stats_label.configure(
            text=f"📊 Статистика: переименовано: {self.stats['renamed']} | "
                 f"удалено: {self.stats['deleted']} | "
                 f"создано: {self.stats['created']}"
        )
    
    def show_history(self):
        """Показать историю операций"""
        history_window = ctk.CTkToplevel(self)
        history_window.title("📜 История операций")
        history_window.geometry("600x400")
        history_window.attributes("-topmost", True)
        
        header = ctk.CTkLabel(
            history_window,
            text="История операций",
            font=("Arial", 20, "bold"),
            text_color="#0066cc"
        )
        header.pack(pady=15)
        
        history_text = ctk.CTkTextbox(
            history_window,
            font=("Consolas", 11),
            fg_color="#ffffff",
            text_color="#333333"
        )
        history_text.pack(fill="both", expand=True, padx=15, pady=10)
        
        if not self.history:
            history_text.insert("end", "История пуста\n")
        else:
            for item in self.history:
                history_text.insert("end", f"• {item}\n")
        
        history_text.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            history_window,
            text="Закрыть",
            command=history_window.destroy,
            font=("Arial", 13, "bold"),
            fg_color="#0066cc",
            hover_color="#0052a3",
            width=100,
            height=35
        )
        close_btn.pack(pady=15)
    
    def log_action(self, action: str):
        """Записать действие в историю"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append(f"[{timestamp}] {action}")
        if len(self.history) > 50:
            self.history = self.history[-50:]


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()