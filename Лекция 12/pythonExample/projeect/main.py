import logging
from file_sorter import FileSorter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sorter.log"),
        logging.StreamHandler()
    ]
)

def main():
    """
    Основная функция запуска программы.
    """
    try:
        # Инициализация сортировщика с папкой 'files'
        sorter = FileSorter(source_folder="files")
        
        # Запуск мониторинга (бесконечный цикл)
        sorter.start_monitoring()
        
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
