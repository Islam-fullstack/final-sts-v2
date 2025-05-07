#!/usr/bin/env python
"""
Файл: simulation/metrics_collector.py

Класс MetricsCollector для сбора и анализа метрик эффективности симуляции.

Атрибуты:
  - simulation: ссылка на симулятор
  - collection_interval: интервал сбора данных (сек)
  - last_collection_time: время последнего сбора
  - metrics_history: история собранных метрик

Методы:
  - update(current_time): Обновление метрик, если прошёл интервал
  - collect_metrics(): Сбор метрик по транспортным средствам, очередям и светофорам
  - collect_vehicle_metrics(): Расчёт среднего времени ожидания, средней скорости и throughput
  - collect_queue_metrics(): Stub – случайное значение для длины очереди
  - collect_traffic_light_metrics(): Stub – расчет доли зелёных сигналов по контроллерам
  - get_current_metrics(), get_metrics_history(): получение данных
  - export_to_csv(filename): экспорт истории метрик в CSV
  - generate_report(): генерация текстового отчёта по последним метрикам
  - reset(): сброс метрик
"""

import os
import csv

class MetricsCollector:
    def __init__(self, simulation, config):
        self.simulation = simulation
        self.collection_interval = config.get("collection_interval", 30)
        self.metrics_to_collect = config.get("metrics_to_collect", ["average_waiting_time", "average_speed", "throughput"])
        self.last_collection_time = 0.0
        self.metrics_history = []

    def update(self, current_time):
        if current_time - self.last_collection_time >= self.collection_interval:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            self.last_collection_time = current_time

    def collect_metrics(self):
        vehicle_metrics = self.collect_vehicle_metrics()
        queue_metrics = self.collect_queue_metrics()
        tl_metrics = self.collect_traffic_light_metrics()
        metrics = {**vehicle_metrics, **queue_metrics, **tl_metrics, "time": self.simulation.current_time}
        return metrics

    def collect_vehicle_metrics(self):
        vehicles = self.simulation.vehicles
        if not vehicles:
            return {"average_waiting_time": 0, "average_speed": 0, "throughput": 0}
        total_wait = sum(v.waiting_time for v in vehicles)
        total_speed = sum(v.current_speed for v in vehicles)
        avg_wait = total_wait / len(vehicles)
        avg_speed = total_speed / len(vehicles)
        throughput = len(vehicles)
        return {"average_waiting_time": avg_wait, "average_speed": avg_speed, "throughput": throughput}

    def collect_queue_metrics(self):
        # Stub: возвращаем случайное значение для длины очереди
        import random
        return {"queue_length": random.uniform(5, 20)}

    def collect_traffic_light_metrics(self):
        if self.simulation.controllers:
            total, green = 0, 0
            for ctrl in self.simulation.controllers:
                states = ctrl.get_traffic_light_states()
                for state in states.values():
                    total += 1
                    if state.upper() == "GREEN":
                        green += 1
            ratio = (green / total * 100) if total > 0 else 0
            return {"green_ratio": ratio}
        return {"green_ratio": 0}

    def get_current_metrics(self):
        return self.metrics_history[-1] if self.metrics_history else {}

    def get_metrics_history(self):
        return self.metrics_history

    def export_to_csv(self, filename):
        if not self.metrics_history:
            print("Нет метрик для экспорта.")
            return
        keys = self.metrics_history[0].keys()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for row in self.metrics_history:
                writer.writerow(row)
        print(f"Metrics exported to {filename}")

    def generate_report(self):
        current = self.get_current_metrics()
        report = "Simulation Metrics Report:\n"
        for k, v in current.items():
            report += f"{k}: {v}\n"
        return report

    def reset(self):
        self.metrics_history = []
        self.last_collection_time = 0.0

if __name__ == "__main__":
    # Демонстрация работы MetricsCollector с dummy симулятором
    class DummySimulator:
        def __init__(self):
            self.current_time = 10
            self.vehicles = []
            self.controllers = []
    import random
    sim = DummySimulator()
    for i in range(10):
        dummy = type("DummyVehicle", (), {})()
        dummy.current_speed = random.uniform(10, 30)
        dummy.waiting_time = random.uniform(0, 100)
        sim.vehicles.append(dummy)
    config = {"collection_interval": 10, "metrics_to_collect": ["average_waiting_time", "average_speed", "throughput"]}
    collector = MetricsCollector(sim, config)
    sim.current_time = 10
    collector.update(sim.current_time)
    print("Current metrics:", collector.get_current_metrics())
