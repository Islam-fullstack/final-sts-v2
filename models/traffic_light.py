"""
Файл: models/traffic_light.py

Описание:
  Реализованы модели светофоров:
    • Класс TrafficLight – моделирует одиночный светофор с атрибутами: id, position, current_state, time_in_state, states_sequence, durations.
      Методы для переключения состояний, обновления состояния и проверки разрешения проезда.
    • Класс TrafficLightGroup – управляет группой синхронизированных светофоров с матрицей фаз и текущей фазой.

Для автономного тестирования реализована функция main().
"""


class TrafficLight:
    """
    Класс для моделирования светофора.

    Атрибуты:
      id (str): Идентификатор светофора.
      position (tuple): Позиция на дороге (x, y).
      current_state (str): Текущее состояние ("red", "yellow", "green").
      time_in_state (float): Время, проведённое в текущем состоянии.
      states_sequence (list): Последовательность состояний.
      durations (dict): Длительность каждого состояния, сек.
    """
    def __init__(self, id, position, states_sequence=("red", "green", "yellow"), durations=None):
        self.id = id
        self.position = position
        self.states_sequence = list(states_sequence)
        self.durations = durations if durations is not None else {"red": 30, "green": 30, "yellow": 5}
        self.current_state = self.states_sequence[0]
        self.time_in_state = 0.0
        self.current_index = 0

    def update_state(self, dt):
        """
        Обновляет состояние светофора с учётом прошедшего времени dt.

        Аргументы:
          dt (float): Временной интервал, сек.
        """
        self.time_in_state += dt
        if self.time_in_state >= self.durations[self.current_state]:
            self.switch_state()

    def switch_state(self):
        """Переключает состояние согласно заданной последовательности."""
        self.current_index = (self.current_index + 1) % len(self.states_sequence)
        self.current_state = self.states_sequence[self.current_index]
        self.time_in_state = 0.0

    def is_passage_allowed(self):
        """
        Проверяет, разрешён ли проезд.

        Возвращает:
          bool: True если состояние "green", иначе False.
        """
        return self.current_state.lower() == "green"

    def __str__(self):
        return f"TrafficLight(id={self.id}, state={self.current_state}, time={self.time_in_state:.1f})"


class TrafficLightGroup:
    """
    Класс для группы синхронизированных светофоров.

    Атрибуты:
      id (str): Идентификатор группы.
      traffic_lights (list): Список объектов TrafficLight.
      phase_matrix (list): Матрица фаз работы (каждая фаза – список состояний для светофоров).
      current_phase (int): Текущая фаза.
    """
    def __init__(self, id, traffic_lights, phase_matrix, current_phase=0):
        self.id = id
        self.traffic_lights = traffic_lights
        self.phase_matrix = phase_matrix
        self.current_phase = current_phase

    def update_group(self, dt):
        """
        Обновляет состояние каждого светофора группы.
        
        Аргументы:
          dt (float): Временной интервал, сек.
        """
        for light in self.traffic_lights:
            light.update_state(dt)
        # Пример синхронизации: при полном переключении (time_in_state == 0) переходим к новой фазе
        if all(light.time_in_state == 0.0 for light in self.traffic_lights):
            self.current_phase = (self.current_phase + 1) % len(self.phase_matrix)
            phase_states = self.phase_matrix[self.current_phase]
            for light, state in zip(self.traffic_lights, phase_states):
                light.current_state = state
                light.time_in_state = 0.0

    def __str__(self):
        lights_str = "\n".join(str(light) for light in self.traffic_lights)
        return f"TrafficLightGroup(id={self.id}, phase={self.current_phase})\n{lights_str}"


def main():
    """
    Демонстрация работы классов TrafficLight и TrafficLightGroup.
    Создаются светофоры, выполняется их обновление, выводится состояние и синхронизация группы.
    """
    import time

    # Создаем два светофора
    light1 = TrafficLight(id="TL1", position=(0, 0))
    light2 = TrafficLight(id="TL2", position=(100, 0))
    lights = [light1, light2]

    # Определяем матрицу фаз: каждая фаза – список состояний для каждого светофора
    phase_matrix = [
        ["red", "red"],
        ["green", "green"],
        ["yellow", "yellow"]
    ]
    group = TrafficLightGroup(id="Group1", traffic_lights=lights, phase_matrix=phase_matrix)

    dt = 1.0
    for t in range(40):
        group.update_group(dt)
        print(group)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
