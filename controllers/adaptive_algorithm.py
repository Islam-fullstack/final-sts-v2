#!/usr/bin/env python
"""
Файл: controllers/adaptive_algorithm.py

Реализует базовые стратегии принятия решений для адаптивного управления.
Содержит следующие классы:
  - AdaptiveAlgorithm (базовый)
  - WebsterAlgorithm (stub)
  - QueueLengthOptimizer (stub)
  - WaitingTimeOptimizer (stub)
  - RLBasedController (stub)
  - HybridController – гибридный подход (используется в SmartController)
"""

import random

class AdaptiveAlgorithm:
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        raise NotImplementedError("Метод decide() должен быть реализован в наследниках.")

    def save_model(self, filename):
        pass
    
    def load_model(self, filename):
        pass

class WebsterAlgorithm(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        next_phase = random.choice([1, 2, 3, 4])
        optimal_duration = (min_duration + max_duration) / 2
        return next_phase, optimal_duration

class QueueLengthOptimizer(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        next_phase = random.choice([1, 2, 3, 4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class WaitingTimeOptimizer(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        next_phase = random.choice([1, 2, 3, 4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class RLBasedController(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        next_phase = random.choice([1, 2, 3, 4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class HybridController(AdaptiveAlgorithm):
    def __init__(self, config, phases):
        self.config = config
        self.phases = phases
        self.qt_weight = config.get("queue_length", {}).get("weight", 0.7)
        self.wt_weight = config.get("waiting_time", {}).get("weight", 0.3)

    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        phase_ids = [phase["id"] for phase in self.phases]
        cost_dict = {}
        avg_queue = sum(queue_lengths.values()) / len(queue_lengths) if queue_lengths else 10
        avg_wait = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 50
        for pid in phase_ids:
            cost = self.qt_weight * avg_queue + self.wt_weight * avg_wait + random.random() * 5
            cost_dict[pid] = cost
        next_phase = min(cost_dict, key=cost_dict.get)
        optimal_duration = (min_duration + max_duration) / 2
        return next_phase, optimal_duration

    def save_model(self, filename):
        with open(filename, 'w') as f:
            f.write(str(self.config))

    def load_model(self, filename):
        with open(filename, 'r') as f:
            data = f.read()
        self.config = eval(data)  # Замечание: eval использовать осторожно

if __name__ == "__main__":
    # Простейшая демонстрация работы HybridController
    config = {
        "queue_length": {"weight": 0.7},
        "waiting_time": {"weight": 0.3}
    }
    phases = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]
    controller = HybridController(config, phases)
    result = controller.decide({}, 1, 20, 60, {"a": 10, "b": 20}, {"a": 30, "b": 40})
    print("Результат решения:", result)
