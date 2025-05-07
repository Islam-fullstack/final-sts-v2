"""
Файл: controllers/traditional_controller_config.py

Описание:
  Класс TraditionalControllerConfig предназначен для хранения и валидации
  конфигурации традиционного контроллера светофоров. Класс позволяет:
    - загрузить конфигурацию из YAML файла;
    - проверить корректность настроек;
    - получить план времени для указанного времени суток;
    - экспортировать конфигурацию в виде словаря.
"""

import yaml


class TraditionalControllerConfig:
    def __init__(self, phase_settings=None, timing_plans=None, synchronization_settings=None, emergency_settings=None):
        self.phase_settings = phase_settings if phase_settings is not None else []
        self.timing_plans = timing_plans if timing_plans is not None else []
        self.synchronization_settings = synchronization_settings if synchronization_settings is not None else {}
        self.emergency_settings = emergency_settings if emergency_settings is not None else {}

    @classmethod
    def load_from_file(cls, filename):
        """
        Загружает конфигурацию из YAML файла.

        Аргументы:
          filename (str): Путь к YAML файлу.

        Возвращает:
          TraditionalControllerConfig: Объект конфигурации.
        """
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
        config = cls(
            phase_settings=data.get("phases", []),
            timing_plans=data.get("timing_plans", []),
            synchronization_settings=data.get("synchronization", {}),
            emergency_settings=data.get("emergency", {})
        )
        config.validate_config()
        return config

    def validate_config(self):
        """
        Проверяет корректность конфигурационных настроек.
        
        Выбрасывает:
          ValueError: Если настройки некорректны.
        """
        if not self.phase_settings:
            raise ValueError("Настройки фаз (phase_settings) отсутствуют.")
        if not isinstance(self.timing_plans, list):
            raise ValueError("timing_plans должен быть списком.")
        if "enabled" not in self.synchronization_settings:
            raise ValueError("Некорректные настройки синхронизации: отсутствует ключ 'enabled'.")
        if "enabled" not in self.emergency_settings:
            raise ValueError("Некорректные настройки ЧС: отсутствует ключ 'enabled'.")

    def get_timing_for_time_of_day(self, time_of_day):
        """
        Возвращает план длительностей фаз для заданного времени суток.

        Аргументы:
          time_of_day (str): Например, "Morning Peak", "Evening Peak", "Night", "Default".

        Возвращает:
          list: Список длительностей фаз.
        """
        for plan in self.timing_plans:
            if time_of_day in plan.get("time_range", []):
                return plan.get("phase_durations", [])
        for plan in self.timing_plans:
            if "default" in plan.get("time_range", []):
                return plan.get("phase_durations", [])
        return []

    def to_dict(self):
        """
        Экспортирует конфигурацию в формате словаря.
        
        Возвращает:
          dict: Конфигурация.
        """
        return {
            "phases": self.phase_settings,
            "timing_plans": self.timing_plans,
            "synchronization": self.synchronization_settings,
            "emergency": self.emergency_settings
        }


def main():
    """
    Демонстрация работы TraditionalControllerConfig.
    Загружает конфигурацию из файла YAML, выполняет валидацию и выводит настройки.
    """
    config_filename = "traditional_controller.yaml"
    sample_config = {
        "intersection_id": "main_intersection",
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

    with open(config_filename, 'w') as file:
        yaml.dump(sample_config, file)

    try:
        config_obj = TraditionalControllerConfig.load_from_file(config_filename)
        print("Конфигурация успешно загружена и валидирована:")
        print(config_obj.to_dict())
        timings = config_obj.get_timing_for_time_of_day("Morning Peak")
        print("Временной план для 'Morning Peak':", timings)
    except Exception as e:
        print("Ошибка при загрузке конфигурации:", e)


if __name__ == '__main__':
    main()
