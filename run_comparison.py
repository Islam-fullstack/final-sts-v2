#!/usr/bin/env python
"""
run_comparison.py

Скрипт для сравнения различных контроллеров.
Функциональность:
  - Последовательный запуск симуляций с разными контроллерами.
  - Сбор метрик для каждого контроллера.
  - Сравнительный анализ результатов.
  - Построение графиков и диаграмм.
  - Генерация отчета.
  - Сохранение результатов анализа.
"""

import yaml
import pandas as pd
from visualization.comparison_analyzer import ComparisonAnalyzer

def main():
    # Для демонстрации используем dummy DataFrame результатов
    data_traditional = pd.DataFrame({
        "average_waiting_time": [20, 22, 19, 21],
        "max_queue_length": [15, 16, 14, 17],
        "average_throughput": [80, 82, 78, 81],
        "total_fuel_consumption": [50, 52, 48, 51],
        "total_emissions": [30, 29, 31, 30]
    })
    data_smart = pd.DataFrame({
        "average_waiting_time": [18, 19, 17, 18],
        "max_queue_length": [13, 14, 12, 13],
        "average_throughput": [85, 87, 84, 86],
        "total_fuel_consumption": [45, 46, 44, 45],
        "total_emissions": [28, 27, 29, 28]
    })
    results = {"traditional": data_traditional, "smart": data_smart}
    analysis_config = {
        "metrics": ["average_waiting_time", "max_queue_length", "average_throughput", "total_fuel_consumption", "total_emissions"],
        "statistical_tests": ["t_test", "anova"],
        "export": {
            "csv_file": "results/comparison_results.csv",
            "latex_file": "results/comparison_table.tex",
            "report_file": "results/comparison_report.pdf"
        }
    }
    analyzer = ComparisonAnalyzer(results, analysis_config)
    report = analyzer.generate_full_report()
    print(report)
    analyzer.export_to_csv("results/comparison_results.csv")
    analyzer.export_to_latex("results/comparison_table.tex")

if __name__ == "__main__":
    main()
