"""
Файл: visualization/data_processor.py

Реализует класс DataProcessor для обработки и анализа данных симуляции.
Методы позволяют загружать данные, фильтровать, агрегировать, рассчитывать скользящие средние,
обнаруживать пиковые периоды и аномалии, нормализовывать данные и экспортировать обработанные данные.
"""

import pandas as pd
import numpy as np


class DataProcessor:
    def load_simulation_data(self, filename):
        """
        Загружает данные симуляции из CSV файла.
        
        Аргументы:
          filename (str): Путь к файлу.
        
        Возвращает:
          DataFrame: Загруженные данные.
        """
        return pd.read_csv(filename)

    def filter_data(self, data, criteria):
        """
        Фильтрует данные по заданным критериям.
        
        Аргументы:
          data (DataFrame): Исходные данные.
          criteria (dict): Словарь условий фильтрации, например {"column": value}.
        
        Возвращает:
          DataFrame: Отфильтрованные данные.
        """
        for col, val in criteria.items():
            data = data[data[col] == val]
        return data

    def aggregate_data(self, data, group_by, aggregate_func):
        """
        Агрегирует данные по указанным столбцам с использованием выбранных функций.
        
        Аргументы:
          data (DataFrame): Исходные данные.
          group_by (str или list): Столбцы для группировки.
          aggregate_func (dict): Функции агрегации, например {"column": "mean"}.
        
        Возвращает:
          DataFrame: Агрегированные данные.
        """
        return data.groupby(group_by).agg(aggregate_func)

    def calculate_moving_average(self, data, window_size):
        """
        Рассчитывает скользящее среднее для заданных данных.
        
        Аргументы:
          data (Series или DataFrame): Данные.
          window_size (int): Размер окна.
        
        Возвращает:
          Series или DataFrame: Значения скользящего среднего.
        """
        return data.rolling(window=window_size).mean()

    def calculate_peak_periods(self, data, threshold):
        """
        Определяет пиковые периоды (когда значение превышает порог).
        
        Аргументы:
          data (Series): Данные.
          threshold (float): Пороговое значение.
        
        Возвращает:
          DataFrame: Строки с пиковыми значениями.
        """
        return data[data > threshold]

    def detect_anomalies(self, data, method="z_score", threshold=3):
        """
        Обнаруживает аномалии в данных.
        
        Аргументы:
          data (Series): Данные.
          method (str): Метод обнаружения ("z_score").
          threshold (float): Порог для z-оценки.
        
        Возвращает:
          Series: Булев массив, где True означает наличие аномалии.
        """
        if method == "z_score":
            mean = data.mean()
            std = data.std()
            if std == 0:
                # Если стандартное отклонение равно нулю, аномалии отсутствуют
                return data.apply(lambda x: False)
            z_scores = (data - mean) / std
            anomalies = abs(z_scores) > threshold
            return anomalies
        else:
            raise ValueError(f"Метод обнаружения аномалий '{method}' не поддерживается.")

    def detect_patterns(self, data):
        """
        Обнаруживает паттерны в данных.
        Stub-реализация: возвращает список найденных периодов, где данные колеблются с периодичностью.
        
        Аргументы:
          data (Series): Временной ряд с данными.
        
        Возвращает:
          list: Найденные паттерны.
        """
        # Простейший алгоритм: если разница между соседними точками меняет знак более 3 раз за окно, фиксируем паттерн.
        patterns = []
        sign_changes = 0
        previous_diff = None
        for i in range(1, len(data)):
            diff = data.iloc[i] - data.iloc[i-1]
            if previous_diff is not None and np.sign(diff) != np.sign(previous_diff):
                sign_changes += 1
            previous_diff = diff
            if sign_changes >= 3:
                patterns.append((i-3, i))
                sign_changes = 0
        return patterns

    def normalize_data(self, data):
        """
        Нормализует данные к диапазону [0, 1].
        
        Аргументы:
          data (Series или DataFrame): Входные данные.
        
        Возвращает:
          аналогичная структура данных с нормализованными значениями.
        """
        min_val = data.min()
        max_val = data.max()
        if max_val == min_val:
            return data.apply(lambda x: 0.0)
        return (data - min_val) / (max_val - min_val)

    def export_processed_data(self, data, filename):
        """
        Экспортирует обработанные данные в CSV файл.
        
        Аргументы:
          data (DataFrame): Данные для экспорта.
          filename (str): Путь к файлу.
        """
        data.to_csv(filename, index=False)
        print(f"Processed data экспортированы в {filename}")


def main():
    """
    Демонстрация работы DataProcessor.
    Загружает dummy-данные, выполняет фильтрацию, агрегирование, расчет скользящего среднего,
    обнаружение аномалий, нормализацию и экспорт обработанных данных.
    """
    # Создаем dummy DataFrame с данными симуляции
    df = pd.DataFrame({
        "time": np.arange(0, 100, 1),
        "waiting_time": np.random.normal(20, 5, 100)
    })

    processor = DataProcessor()
    
    # Фильтрация: оставим данные, где время больше 50
    filtered = processor.filter_data(df, {"time": 50})
    print("Filtered data:")
    print(filtered.head())

    # Агрегация: среднее время ожидания по каждому времени (группировка по time)
    aggregated = processor.aggregate_data(df, ["time"], {"waiting_time": "mean"})
    print("Aggregated data:")
    print(aggregated.head())

    # Скользящее среднее
    moving_avg = processor.calculate_moving_average(df["waiting_time"], window_size=5)
    print("Moving average:")
    print(moving_avg.head())

    # Пиковые периоды (если значение waiting_time > 25)
    peak_periods = processor.calculate_peak_periods(df["waiting_time"], threshold=25)
    print("Peak periods:")
    print(peak_periods.head())

    # Обнаружение аномалий по z-оценке
    anomalies = processor.detect_anomalies(df["waiting_time"], method="z_score", threshold=2)
    print("Anomalies:")
    print(anomalies.head())

    # Обнаружение паттернов
    patterns = processor.detect_patterns(df["waiting_time"])
    print("Detected patterns:")
    print(patterns)

    # Нормализация данных
    normalized = processor.normalize_data(df["waiting_time"])
    print("Normalized data:")
    print(normalized.head())

    # Экспорт обработанных данных
    processor.export_processed_data(df, "processed_simulation_data.csv")


if __name__ == '__main__':
    main()