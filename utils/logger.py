#!/usr/bin/env python
"""
utils/logger.py

Реализует класс Logger для настройки системы логирования.
Методы:
  - setup_logger(level, log_file): настройка логгера.
  - get_logger(name): получение логгера для компонента.
  - set_log_level(level): изменение уровня логирования.
  - log_to_file(message, level): запись в файл лога.
  - log_to_console(message, level): вывод в консоль.
  - get_log_history(): получение истории логов.
"""

import logging

class Logger:
    _log_history = []
    _logger = None

    @staticmethod
    def setup_logger(level, log_file):
        numeric_level = getattr(logging, level.upper(), None)
        logging.basicConfig(level=numeric_level,
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            filename=log_file,
                            filemode="a")
        Logger._logger = logging.getLogger("SmartTrafficSystem")

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

    @staticmethod
    def set_log_level(level):
        numeric_level = getattr(logging, level.upper(), None)
        logging.getLogger().setLevel(numeric_level)

    @staticmethod
    def log_to_file(message, level="INFO"):
        logger = logging.getLogger()
        getattr(logger, level.lower())(message)
        Logger._log_history.append(message)

    @staticmethod
    def log_to_console(message, level="INFO"):
        print(f"[{level}] {message}")
        Logger._log_history.append(message)

    @staticmethod
    def get_log_history():
        return Logger._log_history

if __name__ == "__main__":
    Logger.setup_logger("DEBUG", "test.log")
    logger = Logger.get_logger("Test")
    logger.debug("Test debug")
    Logger.log_to_console("Test message", "INFO")
    print(Logger.get_log_history())
