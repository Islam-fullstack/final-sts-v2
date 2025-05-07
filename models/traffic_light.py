#!/usr/bin/env python
"""
Файл: models/traffic_light.py

Реализует модели светофоров:
  - TrafficLight: отдельный светофор.
  - TrafficLightGroup: группа синхронизированных светофоров.
"""

class TrafficLight:
    def __init__(self, id, position, states_sequence=("red", "green", "yellow"), durations=None):
        self.id = id
        self.position = position
        self.states_sequence = list(states_sequence)
        self.durations = durations if durations is not None else {"red": 30, "green": 30, "yellow": 5}
        self.current_state = self.states_sequence[0] if self.states_sequence else None
        self.time_in_state = 0.0
        self.current_index = 0

    def update_state(self, dt):
        self.time_in_state += dt
        if self.time_in_state >= self.durations[self.current_state]:
            self.switch_state()

    def switch_state(self):
        self.current_index = (self.current_index + 1) % len(self.states_sequence)
        self.current_state = self.states_sequence[self.current_index]
        self.time_in_state = 0.0

    def is_passage_allowed(self):
        return self.current_state.lower() == "green"

    def __str__(self):
        return f"TrafficLight({self.id}, state={self.current_state}, time_in_state={self.time_in_state:.1f})"

class TrafficLightGroup:
    def __init__(self, id, traffic_lights, phase_matrix, current_phase=0):
        self.id = id
        self.traffic_lights = traffic_lights  # список объектов TrafficLight
        self.phase_matrix = phase_matrix  # список фаз (каждая фаза – словарь {traffic_light_id: state})
        self.current_phase = current_phase

    def update_group(self, dt):
        for light in self.traffic_lights:
            light.update_state(dt)
        # Если все светофоры перешли в новое состояние (time_in_state == 0), переключаем фазу
        if all(light.time_in_state == 0.0 for light in self.traffic_lights):
            self.current_phase = (self.current_phase + 1) % len(self.phase_matrix)
            phase_states = self.phase_matrix[self.current_phase]
            for light in self.traffic_lights:
                if light.id in phase_states:
                    light.current_state = phase_states[light.id]
                    light.time_in_state = 0.0

    def __str__(self):
        lights_str = "\n".join(str(light) for light in self.traffic_lights)
        return f"TrafficLightGroup({self.id}, current_phase={self.current_phase})\n{lights_str}"

if __name__ == "__main__":
    light1 = TrafficLight("TL1", (0, 0))
    light2 = TrafficLight("TL2", (100, 0))
    phase_matrix = [
        {"TL1": "red", "TL2": "red"},
        {"TL1": "green", "TL2": "green"},
        {"TL1": "yellow", "TL2": "yellow"}
    ]
    group = TrafficLightGroup("Group1", [light1, light2], phase_matrix)
    dt = 1.0
    for t in range(40):
        group.update_group(dt)
        print(group)
