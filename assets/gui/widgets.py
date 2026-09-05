import customtkinter as ctk

class FileListItem(ctk.CTkFrame):
    """Виджет для отображения файла в списке"""
    
    def __init__(self, master, filename: str, old_name: str = None, new_name: str = None):
        super().__init__(master)
        
        self.filename = filename
        
        # Старое имя
        self.old_name_label = ctk.CTkLabel(
            self,
            text=old_name or filename,
            font=("Arial", 11),
            anchor="w"
        )
        self.old_name_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        
        # Стрелка
        self.arrow_label = ctk.CTkLabel(
            self,
            text="→",
            font=("Arial", 14),
            text_color="#00BFFF"
        )
        self.arrow_label.pack(side="left", padx=5)
        
        # Новое имя
        self.new_name_label = ctk.CTkLabel(
            self,
            text=new_name or "",
            font=("Arial", 11),
            text_color="#4CAF50",
            anchor="w"
        )
        self.new_name_label.pack(side="left", padx=5, pady=2, fill="x", expand=True)

class ProgressBar(ctk.CTkProgressBar):
    """Прогресс-бар с текстом"""
    
    def __init__(self, master):
        super().__init__(master)
        self.set(0)
        self.progress_label = ctk.CTkLabel(
            master,
            text="0%",
            font=("Arial", 10)
        )
    
    def set_progress(self, value: float):
        """Установить прогресс"""
        self.set(value)
        self.progress_label.configure(text=f"{int(value * 100)}%")  
