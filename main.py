#!/usr/bin/env python
"""
main.py

Основной исполняемый файл системы умных светофоров.
Функциональность:
  - Парсинг аргументов командной строки.
  - Загрузка конфигурации из файлов.
  - Инициализация всех компонентов системы.
  - Настройка логирования.
  - Выбор режима работы (simulation, comparison, visualization, detection).
  - Запуск выбранного режима.
  - Обработка завершения работы и сохранение результатов.
  
Аргументы командной строки:
  --config - путь к конфигурационному файлу.
  --mode - режим работы (simulation, comparison, visualization, detection).
  --controller - тип контроллера (traditional, smart, both).
  --duration - продолжительность симуляции.
  --video - путь к видеофайлу для обработки.
  --output - путь для сохранения результатов.
  --debug - включение режима отладки.
  --no-gui - запуск без графического интерфейса.
"""

import argparse
import sys
import os

from utils.config_loader import ConfigLoader
from utils.logger import Logger
from smart_traffic_system import SmartTrafficSystem

def parse_arguments():
    parser = argparse.ArgumentParser(description="Smart Traffic System")
    parser.add_argument("--config", required=True, help="Путь к конфигурационному YAML файлу")
    parser.add_argument("--mode", choices=["simulation", "comparison", "visualization", "detection"], default="simulation", help="Режим работы системы")
    parser.add_argument("--controller", choices=["traditional", "smart", "both"], default="smart", help="Тип контроллера")
    parser.add_argument("--duration", type=int, default=3600, help="Продолжительность симуляции (сек)")
    parser.add_argument("--video", help="Путь к видеофайлу для обработки")
    parser.add_argument("--output", help="Путь для сохранения результатов")
    parser.add_argument("--debug", action="store_true", help="Включение режима отладки")
    parser.add_argument("--no-gui", action="store_true", help="Запуск без графического интерфейса")
    return parser.parse_args()

def main():
    args = parse_arguments()

    # Загрузка конфигурации
    config = ConfigLoader.load_config(args.config)
    
    # Настройка логирования – включаем DEBUG при необходимости
    Logger.setup_logger(level="DEBUG" if args.debug else "INFO", log_file="system.log")
    logger = Logger.get_logger("main")
    logger.info("Запуск системы Smart Traffic System")
    
    # Обновляем конфигурацию для режима и контроллера
    config["mode"] = args.mode
    config["controller"] = args.controller
    if args.duration:
        config.setdefault("simulation", {})["duration"] = args.duration
    if args.video:
        config["video_source"] = args.video
    if args.output:
        config["output_path"] = args.output
    if args.no_gui:
        config.setdefault("visualization", {})["load_gui"] = False
    else:
        config.setdefault("visualization", {})["load_gui"] = True

    # Инициализация системы
    system = SmartTrafficSystem(config)
    system.initialize_components(controller_type=args.controller, load_gui=not args.no_gui)
    
    # Запуск выбранного режима
    if args.mode == "simulation":
        logger.info("Запуск режима симуляции")
        system.run_simulation(args.duration)
    elif args.mode == "comparison":
        logger.info("Запуск режима сравнения контроллеров")
        system.run_comparison(args.controller)
    elif args.mode == "visualization":
        logger.info("Запуск режима визуализации")
        system.run_visualization()
    elif args.mode == "detection":
        if not args.video:
            logger.error("Для режима detection требуется указать путь к видео через аргумент --video")
            sys.exit(1)
        logger.info("Запуск режима детекции")
        system.run_detection(args.video)
    
    # Сохранение результатов, генерация отчёта
    if args.output:
        system.save_state(args.output)
    system.generate_report()
    
    logger.info("Завершение работы системы.")

if __name__ == "__main__":
    main()
