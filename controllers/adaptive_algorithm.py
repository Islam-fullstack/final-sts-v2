"""
Файл: controllers/adaptive_algorithm.py

Описание:
  Данный модуль реализует базовые стратегии принятия решений для адаптивного управления.
  
  Реализованы следующие классы:
    - AdaptiveAlgorithm: базовый класс (можно расширить для различных стратегий).
    - WebsterAlgorithm: классический алгоритм Вебстера (stub).
    - QueueLengthOptimizer: оптимизация на основе длин очередей (stub).
    - WaitingTimeOptimizer: оптимизация на основе времени ожидания (stub).
    - RLBasedController: контроллер на основе обучения с подкреплением (Q-learning, stub).
    - HybridController: гибридный подход, объединяющий несколько стратегий; эта реализация используется в SmartController.
"""

import random

class AdaptiveAlgorithm:
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        """
        Базовый метод принятия решения.
        Возвращает:
          tuple: (next_phase, optimal_duration)
        """
        raise NotImplementedError("Метод decide() должен быть реализован в наследниках.")

    def save_model(self, filename):
        """Сохранение модели (stub)."""
        pass
    
    def load_model(self, filename):
        """Загрузка модели (stub)."""
        pass

class WebsterAlgorithm(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        # Stub-реализация: возвращает случайную фазу и среднюю длительность
        next_phase = random.choice([1,2,3,4])
        optimal_duration = (min_duration + max_duration) / 2
        return next_phase, optimal_duration

class QueueLengthOptimizer(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        # Stub: выбираем фазу с минимальной суммой длин очередей (условно)
        next_phase = random.choice([1,2,3,4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class WaitingTimeOptimizer(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        # Stub: выбираем фазу с минимальным временем ожидания (условно)
        next_phase = random.choice([1,2,3,4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class RLBasedController(AdaptiveAlgorithm):
    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        # Stub: использование Q-learning (реализовать отдельную модель)
        next_phase = random.choice([1,2,3,4])
        optimal_duration = min_duration + random.random() * (max_duration - min_duration)
        return next_phase, optimal_duration

class HybridController(AdaptiveAlgorithm):
    def __init__(self, config, phases):
        """
        Инициализирует гибридный контроллер.
        
        Аргументы:
          config (dict): Параметры адаптивного алгоритма.
          phases (list): Список конфигураций фаз.
        """
        self.config = config
        self.phases = phases
        # Из конфигурации можно прочитать веса для оптимизации
        self.qt_weight = config.get("queue_length", {}).get("weight", 0.7)
        self.wt_weight = config.get("waiting_time", {}).get("weight", 0.3)

    def decide(self, traffic_data, current_phase, min_duration, max_duration, queue_lengths, waiting_times):
        """
        Гибридная стратегия: рассчитывает стоимость каждой фазы как взвешенную сумму
        средней длины очереди и времени ожидания. Выбирается фаза с минимальной стоимостью.
        
        Возвращает:
          tuple: (next_phase, optimal_duration)
        """
        # Для упрощения предположим, что каждая фаза имеет id из набора {1,2,3,4}
        phase_ids = [phase["id"] for phase in self.phases]
        cost_dict = {}
        # Если данные отсутствуют, используем случайное значение
        avg_queue = sum(queue_lengths.values()) / len(queue_lengths) if queue_lengths else 10
        avg_wait = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 50
        
        for pid in phase_ids:
            # Стоимость рассчитывается как:
            # cost = qt_weight * avg_queue + wt_weight * avg_wait + random фоновый шум
            cost = self.qt_weight * avg_queue + self.wt_weight * avg_wait + random.random() * 5
            cost_dict[pid] = cost
        # Выбираем фазу с минимальной стоимостью
        next_phase = min(cost_dict, key=cost_dict.get)
        # Оптимальная длительность – можно брать среднее между min и max для выбранной фазы
        optimal_duration = (min_duration + max_duration) / 2
        return next_phase, optimal_duration

    def save_model(self, filename):
        # Stub: здесь можно сохранить параметры (например, веса) в файл
        with open(filename, 'w') as f:
            f.write(str(self.config))

    def load_model(self, filename):
        # Stub: загрузка параметров из файла
        with open(filename, 'r') as f:
            data = f.read()
        self.config = eval(data)  # не рекомендуется для production

