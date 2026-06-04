import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from archive_handler import ArchiveHandler

class FileSorter:
    """
    Класс для автоматической сортировки файлов по категориям.
    Обрабатывает обычные файлы и архивы (распаковывает их содержимое).
    """

    # Карта категорий и соответствующих расширений
    CATEGORIES = {
        "documents": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".ppt", ".pptx"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
        "videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php", ".rb", ".go"],
        "spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
        "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"] # Архивы тоже можно сортировать отдельно, если не распаковывать
    }

    def __init__(self, source_folder: str = "files"):
        """
        Инициализация сортировщика.
        
        Args:
            source_folder (str): Путь к папке, за которой нужно следить.
        """
        self.source_folder = Path(source_folder)
        if not self.source_folder.exists():
            self.source_folder.mkdir(parents=True, exist_ok=True)
            
        self.archive_handler = ArchiveHandler()
        self._create_category_folders()

    def _create_category_folders(self):
        """Создает папки для каждой категории файлов в исходной директории."""
        for category in self.CATEGORIES:
            (self.source_folder / category).mkdir(exist_ok=True)

    def get_file_category(self, file_path: Path) -> str:
        """
        Определяет категорию файла на основе его расширения.
        
        Args:
            file_path (Path): Путь к файлу.
            
        Returns:
            str: Название категории (например, 'images'). Если расширение неизвестно - 'other'.
        """
        ext = file_path.suffix.lower()
        for category, extensions in self.CATEGORIES.items():
            if ext in extensions:
                return category
        return "other"

    def generate_new_filename(self, original_file: Path, archive_name: Optional[str] = None) -> str:
        """
        Генерирует новое имя файла согласно формату ТЗ.
        Формат: {имя_архива}_{оригинальное_имя}_{дата}.{расширение}
        
        Args:
            original_file (Path): Исходный файл.
            archive_name (str, optional): Имя архива (если файл был внутри него).
            
        Returns:
            str: Новое имя файла.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Получаем оригинальное имя без расширения и с расширением
        stem = original_file.stem
        ext = original_file.suffix
        
        # Формируем префикс (имя архива)
        prefix_part = ""
        if archive_name:
            # Убираем расширение у имени архива для чистоты
            clean_archive_name = Path(archive_name).stem
            prefix_part = f"{clean_archive_name}_"
            
        new_filename = f"{prefix_part}{stem}_{date_str}{ext}"
        
        return new_filename

    def move_to_category(self, file_path: Path, category: str, archive_name: Optional[str] = None):
        """
        Перемещает файл в соответствующую папку категории с новым именем.
        Если файл с таким именем уже существует, добавляет суффикс _dop_N.

        Args:
            file_path (Path): Путь к файлу для перемещения.
            category (str): Целевая категория (имя папки).
            archive_name (str, optional): Имя архива-источника.
        """
        target_dir = self.source_folder / category
        
        # Генерируем базовое имя файла (без учета дубликатов)
        new_filename = self.generate_new_filename(file_path, archive_name)
        target_path = target_dir / new_filename

        counter = 1
        # Если файл с таким именем уже существует в папке назначения, ищем свободное имя
        while target_path.exists():
            stem = file_path.stem
            ext = file_path.suffix
            
            # Формируем префикс (имя архива)
            prefix_part = ""
            if archive_name:
                clean_archive_name = Path(archive_name).stem
                prefix_part = f"{clean_archive_name}_"
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Формируем новое имя с суффиксом _dop_N перед расширением
            # Пример: archive_photo_2024-01-15_dop_1.jpg
            new_filename = f"{prefix_part}{stem}_{date_str}_dop_{counter}{ext}"
            target_path = target_dir / new_filename
            
            counter += 1

        try:
            shutil.move(str(file_path), str(target_path))
            print(f"Перемещено: {file_path.name} -> {target_path.name}")
        except Exception as e:
            print(f"Ошибка при перемещении файла {file_path}: {e}")

    def process_file(self, file_path: Path):
        """
        Главный метод обработки файла. Определяет тип и запускает сортировку.
        
        Args:
            file_path (Path): Путь к файлу в папке мониторинга.
        """
        if not file_path.is_file():
            return

        # Проверяем, является ли файл архивом
        if self.archive_handler.is_archive(file_path):
            print(f"Обнаружен архив: {file_path.name}. Распаковка...")
            
            try:
                extracted_files = self.archive_handler.extract_archive(file_path)
                
                for extracted_file in extracted_files:
                    # Если внутри архива есть еще один архив, обрабатываем рекурсивно (с пометкой о родительском архиве)
                    if self.archive_handler.is_archive(extracted_file):
                        self.process_file(extracted_file)
                    else:
                        category = self.get_file_category(extracted_file)
                        # Передаем имя оригинального архива для формирования имени файла
                        self.move_to_category(extracted_file, category, archive_name=file_path.name)
                        
            except Exception as e:
                print(f"Не удалось обработать архив {file_path}: {e}")
        else:
            # Обычный файл
            category = self.get_file_category(file_path)
            self.move_to_category(file_path, category)

    def start_monitoring(self):
        """
        Запускает цикл мониторинга папки.
        Проверяет наличие новых файлов каждые 2 секунды.
        """
        print(f"Мониторинг папки: {self.source_folder.absolute()}")
        
        # Список уже обработанных файлов (чтобы не обрабатывать один файл дважды)
        processed_files = set()

        while True:
            try:
                current_files = [f for f in self.source_folder.iterdir() if f.is_file()]
                
                for file_path in current_files:
                    # Используем абсолютный путь и время изменения для уникальности
                    file_id = (str(file_path.absolute()), file_path.stat().st_mtime)
                    
                    if file_id not in processed_files:
                        self.process_file(file_path)
                        processed_files.add(file_id)
                        
            except Exception as e:
                print(f"Ошибка при сканировании папки: {e}")

            # Пауза перед следующей проверкой (чтобы не грузить CPU)
            import time
            time.sleep(2)
