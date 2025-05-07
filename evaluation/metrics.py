#!/usr/bin/env python
"""
Файл: evaluation/metrics.py

Реализует функции для расчета метрик эффективности симуляции.
"""

def compute_wait_times(traffic_flow):
    if not traffic_flow.vehicles:
        return 0
    total_wait = sum(vehicle.waiting_time for vehicle in traffic_flow.vehicles)
    return total_wait / len(traffic_flow.vehicles)

def compute_throughput(road):
    return len(road.vehicles)

if __name__ == "__main__":
    class DummyFlow:
        def __init__(self, vehicles):
            self.vehicles = vehicles
    class DummyVehicle:
        def __init__(self, waiting_time):
            self.waiting_time = waiting_time
    flow = DummyFlow([DummyVehicle(10), DummyVehicle(20), DummyVehicle(30)])
    print("Average waiting time:", compute_wait_times(flow))
