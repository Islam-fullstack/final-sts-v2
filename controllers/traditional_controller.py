"""
Файл: controllers/traditional_controller.py

Описание:
  Класс TraditionalController реализует традиционный контроллер с фиксированными
  фазами. Контроллер управляет группами светофоров, переключает фазы согласно
  предопределённому расписанию и поддерживает изменение настроек времени в зависимости 
  от времени суток, а также режим чрезвычайной ситуации.

  Основные атрибуты:
    - traffic_light_groups: группы синхронизированных светофоров (dict: group_id → [светофоры]).
    - phase_durations: список длительностей фаз.
    - current_phase: индекс текущей активной фазы.
    - time_in_current_phase: время, проведённое в текущей фазе.
    - cycle_time: общее время цикла.
    - offset: смещение начала цикла.
    - fixed_timing: флаг фиксированных временных интервалов.
    - emergency_mode: флаг режима ЧС.
    - phase_history: история переключений фаз.

  Реализованы методы:
    - __init__(traffic_lights, config)
    - update(time_step)
    - switch_to_next_phase()
    - switch_to_phase(phase_id)
    - get_traffic_light_states()
    - setup_phase_timing(timing_data)
    - create_traffic_light_groups(grouping_data)
    - adjust_timing_for_time_of_day(time_of_day)
    - enable_emergency_mode() / disable_emergency_mode()
    - calculate_performance_metrics()
    - save_configuration(filename) / load_configuration(filename)
    - reset()
"""

from controllers.base_controller import BaseController
import yaml
import logging


class TraditionalController(BaseController):
    def __init__(self, traffic_lights, config):
        """
        Инициализация контроллера на основе конфигурации.
        
        Аргументы:
          traffic_lights (list): Список объектов светофоров.
          config (dict): Конфигурация контроллера.
        """
        super().__init__(traffic_lights, config)
        self.cycle_time = config.get("cycle_time", 120)
        self.offset = config.get("offset", 0)
        self.fixed_timing = True
        self.emergency_mode = config.get("emergency", {}).get("enabled", False)
        self.phase_history = []

        self.phase_settings = config.get("phases", [])
        self.phase_durations = [phase.get("duration", 30) for phase in self.phase_settings]
        self.current_phase = 0
        self.time_in_current_phase = 0.0

        grouping_data = config.get("traffic_light_groups", [])
        self.traffic_light_groups = self.create_traffic_light_groups(grouping_data)

        self.timing_plans = config.get("timing_plans", [])
        self.synchronization_settings = config.get("synchronization", {})
        self.emergency_settings = config.get("emergency", {})

    def update(self, time_step):
        """
        Обновляет состояние контроллера за временной шаг.
        
        Аргументы:
          time_step (float): Интервал времени в секундах.
        """
        self.time_in_current_phase += time_step
        current_phase_duration = self.phase_durations[self.current_phase]
        if self.time_in_current_phase >= current_phase_duration:
            self.switch_to_next_phase()
        self.apply_phase(self.phase_settings[self.current_phase])

    def switch_to_next_phase(self):
        """
        Переключает контроллер на следующую фазу.
        """
        self.phase_history.append(self.current_phase)
        self.current_phase = (self.current_phase + 1) % len(self.phase_settings)
        self.time_in_current_phase = 0.0
        self.apply_phase(self.phase_settings[self.current_phase])

    def switch_to_phase(self, phase_id):
        """
        Переключает контроллер на указанную фазу по id.
        
        Аргументы:
          phase_id (int): Идентификатор фазы.
        """
        for index, phase in enumerate(self.phase_settings):
            if phase.get("id") == phase_id:
                self.phase_history.append(self.current_phase)
                self.current_phase = index
                self.time_in_current_phase = 0.0
                self.apply_phase(phase)
                return
        print(f"Фаза с id {phase_id} не найдена.")

    def apply_phase(self, phase_config):
        """
        Применяет настройки фазы ко всем группам светофоров.
        
        Аргументы:
          phase_config (dict): Конфигурация фазы (должна содержать ключ groups_states).
        """
        groups_states = phase_config.get("groups_states", {})
        for group_id, state in groups_states.items():
            group = self.traffic_light_groups.get(group_id, [])
            for tl in group:
                tl.state = state

    def get_traffic_light_states(self):
        """
        Возвращает состояния всех светофоров.
        
        Возвращает:
          dict: {id светофора: состояние}
        """
        return {tl.id: tl.state for tl in self.traffic_lights}

    def setup_phase_timing(self, timing_data):
        """
        Настраивает длительности фаз.
        
        Аргументы:
          timing_data (list): Список длительностей фаз.
        """
        if len(timing_data) != len(self.phase_durations):
            print("Ошибка: число интервалов не соответствует числу фаз")
            return
        self.phase_durations = timing_data

    def create_traffic_light_groups(self, grouping_data):
        """
        Создает группы светофоров на основе конфигурационных данных.
        
        Аргументы:
          grouping_data (list): Список групп с id и перечнем светофоров.
        
        Возвращает:
          dict: {group_id: список объектов светофоров}
        """
        groups = {}
        for group in grouping_data:
            group_id = group.get("id")
            tl_ids = group.get("traffic_lights", [])
            groups[group_id] = [tl for tl in self.traffic_lights if tl.id in tl_ids]
        return groups

    def adjust_timing_for_time_of_day(self, time_of_day):
        """
        Корректирует длительности фаз в зависимости от времени суток.
        
        Аргументы:
          time_of_day (str): Например, "Morning Peak", "Evening Peak", "Night".
        """
        for plan in self.timing_plans:
            if time_of_day in plan.get("time_range", []):
                self.setup_phase_timing(plan.get("phase_durations", self.phase_durations))
                return
        for plan in self.timing_plans:
            if "default" in plan.get("time_range", []):
                self.setup_phase_timing(plan.get("phase_durations", self.phase_durations))
                return

    def enable_emergency_mode(self):
        """
        Включает режим чрезвычайной ситуации.
        """
        self.emergency_mode = True
        for group in self.traffic_light_groups.values():
            for tl in group:
                tl.state = "GREEN" if self.emergency_settings.get("priority_direction", "").lower() in tl.id.lower() else "RED"

    def disable_emergency_mode(self):
        """
        Отключает режим чрезвычайной ситуации.
        """
        self.emergency_mode = False

    def calculate_performance_metrics(self):
        """
        Рассчитывает показатели эффективности работы контроллера.
        
        Возвращает:
          dict: Пример показателей (средняя длительность фазы, число переключений).
        """
        return {
            "average_phase_duration": sum(self.phase_durations) / len(self.phase_durations),
            "total_phase_switches": len(self.phase_history)
        }

    def save_configuration(self, filename):
        """
        Сохраняет конфигурацию контроллера в YAML файл.
        
        Аргументы:
          filename (str): Путь к файлу.
        """
        with open(filename, 'w') as file:
            yaml.dump(self.config, file)

    def load_configuration(self, filename):
        """
        Загружает конфигурацию контроллера из YAML файла и пересоздаёт внутреннее состояние.
        
        Аргументы:
          filename (str): Путь к YAML файлу.
        """
        with open(filename, 'r') as file:
            self.config = yaml.safe_load(file)
        self.__init__(self.traffic_lights, self.config)

    def reset(self):
        """
        Сбрасывает контроллер: устанавливает начальную фазу, обнуляет время и историю переключений.
        """
        self.current_phase = 0
        self.time_in_current_phase = 0.0
        self.phase_history = []


def main():
    """
    Демонстрация работы TraditionalController.
    Создаются фейковые объекты светофоров и пример конфигурации,
    выполняется несколько обновлений и выводятся показатели эффективности.
    """
    import time

    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state

        def __str__(self):
            return f"{self.id}: {self.state}"

    traffic_lights = [
        DummyTrafficLight("north_1"), DummyTrafficLight("south_1"),
        DummyTrafficLight("east_1"), DummyTrafficLight("west_1"),
        DummyTrafficLight("north_left"), DummyTrafficLight("south_left"),
        DummyTrafficLight("east_left"), DummyTrafficLight("west_left")
    ]

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
        "timing_plans": [
            {"name": "Morning Peak", "time_range": ["06:00", "09:00"], "phase_durations": [30, 20, 50, 20]},
            {"name": "Evening Peak", "time_range": ["16:00", "19:00"], "phase_durations": [30, 20, 50, 20]},
            {"name": "Night", "time_range": ["22:00", "05:00"], "phase_durations": [25, 15, 25, 15]},
            {"name": "Default", "time_range": ["default"], "phase_durations": [40, 20, 40, 20]}
        ],
        "synchronization": {
            "enabled": False,
            "master_intersection": "main_intersection",
            "affected_intersections": ["second_intersection", "third_intersection"],
            "offset_seconds": [0, 15, 30]
        },
        "emergency": {
            "enabled": False,
            "priority_direction": "north_south",
            "min_green_time": 10,
            "max_red_time": 60
        }
    }

    controller = TraditionalController(traffic_lights, config)
    logger = logging.getLogger("TraditionalControllerTest")
    logging.basicConfig(level=logging.INFO)

    print("Начальное состояние светофоров:")
    print(controller.get_traffic_light_states())
    
    for i in range(5):
        controller.update(10)
        print(f"Состояние после {10*(i+1)} секунд:")
        print(controller.get_traffic_light_states())
        time.sleep(0.5)
    
    metrics = controller.calculate_performance_metrics()
    print("Показатели эффективности:", metrics)

    controller.save_configuration("traditional_controller_config_test.yaml")
    controller.load_configuration("traditional_controller_config_test.yaml")
    controller.reset()
    print("После сброса:")
    print(controller.get_traffic_light_states())


if __name__ == '__main__':
    main()
