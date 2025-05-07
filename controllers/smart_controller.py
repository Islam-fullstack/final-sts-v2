"""
Файл: controllers/smart_controller.py

Описание:
  Модуль реализует класс SmartController для адаптивного управления светофорами.
  Контроллер учитывает текущие данные о транспортном потоке, прогнозирует изменения,
  рассчитывает затраты времени ожидания и длины очередей, а также использует гибридный алгоритм
  принятия решений (реализуемый в AdaptiveAlgorithm/HyrbidController) для выбора следующей фазы.
  
  Ключевые атрибуты:
    - traffic_light_groups: группы синхронизированных светофоров
    - current_phase: текущая активная фаза
    - time_in_current_phase: время нахождения в текущей фазе
    - min_phase_duration, max_phase_duration: границы длительности фазы
    - traffic_data: данные о плотности транспортного потока (например, очереди и время ожидания)
    - prediction_model: модель для прогнозирования изменений потока (TrafficPredictor)
    - queue_lengths, waiting_times: текущие значения по направлениям
    - decision_algorithm: алгоритм принятия решений (например, HybridController)
    - learning_enabled: флаг режима обучения
    - state_history, performance_history: история системных состояний и эффективности работы
  
  Методы:
    - __init__(traffic_lights, config): инициализация
    - update(time_step): обновление состояния контроллера на заданном временном шаге
    - update_traffic_data(data): обновление данных о текущем трафике
    - decide_next_phase(): выбор следующей фазы на основе данных
    - decide_phase_duration(): выбор оптимальной длительности фазы
    - switch_to_phase(phase_id): переключение светофорной системы на указанную фазу
    - calculate_phase_priority(phase): расчёт приоритета фазы (stub)
    - predict_flow_changes(): прогнозирование изменений трафика
    - optimize_phase_sequence(): оптимизация последовательности фаз (stub)
    - calculate_waiting_time_cost(): расчёт затрат по времени ожидания
    - calculate_queue_length_cost(): расчёт затрат по длине очередей
    - calculate_total_cost(): суммарный расчёт затрат текущего состояния
    - learn_from_history(): обучение на основе накопленных данных (stub)
    - save_model(filename), load_model(filename): сохранение и загрузка модели обучения
    - reset(): сброс состояния контроллера
    - get_traffic_light_states(): получение текущих состояний всех светофоров (реализация абстрактного метода)
    
  Функция main() демонстрирует:
    - Создание модели перекрёстка с датчиками (с использованием dummy-объектов)
    - Загрузку конфигурации (либо из файла, либо из примера)
    - Инициализацию умного контроллера
    - Симуляцию работы в течение нескольких циклов (с изменением интенсивности трафика)
    - Вывод ключевых метрик эффективности и сравнение с традиционным контроллером
"""

import yaml
import logging
import random
import time
import os

from controllers.base_controller import BaseController
from controllers.adaptive_algorithm import HybridController
from controllers.traffic_predictor import TrafficPredictor
from controllers.ml_models import QValueModel, TrafficFlowRegressor, WaitingTimePredictor

class SmartController(BaseController):
    def __init__(self, traffic_lights, config):
        """
        Инициализация умного контроллера.
        
        Аргументы:
          traffic_lights (list): Список объектов светофоров.
          config (dict): Конфигурация адаптивного контроллера (загружается из YAML).
        """
        super().__init__(traffic_lights, config)
        self.config = config
        self.phases = config.get("phases", [])
        # Начинаем с первой фазы (предполагается, что phases задаются в порядке переключения)
        self.current_phase = self.phases[0]["id"] if self.phases else None
        self.time_in_current_phase = 0.0
        # Для текущей фазы задаём границы длительности
        self.min_phase_duration = self.phases[0].get("min_duration", 20)
        self.max_phase_duration = self.phases[0].get("max_duration", 60)
        # Группы светофоров создаются по конфигурации
        self.traffic_light_groups = self._create_traffic_light_groups(config.get("traffic_light_groups", []))
        
        # Инициализация данных о трафике (очереди, ожидания) – будут обновляться входящими данными
        self.traffic_data = {}
        self.queue_lengths = {}   # например: {"north_south": 10, "east_west": 5}
        self.waiting_times = {}   # например: {"north_south": 35, "east_west": 20}
        
        # Модель для прогнозирования изменений трафика (на основе конфигурации traffic_prediction)
        tp_config = config.get("traffic_prediction", {})
        self.prediction_model = TrafficPredictor(tp_config)
        
        # Инициализация алгоритма принятия решений – для демонстрации используем гибридный алгоритм
        aa_config = config.get("adaptive_algorithm", {})
        self.decision_algorithm = HybridController(aa_config, self.phases)
        
        self.learning_enabled = config.get("machine_learning", {}).get("enabled", False)
        self.state_history = []
        self.performance_history = []
        
        # Интервал принятия решения (например, каждые 5 секунд)
        self.decision_interval = aa_config.get("decision_interval", 5)
        self.last_decision_time = 0

    def _create_traffic_light_groups(self, grouping_data):
        """
        Создаёт словарь групп светофоров по конфигурационным данным.
        
        Аргументы:
          grouping_data (list): Список групп вида {"id": ..., "traffic_lights": [list of ids]}.
          
        Возвращает:
          dict: {group_id: список объектов светофоров}
        """
        groups = {}
        for group in grouping_data:
            group_id = group.get("id")
            tl_ids = group.get("traffic_lights", [])
            groups[group_id] = [tl for tl in self.traffic_lights if tl.id in tl_ids]
        return groups

    def update(self, time_step):
        """
        Обновляет состояние контроллера за указанный временной шаг.
        
        Аргументы:
          time_step (float): Временной шаг в секундах.
        """
        # Накапливаем время в текущей фазе
        self.time_in_current_phase += time_step

        # Периодически принимаем решение о смене фазы
        if self.time_in_current_phase >= self.decision_interval:
            # Получаем следующее решение: phase, оптимальная длительность
            next_phase, optimal_duration = self.decision_algorithm.decide(
                self.traffic_data,
                current_phase=self.current_phase,
                min_duration=self.min_phase_duration,
                max_duration=self.max_phase_duration,
                queue_lengths=self.queue_lengths,
                waiting_times=self.waiting_times
            )
            # Если принято решение о смене фазы – переключаемся
            if next_phase is not None and next_phase != self.current_phase:
                self.switch_to_phase(next_phase)
                # Обновляем границы длительности по новому phase
                phase_config = next((p for p in self.phases if p["id"] == next_phase), None)
                if phase_config:
                    self.min_phase_duration = phase_config.get("min_duration", self.min_phase_duration)
                    self.max_phase_duration = phase_config.get("max_duration", self.max_phase_duration)
            # Можно также обновлять длительность текущей фазы, если требуется
            self.last_decision_time = 0
            self.time_in_current_phase = 0.0

        # Записываем показатели эффективности за данный шаг
        cost = self.calculate_total_cost()
        self.performance_history.append(cost)
        # Добавляем текущий системный снимок для обучения (если включено)
        self.state_history.append({
            "time": time.time(),
            "current_phase": self.current_phase,
            "queue_lengths": self.queue_lengths,
            "waiting_times": self.waiting_times,
            "cost": cost
        })

    def update_traffic_data(self, data):
        """
        Обновляет информацию о текущем трафике.
        
        Аргументы:
          data (dict): Данные трафика, например {"queue_lengths": ..., "waiting_times": ...}
        """
        self.traffic_data = data
        self.queue_lengths = data.get("queue_lengths", self.queue_lengths)
        self.waiting_times = data.get("waiting_times", self.waiting_times)

    def decide_next_phase(self):
        """
        Выбирает следующую фазу на основе текущих данных.
        
        Возвращает:
          tuple: (next_phase, optimal_duration)
        """
        return self.decision_algorithm.decide(
            self.traffic_data,
            current_phase=self.current_phase,
            min_duration=self.min_phase_duration,
            max_duration=self.max_phase_duration,
            queue_lengths=self.queue_lengths,
            waiting_times=self.waiting_times
        )

    def decide_phase_duration(self):
        """
        Возвращает оптимальную длительность фазы на основе текущих данных.
        (Функция может быть объединена с decide_next_phase)
        
        Возвращает:
          float: Оптимальное время (сек).
        """
        _, optimal_duration = self.decision_algorithm.decide(
            self.traffic_data,
            current_phase=self.current_phase,
            min_duration=self.min_phase_duration,
            max_duration=self.max_phase_duration,
            queue_lengths=self.queue_lengths,
            waiting_times=self.waiting_times
        )
        return optimal_duration

    def switch_to_phase(self, phase_id):
        """
        Переключает систему на выбранную фазу.
        
        Аргументы:
          phase_id: Идентификатор фазы для переключения.
        """
        self.current_phase = phase_id
        # Обновляем состояния светофоров для групп согласно конфигурации фазы
        phase_config = next((p for p in self.phases if p["id"] == phase_id), None)
        if phase_config:
            groups_states = phase_config.get("groups_states", {})
            for group_id, state in groups_states.items():
                group = self.traffic_light_groups.get(group_id, [])
                for tl in group:
                    tl.state = state

    def calculate_phase_priority(self, phase):
        """
        Расчитывает приоритет заданной фазы на основе текущих данных.
        Для примера используется stub-реализация.
        
        Аргументы:
          phase: Конфигурация фазы.
          
        Возвращает:
          float: Приоритет (чем меньше – тем выгоднее).
        """
        # stub: можно использовать, например, сумму длин очередей
        priority = sum(self.queue_lengths.values()) if self.queue_lengths else 0
        return priority

    def predict_flow_changes(self, horizon=300):
        """
        Выполняет прогнозирование изменений в транспортном потоке.
        
        Аргументы:
          horizon (int): Горизонт прогнозирования в секундах.
          
        Возвращает:
          dict: Прогнозные данные (stub-реализация).
        """
        return self.prediction_model.predict_flow(self.traffic_data, horizon)

    def optimize_phase_sequence(self):
        """
        Оптимизирует последовательность фаз (stub).
        """
        pass

    def calculate_waiting_time_cost(self):
        """
        Расчитывает "стоимость" времени ожидания – чем больше время, тем выше затраты.
        
        Возвращает:
          float: Стоимость.
        """
        if self.waiting_times:
            return sum(self.waiting_times.values()) / len(self.waiting_times)
        return 0.0

    def calculate_queue_length_cost(self):
        """
        Расчитывает "стоимость" длины очередей – чем длиннее очередь, тем больше затрат.
        
        Возвращает:
          float: Стоимость.
        """
        if self.queue_lengths:
            return sum(self.queue_lengths.values()) / len(self.queue_lengths)
        return 0.0

    def calculate_total_cost(self):
        """
        Рассчитывает общую "стоимость" текущего состояния (комбинация затрат ожидания и очередей).
        
        Возвращает:
          float: Общая стоимость.
        """
        waiting_cost = self.calculate_waiting_time_cost()
        queue_cost = self.calculate_queue_length_cost()
        return waiting_cost + queue_cost

    def learn_from_history(self):
        """
        Обучается на основе накопленных данных (stub-реализация).
        """
        if self.learning_enabled:
            # Здесь можно обновлять параметры модели или алгоритма
            pass

    def save_model(self, filename):
        """
        Сохраняет обученную модель.
        
        Аргументы:
          filename (str): Путь для сохранения модели.
        """
        self.decision_algorithm.save_model(filename)

    def load_model(self, filename):
        """
        Загружает модель из файла.
        
        Аргументы:
          filename (str): Путь к сохранённой модели.
        """
        self.decision_algorithm.load_model(filename)

    def reset(self):
        """
        Сбрасывает контроллер в начальное состояние.
        """
        self.current_phase = self.phases[0]["id"] if self.phases else None
        self.time_in_current_phase = 0.0
        self.state_history = []
        self.performance_history = []

    def get_traffic_light_states(self):
        """
        Реализация абстрактного метода BaseController: возвращает текущие состояния светофоров.
        
        Возвращает:
          dict: {id светофора: состояние}
        """
        return {tl.id: tl.state for tl in self.traffic_lights}

    def __str__(self):
        return f"SmartController(phase={self.current_phase}, time_in_phase={self.time_in_current_phase:.1f})"


def main():
    """
    Функция демонстрации работы умного адаптивного контроллера.
    
    Выполняются следующие шаги:
      1. Создание dummy-объектов светофоров для перекрёстка.
      2. Загрузка конфигурации адаптивного контроллера (из файла YAML или из примера).
      3. Инициализация SmartController.
      4. Генерация реалистичных данных о транспортном потоке (имитируются случайные значения очередей и ожиданий).
      5. Симуляция работы контроллера в течение нескольких циклов.
      6. Вывод метрик эффективности, истории состояний и сравнение с традиционным контроллером (здесь – условно).
    """
    # Для демонстрации определим простой класс DummyTrafficLight
    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state
        def __str__(self):
            return f"{self.id}: {self.state}"

    # Создаем список dummy-светофоров
    dummy_lights = [
        DummyTrafficLight("north_1"),
        DummyTrafficLight("south_1"),
        DummyTrafficLight("east_1"),
        DummyTrafficLight("west_1"),
        DummyTrafficLight("north_left"),
        DummyTrafficLight("south_left"),
        DummyTrafficLight("east_left"),
        DummyTrafficLight("west_left")
    ]

    # Пытаемся загрузить конфигурацию из файла, если он есть, иначе используем пример
    config_path = os.path.join("configs", "smart_controller.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
    else:
        # Пример конфигурации (схож с приведённым в условии)
        config = {
            "intersection_id": "main_intersection",
            "controller_type": "adaptive",
            "traffic_light_groups": [
                {"id": "group_north_south", "traffic_lights": ["north_1", "south_1"]},
                {"id": "group_east_west", "traffic_lights": ["east_1", "west_1"]},
                {"id": "group_north_south_left", "traffic_lights": ["north_left", "south_left"]},
                {"id": "group_east_west_left", "traffic_lights": ["east_left", "west_left"]}
            ],
            "phases": [
                {
                    "id": 1,
                    "name": "North-South Movement",
                    "min_duration": 20,
                    "max_duration": 60,
                    "groups_states": {
                        "group_north_south": "GREEN",
                        "group_east_west": "RED",
                        "group_north_south_left": "RED",
                        "group_east_west_left": "RED"
                    }
                },
                {
                    "id": 2,
                    "name": "North-South Left Turn",
                    "min_duration": 10,
                    "max_duration": 30,
                    "groups_states": {
                        "group_north_south": "RED",
                        "group_east_west": "RED",
                        "group_north_south_left": "GREEN",
                        "group_east_west_left": "RED"
                    }
                },
                {
                    "id": 3,
                    "name": "East-West Movement",
                    "min_duration": 20,
                    "max_duration": 60,
                    "groups_states": {
                        "group_north_south": "RED",
                        "group_east_west": "GREEN",
                        "group_north_south_left": "RED",
                        "group_east_west_left": "RED"
                    }
                },
                {
                    "id": 4,
                    "name": "East-West Left Turn",
                    "min_duration": 10,
                    "max_duration": 30,
                    "groups_states": {
                        "group_north_south": "RED",
                        "group_east_west": "RED",
                        "group_north_south_left": "RED",
                        "group_east_west_left": "GREEN"
                    }
                }
            ],
            "adaptive_algorithm": {
                "type": "hybrid",
                "decision_interval": 5,
                "webster": {
                    "saturation_flow_rate": 1800,
                    "lost_time_per_phase": 4,
                    "critical_volume_threshold": 0.9
                },
                "queue_length": {
                    "weight": 0.7,
                    "threshold_short": 5,
                    "threshold_medium": 15,
                    "threshold_long": 30
                },
                "waiting_time": {
                    "weight": 0.3,
                    "threshold_short": 30,
                    "threshold_medium": 60,
                    "threshold_long": 120
                },
                "reinforcement_learning": {
                    "algorithm": "q_learning",
                    "learning_rate": 0.1,
                    "discount_factor": 0.9,
                    "exploration_rate": 0.1,
                    "model_path": "models/rl_model.pkl"
                }
            },
            "traffic_prediction": {
                "enabled": True,
                "method": "regression",
                "horizon": 300,
                "update_interval": 60,
                "model_path": "models/traffic_predictor.pkl"
            },
            "safety_constraints": {
                "min_green_time": 10,
                "min_red_time": 15,
                "yellow_time": 3,
                "all_red_time": 2,
                "max_cycle_time": 180
            },
            "machine_learning": {
                "enabled": True,
                "training_interval": 86400,
                "min_samples_for_training": 1000,
                "feature_selection": ["queue_length", "waiting_time", "traffic_flow", "time_of_day", "day_of_week"],
                "validation_split": 0.2
            }
        }

    # Инициализируем логирование
    logger = logging.getLogger("SmartControllerDemo")
    logging.basicConfig(level=logging.INFO)

    # Инициализируем умный контроллер
    smart_ctrl = SmartController(dummy_lights, config)
    print("Начальное состояние умного контроллера:")
    print(smart_ctrl)
    print("Начальные состояния светофоров:", smart_ctrl.get_traffic_light_states())

    # Симуляция работы: будем менять данные о трафике и обновлять контроллер в течение нескольких циклов.
    simulation_duration = 60   # симулируем 60 сек.
    time_step = 1              # шаг 1 секунда
    for t in range(simulation_duration):
        # Генерируем фиктивные данные трафика (например, очереди и время ожидания по направлениям)
        traffic_data = {
            "queue_lengths": {
                "north_south": random.randint(0, 20),
                "east_west": random.randint(0, 20)
            },
            "waiting_times": {
                "north_south": random.randint(10, 80),
                "east_west": random.randint(10, 80)
            }
        }
        smart_ctrl.update_traffic_data(traffic_data)
        smart_ctrl.update(time_step)
        if t % 5 == 0:
            logger.info(f"Время {t} сек. Текущая фаза: {smart_ctrl.current_phase} | "
                        f"Состояния светофоров: {smart_ctrl.get_traffic_light_states()}")
        time.sleep(0.05)  # небольшая задержка для демонстрации

    # Вывод ключевых метрик эффективности
    total_cost = smart_ctrl.calculate_total_cost()
    avg_performance = sum(smart_ctrl.performance_history) / len(smart_ctrl.performance_history) if smart_ctrl.performance_history else 0
    print("Симуляция завершена.")
    print("Итоговая общая стоимость (cost):", total_cost)
    print("Средняя стоимость по шагам:", avg_performance)
    
    # Для сравнения можно создать традиционный контроллер и запустить его на тех же данных.
    # Здесь для демонстрации выведем только сообщение.
    print("Сравнение с традиционным контроллером (демонстрация): традиционный контроллер показал средние метрики, равные 50 (условно).")

if __name__ == '__main__':
    main()
