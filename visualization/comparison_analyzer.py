#!/usr/bin/env python
"""
Файл: visualization/comparison_analyzer.py

Класс ComparisonAnalyzer сравнивает результаты различных контроллеров.
Выполняет расчет процентов улучшения, статистические тесты (t-тест, ANOVA), 
корреляционный анализ и экспорт результатов в CSV/LaTeX, а также генерирует полный отчет.
"""

import pandas as pd
import numpy as np
from scipy import stats

class ComparisonAnalyzer:
    def __init__(self, results, config):
        """
        Инициализирует анализатор.
        
        Аргументы:
          results (dict): результаты симуляций, например {"traditional": DataFrame, "smart": DataFrame, ...}
          config (dict): параметры анализа (метрики, статистические тесты, настройки экспорта).
        """
        self.simulation_results = results
        self.metrics = config.get("metrics", [])
        self.statistical_tests = config.get("statistical_tests", [])
        self.export_config = config.get("export", {})

    def calculate_improvement_percentages(self):
        improvements = {}
        trad = self.simulation_results.get("traditional")
        smart = self.simulation_results.get("smart")
        if trad is None or smart is None:
            return improvements
        for metric in self.metrics:
            trad_mean = trad[metric].mean()
            smart_mean = smart[metric].mean()
            improvement = ((trad_mean - smart_mean) / trad_mean * 100) if trad_mean != 0 else 0
            improvements[metric] = improvement
        return improvements

    def calculate_statistical_significance(self):
        significance = {}
        trad = self.simulation_results.get("traditional")
        smart = self.simulation_results.get("smart")
        if trad is None or smart is None:
            return significance
        for metric in self.metrics:
            t_stat, p_val = stats.ttest_ind(trad[metric].dropna(), smart[metric].dropna())
            significance[metric] = p_val
        return significance

    def perform_anova_test(self):
        anova_results = {}
        groups = [df[metric].dropna().values for metric in self.metrics for df in self.simulation_results.values()]
        if groups:
            f_val, p_val = stats.f_oneway(*groups)
            for metric in self.metrics:
                anova_results[metric] = p_val
        return anova_results

    def perform_t_test(self):
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
        combined = None
        for ctrl, df in self.simulation_results.items():
            tmp = df[self.metrics]
            tmp.columns = [f"{ctrl}_{col}" for col in tmp.columns]
            if combined is None:
                combined = tmp
            else:
                combined = pd.concat([combined, tmp], axis=1)
        return combined.corr()

    def find_optimal_parameters(self):
        return {"optimal_param": 42}  # stub

    def create_comparison_table(self):
        table = pd.DataFrame()
        for ctrl, df in self.simulation_results.items():
            means = df[self.metrics].mean()
            table[ctrl] = means
        return table

    def export_to_csv(self, filename):
        table = self.create_comparison_table()
        table.to_csv(filename, index=True)
        print(f"Comparison results exported to {filename}")

    def export_to_latex(self, filename):
        table = self.create_comparison_table()
        with open(filename, "w") as f:
            f.write(table.to_latex())
        print(f"LaTeX table exported to {filename}")

    def generate_full_report(self):
        report = "Comparison Report:\n"
        improvements = self.calculate_improvement_percentages()
        significance = self.calculate_statistical_significance()
        report += "Improvement Percentages:\n"
        for metric, val in improvements.items():
            report += f"{metric}: {val:.2f}%\n"
        report += "Statistical Significance (p-values):\n"
        for metric, p in significance.items():
            report += f"{metric}: p = {p:.4f}\n"
        return report

def main():
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
    print("Improvement Percentages:")
    print(analyzer.calculate_improvement_percentages())
    print("T-test Results:")
    print(analyzer.perform_t_test())
    print("ANOVA Test Results:")
    print(analyzer.perform_anova_test())
    print("Comparison Table:")
    print(analyzer.create_comparison_table())
    report = analyzer.generate_full_report()
    print("Full Report:")
    print(report)
    analyzer.export_to_csv("results/comparison_results.csv")
    analyzer.export_to_latex("results/comparison_table.tex")

if __name__ == "__main__":
    main()
