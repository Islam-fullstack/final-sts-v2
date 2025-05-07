"""
Файл: visualization/comparison_analyzer.py

Реализует класс ComparisonAnalyzer для сравнения алгоритмов управления.
Проводятся расчёты процентов улучшения, статистическая оценка (t-тест, ANOVA) и построение таблицы сравнений.
Также имеется экспорт результатов в CSV и LaTeX, а также генерация полного отчёта.
"""

import pandas as pd
import numpy as np
from scipy import stats


class ComparisonAnalyzer:
    def __init__(self, results, config):
        """
        Инициализирует анализатор сравнительных результатов.
        
        Аргументы:
          results (dict): Результаты симуляций, например: {"traditional": DataFrame, "smart": DataFrame, ...}
          config (dict): Конфигурация анализа (метрики, статистические тесты, настройки экспорта).
        """
        self.simulation_results = results
        self.metrics = config.get("metrics", [])
        self.statistical_tests = config.get("statistical_tests", [])
    
    def load_results(self, directories):
        """
        Загружает результаты из директорий (CSV файлы).
        
        Аргументы:
          directories (dict): Словарь {controller_type: directory}
        """
        self.simulation_results = {}
        for ctrl, directory in directories.items():
            df = pd.read_csv(f"{directory}/metrics.csv")
            self.simulation_results[ctrl] = df
    
    def calculate_improvement_percentages(self):
        """
        Рассчитывает процент улучшения по каждой метрике по сравнению с традиционным контроллером.
        
        Возвращает:
          dict: {metric_name: improvement_percentage}
        """
        improvements = {}
        traditional = self.simulation_results.get("traditional")
        smart = self.simulation_results.get("smart")
        if traditional is None or smart is None:
            return improvements
        for metric in self.metrics:
            trad_mean = traditional[metric].mean()
            smart_mean = smart[metric].mean()
            improvement = ((trad_mean - smart_mean) / trad_mean * 100) if trad_mean != 0 else 0
            improvements[metric] = improvement
        return improvements

    def calculate_statistical_significance(self):
        """
        Оценивает статистическую значимость различий для каждой метрики.
        
        Возвращает:
          dict: {metric_name: p-value}
        """
        significance = {}
        traditional = self.simulation_results.get("traditional")
        smart = self.simulation_results.get("smart")
        if traditional is None or smart is None:
            return significance
        for metric in self.metrics:
            t_stat, p_val = stats.ttest_ind(traditional[metric].dropna(), smart[metric].dropna())
            significance[metric] = p_val
        return significance

    def perform_anova_test(self):
        """
        Выполняет ANOVA-тест для сравнения метрик между группами.
        
        Возвращает:
          dict: {metric_name: p-value}
        """
        anova_results = {}
        for metric in self.metrics:
            groups = [df[metric].dropna().values for df in self.simulation_results.values()]
            f_val, p_val = stats.f_oneway(*groups)
            anova_results[metric] = p_val
        return anova_results

    def perform_t_test(self):
        """
        Выполняет парный t-тест между традиционным и умным контроллерами.
        
        Возвращает:
          dict: {metric_name: p-value}
        """
        t_test_results = {}
        trad = self.simulation_results.get("traditional")
        smart = self.simulation_results.get("smart")
        if trad is None or smart is None:
            return t_test_results
        for metric in self.metrics:
            t_stat, p_val = stats.ttest_rel(trad[metric].dropna(), smart[metric].dropna())
            t_test_results[metric] = p_val
        return t_test_results

    def calculate_correlation_matrix(self):
        """
        Рассчитывает корреляционную матрицу для всех метрик.
        
        Возвращает:
          DataFrame: матрица корреляций.
        """
        combined = None
        for ctrl, df in self.simulation_results.items():
            df = df[self.metrics]
            df.columns = [f"{ctrl}_{col}" for col in df.columns]
            if combined is None:
                combined = df
            else:
                combined = pd.concat([combined, df], axis=1)
        return combined.corr()

    def find_optimal_parameters(self):
        """
        Поиск оптимальных параметров (stub-реализация).
        
        Возвращает:
          dict: оптимальные параметры.
        """
        return {"optimal_param": 42}

    def create_comparison_table(self):
        """
        Создаёт таблицу сравнения метрик между контроллерами.
        
        Возвращает:
          DataFrame: таблица сравнений.
        """
        table = pd.DataFrame()
        for ctrl, df in self.simulation_results.items():
            means = df[self.metrics].mean()
            table[ctrl] = means
        return table

    def export_to_csv(self, filename):
        """Экспортирует таблицу сравнения в CSV файл."""
        table = self.create_comparison_table()
        table.to_csv(filename, index=True)

    def export_to_latex(self, filename):
        """Экспортирует таблицу сравнения в LaTeX формат."""
        table = self.create_comparison_table()
        with open(filename, "w") as f:
            f.write(table.to_latex())

    def generate_full_report(self):
        """
        Генерирует полный текстовый отчёт, включая проценты улучшения и p-значения тестов.
        
        Возвращает:
          str: Отчёт.
        """
        report = "Comparison Report:\n"
        improvements = self.calculate_improvement_percentages()
        significance = self.calculate_statistical_significance()
        report += "Improvement Percentages:\n"
        for metric, value in improvements.items():
            report += f"{metric}: {value:.2f}%\n"
        report += "Statistical Significance (p-values):\n"
        for metric, p_val in significance.items():
            report += f"{metric}: p = {p_val:.4f}\n"
        return report


def main():
    """
    Демонстрация работы ComparisonAnalyzer.
    Создаются dummy DataFrame с результатами для традиционного и умного контроллеров,
    выполняется анализ, выводятся проценты улучшения, результаты t-теста и ANOVA, а также создается таблица сравнения.
    """
    import pandas as pd
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
    config = {
        "metrics": ["average_waiting_time", "max_queue_length", "average_throughput", "total_fuel_consumption", "total_emissions"],
        "statistical_tests": ["t_test", "anova"],
        "export": {
            "csv_file": "results/comparison_results.csv",
            "latex_file": "results/comparison_table.tex",
            "report_file": "results/comparison_report.pdf"
        }
    }
    analyzer = ComparisonAnalyzer(results, config)
    improvements = analyzer.calculate_improvement_percentages()
    t_test = analyzer.perform_t_test()
    anova = analyzer.perform_anova_test()
    table = analyzer.create_comparison_table()
    report = analyzer.generate_full_report()

    print("Improvement Percentages:")
    print(improvements)
    print("T-test Results:")
    print(t_test)
    print("ANOVA Test Results:")
    print(anova)
    print("Comparison Table:")
    print(table)
    print("Full Report:")
    print(report)
    # Экспорт результатов
    analyzer.export_to_csv("results/comparison_results.csv")
    analyzer.export_to_latex("results/comparison_table.tex")


if __name__ == '__main__':
    main()
