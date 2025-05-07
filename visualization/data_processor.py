#!/usr/bin/env python
"""
Файл: visualization/data_processor.py

Класс DataProcessor для обработки и анализа данных симуляции.

Методы:
  - load_simulation_data(filename): загрузка данных из CSV.
  - filter_data(data, criteria): фильтрация данных по условиям.
  - aggregate_data(data, group_by, aggregate_func): агрегация данных.
  - calculate_moving_average(data, window_size): расчет скользящего среднего.
  - calculate_peak_periods(data, threshold): определение пиковых периодов.
  - detect_anomalies(data, method, threshold): обнаружение аномалий с использованием z-оценки.
  - detect_patterns(data): обнаружение паттернов (stub).
  - normalize_data(data): нормализация данных.
  - export_processed_data(data, filename): экспорт данных в CSV.
"""

import pandas as pd
import numpy as np

class DataProcessor:
    def load_simulation_data(self, filename):
        return pd.read_csv(filename)

    def filter_data(self, data, criteria):
        for col, val in criteria.items():
            data = data[data[col] == val]
        return data

    def aggregate_data(self, data, group_by, aggregate_func):
        return data.groupby(group_by).agg(aggregate_func)

    def calculate_moving_average(self, data, window_size):
        return data.rolling(window=window_size).mean()

    def calculate_peak_periods(self, data, threshold):
        return data[data > threshold]

    def detect_anomalies(self, data, method="z_score", threshold=3):
        if method == "z_score":
            mean = data.mean()
            std = data.std()
            if std == 0:
                return data.apply(lambda x: False)
            z_scores = (data - mean) / std
            anomalies = abs(z_scores) > threshold
            return anomalies
        else:
            raise ValueError(f"Метод {method} не поддерживается.")

    def detect_patterns(self, data):
        patterns = []
        sign_changes = 0
        previous_diff = None
        for i in range(1, len(data)):
            diff = data.iloc[i] - data.iloc[i-1]
            if previous_diff is not None and np.sign(diff) != np.sign(previous_diff):
                sign_changes += 1
            else:
                sign_changes = 0
            previous_diff = diff
            if sign_changes >= 3:
                patterns.append((i-3, i))
                sign_changes = 0
        return patterns

    def normalize_data(self, data):
        min_val = data.min()
        max_val = data.max()
        if max_val == min_val:
            return data.apply(lambda x: 0.0)
        return (data - min_val) / (max_val - min_val)

    def export_processed_data(self, data, filename):
        data.to_csv(filename, index=False)
        print(f"Processed data exported to {filename}")

def main():
    df = pd.DataFrame({
        "time": np.arange(0, 100, 1),
        "waiting_time": np.random.normal(20, 5, 100)
    })
    processor = DataProcessor()
    filtered = processor.filter_data(df, {"time": 50})
    print("Filtered data:")
    print(filtered.head())
    aggregated = processor.aggregate_data(df, ["time"], {"waiting_time": "mean"})
    print("Aggregated data:")
    print(aggregated.head())
    moving_avg = processor.calculate_moving_average(df["waiting_time"], window_size=5)
    print("Moving average:")
    print(moving_avg.head())
    peak_periods = processor.calculate_peak_periods(df["waiting_time"], threshold=25)
    print("Peak periods:")
    print(peak_periods.head())
    anomalies = processor.detect_anomalies(df["waiting_time"], method="z_score", threshold=2)
    print("Anomalies:")
    print(anomalies.head())
    patterns = processor.detect_patterns(df["waiting_time"])
    print("Detected patterns:")
    print(patterns)
    normalized = processor.normalize_data(df["waiting_time"])
    print("Normalized data:")
    print(normalized.head())
    processor.export_processed_data(df, "processed_simulation_data.csv")

if __name__ == "__main__":
    main()
