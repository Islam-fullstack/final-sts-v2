#!/usr/bin/env python
"""
Файл: evaluation/comparison.py

Реализует функцию compare для сравнения эффективности различных алгоритмов управления.
"""

def compare(metrics_traditional, metrics_smart):
    comparison_results = {}
    for key in metrics_traditional.keys():
        comparison_results[key] = {
            "traditional": metrics_traditional.get(key),
            "smart": metrics_smart.get(key),
            "difference": metrics_smart.get(key) - metrics_traditional.get(key)
        }
    return comparison_results

if __name__ == "__main__":
    trad = {"avg_wait": 20, "throughput": 80}
    smart = {"avg_wait": 18, "throughput": 85}
    comp = compare(trad, smart)
    print("Comparison results:")
    print(comp)
