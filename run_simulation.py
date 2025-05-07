#!/usr/bin/env python
"""
run_simulation.py

Скрипт для запуска симуляции.
Функциональность:
  - Инициализация симулятора с выбранной конфигурацией.
  - Настройка контроллера указанного типа.
  - Запуск симуляции на заданное время.
  - Сбор и сохранение метрик.
  - Опциональная визуализация процесса.
  - Сохранение результатов для дальнейшего анализа.
"""

import yaml
from simulation.simulator import TrafficSimulator

def main():
    config_file = "configs/simulation.yaml"
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    simulator = TrafficSimulator(config)
    simulator.setup_environment()
    simulator.setup_controllers()
    simulator.setup_traffic_generators()
    simulator.setup_metrics_collector()

    duration = config.get("simulation", {}).get("duration", 3600)
    simulator.run(duration)
    
    simulator.save_state("results/simulation_state.pkl")

if __name__ == "__main__":
    main()
