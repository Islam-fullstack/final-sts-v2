#!/usr/bin/env python
"""
Файл: controllers/smart_controller.py

Класс SmartController для адаптивного управления светофорами с учетом плотности потока.
"""

import time
import random
from .base_controller import BaseController
from .adaptive_algorithm import HybridController
from .traffic_predictor import TrafficPredictor

class SmartController(BaseController):
    def __init__(self, traffic_lights, config):
        """
        Инициализирует умный контроллер.
        """
        super().__init__(traffic_lights, config)
        self.config = config
        self.phases = config.get("phases", [])
        self.current_phase = self.phases[0]["id"] if self.phases else None
        self.time_in_current_phase = 0.0
        self.min_phase_duration = self.phases[0].get("min_duration", 20) if self.phases else 20
        self.max_phase_duration = self.phases[0].get("max_duration", 60) if self.phases else 60
        
        grouping_data = config.get("traffic_light_groups", [])
        self.traffic_light_groups = self._create_traffic_light_groups(grouping_data)
        
        self.traffic_data = {}
        self.queue_lengths = {}   # Например: {"north_south": 10, "east_west": 5}
        self.waiting_times = {}   # Например: {"north_south": 35, "east_west": 20}
        
        tp_config = config.get("traffic_prediction", {})
        self.prediction_model = TrafficPredictor(tp_config)
        
        aa_config = config.get("adaptive_algorithm", {})
        self.decision_algorithm = HybridController(aa_config, self.phases)
        
        self.learning_enabled = config.get("machine_learning", {}).get("enabled", False)
        self.state_history = []
        self.performance_history = []
        self.decision_interval = aa_config.get("decision_interval", 5)

    def _create_traffic_light_groups(self, grouping_data):
        groups = {}
        for group in grouping_data:
            group_id = group.get("id")
            tl_ids = group.get("traffic_lights", [])
            groups[group_id] = [tl for tl in self.traffic_lights if tl.id in tl_ids]
        return groups

    def update(self, time_step):
        self.time_in_current_phase += time_step
        if self.time_in_current_phase >= self.decision_interval:
            next_phase, optimal_duration = self.decision_algorithm.decide(
                self.traffic_data,
                current_phase=self.current_phase,
                min_duration=self.min_phase_duration,
                max_duration=self.max_phase_duration,
                queue_lengths=self.queue_lengths,
                waiting_times=self.waiting_times
            )
            if next_phase is not None and next_phase != self.current_phase:
                self.switch_to_phase(next_phase)
                phase_config = next((p for p in self.phases if p["id"] == next_phase), None)
                if phase_config:
                    self.min_phase_duration = phase_config.get("min_duration", self.min_phase_duration)
                    self.max_phase_duration = phase_config.get("max_duration", self.max_phase_duration)
            self.time_in_current_phase = 0.0

        cost = self.calculate_total_cost()
        self.performance_history.append(cost)
        self.state_history.append({
            "time": time.time(),
            "current_phase": self.current_phase,
            "queue_lengths": self.queue_lengths,
            "waiting_times": self.waiting_times,
            "cost": cost
        })

    def update_traffic_data(self, data):
        self.traffic_data = data
        self.queue_lengths = data.get("queue_lengths", self.queue_lengths)
        self.waiting_times = data.get("waiting_times", self.waiting_times)

    def decide_next_phase(self):
        return self.decision_algorithm.decide(
            self.traffic_data,
            current_phase=self.current_phase,
            min_duration=self.min_phase_duration,
            max_duration=self.max_phase_duration,
            queue_lengths=self.queue_lengths,
            waiting_times=self.waiting_times
        )

    def decide_phase_duration(self):
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
        self.current_phase = phase_id
        phase_config = next((p for p in self.phases if p["id"] == phase_id), None)
        if phase_config:
            groups_states = phase_config.get("groups_states", {})
            for group_id, state in groups_states.items():
                for tl in self.traffic_light_groups.get(group_id, []):
                    tl.state = state

    def calculate_phase_priority(self, phase):
        priority = sum(self.queue_lengths.values()) if self.queue_lengths else 0
        return priority

    def predict_flow_changes(self, horizon=300):
        return self.prediction_model.predict_flow(self.traffic_data, horizon)

    def optimize_phase_sequence(self):
        pass

    def calculate_waiting_time_cost(self):
        if self.waiting_times:
            return sum(self.waiting_times.values()) / len(self.waiting_times)
        return 0.0

    def calculate_queue_length_cost(self):
        if self.queue_lengths:
            return sum(self.queue_lengths.values()) / len(self.queue_lengths)
        return 0.0

    def calculate_total_cost(self):
        return self.calculate_waiting_time_cost() + self.calculate_queue_length_cost()

    def learn_from_history(self):
        if self.learning_enabled:
            pass

    def save_model(self, filename):
        self.decision_algorithm.save_model(filename)

    def load_model(self, filename):
        self.decision_algorithm.load_model(filename)

    def reset(self):
        self.current_phase = self.phases[0]["id"] if self.phases else None
        self.time_in_current_phase = 0.0
        self.state_history = []
        self.performance_history = []

    def get_traffic_light_states(self):
        return {tl.id: tl.state for tl in self.traffic_lights}

    def __str__(self):
        return f"SmartController(phase={self.current_phase}, time_in_phase={self.time_in_current_phase:.1f})"

if __name__ == "__main__":
    # Тестовая демонстрация smart контроллера
    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state
    lights = [DummyTrafficLight("north_1"), DummyTrafficLight("south_1"),
              DummyTrafficLight("east_1"), DummyTrafficLight("west_1"),
              DummyTrafficLight("north_left"), DummyTrafficLight("south_left"),
              DummyTrafficLight("east_left"), DummyTrafficLight("west_left")]
    config = {
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
        "traffic_light_groups": [
            {"id": "group_north_south", "traffic_lights": ["north_1", "south_1"]},
            {"id": "group_east_west", "traffic_lights": ["east_1", "west_1"]},
            {"id": "group_north_south_left", "traffic_lights": ["north_left", "south_left"]},
            {"id": "group_east_west_left", "traffic_lights": ["east_left", "west_left"]}
        ],
        "adaptive_algorithm": {
            "decision_interval": 5,
            "queue_length": {"weight": 0.7, "threshold_short": 5, "threshold_medium": 15, "threshold_long": 30},
            "waiting_time": {"weight": 0.3, "threshold_short": 30, "threshold_medium": 60, "threshold_long": 120}
        },
        "traffic_prediction": {"horizon": 300, "update_interval": 60, "model_path": "models/traffic_predictor.pkl"},
        "machine_learning": {"enabled": True}
    }
    ctrl = SmartController(lights, config)
    print("Начальное состояние:", ctrl.get_traffic_light_states())
    ctrl.update(5)
    print("После обновления:", ctrl.get_traffic_light_states())
