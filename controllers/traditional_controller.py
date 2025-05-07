#!/usr/bin/env python
"""
Файл: controllers/traditional_controller.py

Традиционный контроллер с фиксированными фазами.
Реализует переключение фаз согласно конфигурации цикла.
"""

from .base_controller import BaseController

class TraditionalController(BaseController):
    def __init__(self, traffic_lights, config):
        super().__init__(traffic_lights, config)
        self.cycle_time = config.get("cycle_time", 120)
        self.offset = config.get("offset", 0)
        self.fixed_timing = True
        self.emergency_mode = config.get("emergency", {}).get("enabled", False)
        self.phase_history = []
        self.phase_settings = config.get("phases", [])
        self.phase_durations = [phase.get("duration", 30) for phase in self.phase_settings]
        self.current_phase = self.phase_settings[0]["id"] if self.phase_settings else None
        self.time_in_current_phase = 0.0
        
        grouping_data = config.get("traffic_light_groups", [])
        self.traffic_light_groups = self.create_traffic_light_groups(grouping_data)
        self.timing_plans = config.get("timing_plans", [])
        self.synchronization_settings = config.get("synchronization", {})
        self.emergency_settings = config.get("emergency", {})

    def update(self, time_step):
        self.time_in_current_phase += time_step
        current_duration = self.phase_durations[self.current_phase - 1] if self.current_phase else 30
        if self.time_in_current_phase >= current_duration:
            self.switch_to_next_phase()
        # Дополнительно можно реализовать более сложную логику обновления

    def switch_to_next_phase(self):
        self.phase_history.append(self.current_phase)
        idx = next((i for i, phase in enumerate(self.phase_settings) if phase["id"] == self.current_phase), 0)
        next_idx = (idx + 1) % len(self.phase_settings)
        self.current_phase = self.phase_settings[next_idx]["id"]
        self.time_in_current_phase = 0.0
        self.apply_phase(self.phase_settings[next_idx])

    def switch_to_phase(self, phase_id):
        for phase in self.phase_settings:
            if phase.get("id") == phase_id:
                self.phase_history.append(self.current_phase)
                self.current_phase = phase_id
                self.time_in_current_phase = 0.0
                self.apply_phase(phase)
                return
        print(f"Фаза c id {phase_id} не найдена.")

    def apply_phase(self, phase_config):
        groups_states = phase_config.get("groups_states", {})
        for group_id, state in groups_states.items():
            for tl in self.traffic_light_groups.get(group_id, []):
                tl.state = state

    def get_traffic_light_states(self):
        return {tl.id: tl.state for tl in self.traffic_lights}

    def setup_phase_timing(self, timing_data):
        if len(timing_data) != len(self.phase_durations):
            print("Ошибка: число интервалов не соответствует числу фаз")
            return
        self.phase_durations = timing_data

    def create_traffic_light_groups(self, grouping_data):
        groups = {}
        for group in grouping_data:
            group_id = group.get("id")
            tl_ids = group.get("traffic_lights", [])
            groups[group_id] = [tl for tl in self.traffic_lights if tl.id in tl_ids]
        return groups

    def adjust_timing_for_time_of_day(self, time_of_day):
        for plan in self.timing_plans:
            if time_of_day in plan.get("time_range", []):
                self.setup_phase_timing(plan.get("phase_durations", self.phase_durations))
                return
        for plan in self.timing_plans:
            if "default" in plan.get("time_range", []):
                self.setup_phase_timing(plan.get("phase_durations", self.phase_durations))
                return

    def enable_emergency_mode(self):
        self.emergency_mode = True
        for group in self.traffic_light_groups.values():
            for tl in group:
                if "north_south" in tl.id.lower():
                    tl.state = "GREEN"
                else:
                    tl.state = "RED"

    def disable_emergency_mode(self):
        self.emergency_mode = False

    def calculate_performance_metrics(self):
        return {
            "average_phase_duration": sum(self.phase_durations) / len(self.phase_durations),
            "total_phase_switches": len(self.phase_history)
        }

    def save_configuration(self, filename):
        import yaml
        with open(filename, 'w') as file:
            yaml.dump(self.config, file)

    def load_configuration(self, filename):
        import yaml
        with open(filename, 'r') as file:
            self.config = yaml.safe_load(file)
        self.__init__(self.traffic_lights, self.config)

    def reset(self):
        self.current_phase = self.phase_settings[0]["id"] if self.phase_settings else None
        self.time_in_current_phase = 0.0
        self.phase_history = {}

if __name__ == "__main__":
    # Тестовая демонстрация традиционного контроллера
    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state
    lights = [DummyTrafficLight("north_1"), DummyTrafficLight("south_1"),
              DummyTrafficLight("east_1"), DummyTrafficLight("west_1"),
              DummyTrafficLight("north_left"), DummyTrafficLight("south_left"),
              DummyTrafficLight("east_left"), DummyTrafficLight("west_left")]
    config = {
        "cycle_time": 120,
        "offset": 0,
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
                "duration": 40,
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
                "duration": 20,
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
                "duration": 40,
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
                "duration": 20,
                "groups_states": {
                    "group_north_south": "RED",
                    "group_east_west": "RED",
                    "group_north_south_left": "RED",
                    "group_east_west_left": "GREEN"
                }
            }
        ],
        "timing_plans": [],
        "synchronization": {},
        "emergency": {}
    }
    ctrl = TraditionalController(lights, config)
    print("Начальное состояние:", ctrl.get_traffic_light_states())
    ctrl.update(10)
    print("После обновления:", ctrl.get_traffic_light_states())
