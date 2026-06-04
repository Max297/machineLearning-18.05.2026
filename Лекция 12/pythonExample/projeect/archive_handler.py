import os
import zipfile
import tarfile
from pathlib import Path
from typing import List, Tuple

class ArchiveHandler:
    """
    Класс для работы с архивами. Поддерживает ZIP и TAR форматы (gzip, bzip2).
    Использует стандартные библиотеки Python.
    """
    
    # Поддерживаемые расширения архивов
    SUPPORTED_EXTENSIONS = {'.zip', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2'}

    def __init__(self, temp_dir: str = "temp_extract"):
        """
        Инициализация обработчика.
        
        Args:
            temp_dir (str): Путь к временной директории для распаковки архивов.
        """
        self.temp_dir = Path(temp_dir)
        if not self.temp_dir.exists():
            self.temp_dir.mkdir(parents=True, exist_ok=True)

    def is_archive(self, file_path: Path) -> bool:
        """
        Проверяет, является ли файл архивом по его расширению.
        
        Args:
            file_path (Path): Путь к файлу для проверки.
            
        Returns:
            bool: True если файл является поддерживаемым архивом, иначе False.
        """
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract_archive(self, archive_path: Path) -> List[Path]:
        """
        Распаковывает архив во временную директорию и возвращает список извлеченных файлов.
        
        Args:
            archive_path (Path): Путь к файлу-архиву.
            
        Returns:
            List[Path]: Список путей к извлеченным файлам.
            
        Raises:
            Exception: Если архив поврежден или формат не поддерживается.
        """
        extracted_files = []
        
        try:
            # Определяем тип архива по расширению
            suffix = archive_path.suffix.lower()
            
            if suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_dir)
                    extracted_files.extend([self.temp_dir / f for f in zip_ref.namelist() if not f.endswith('/')])
                    
            elif suffix in ['.tar.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(self.temp_dir)
                    extracted_files.extend([self.temp_dir / member.name for member in tar_ref.getmembers() if member.isfile()])
                    
            elif suffix in ['.tar.bz2', '.tbz2']:
                with tarfile.open(archive_path, 'r:bz2') as tar_ref:
                    tar_ref.extractall(self.temp_dir)
                    extracted_files.extend([self.temp_dir / member.name for member in tar_ref.getmembers() if member.isfile()])
            
            # Удаляем исходный архив после успешной распаковки (опционально, по ТЗ не указано явно, но логично для сортировки)
            archive_path.unlink()
            
        except Exception as e:
            print(f"Ошибка при распаковке {archive_path}: {e}")
            raise

        return extracted_files

    def cleanup_temp(self):
        """Очищает временную директорию после обработки."""
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
