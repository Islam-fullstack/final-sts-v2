# simulation/traffic_generator.py
import random
import uuid

class TrafficGenerator:
    """
    Генерирует транспортный поток.
    
    Атрибуты:
      - source_points: координаты источника (из конфигурации).
      - vehicle_types: словарь вероятностей типов ТС.
      - flow_rate: базовая интенсивность потока (ТС/час).
      - time_pattern: темп численности по времени.
      - generated_vehicles: счетчик сгенерированных ТС.
    """
    def __init__(self, config):
        self.id = config.get("id", "tg_" + str(uuid.uuid4()))
        self.source_road = config.get("source_road")
        self.position = tuple(config.get("position", [0, 0]))
        self.base_flow_rate = config.get("base_flow_rate", 600)  # ТС/час
        self.vehicle_types = config.get("vehicle_types", {"car": 0.7, "bus": 0.1, "truck": 0.15, "motorcycle": 0.05})
        self.time_pattern = config.get("time_pattern", {})  # Можно использовать для изменения интенсивности по времени
        self.generated_vehicles = 0

    def update(self, current_time, dt):
        """
        Обновляет генератор за временной шаг dt.
        
        Аргументы:
          current_time (float): Текущее время симуляции.
          dt (float): Временной шаг (сек).
          
        Возвращает:
          list: Список сгенерированных транспортных средств (может быть пустым).
        """
        new_vehicles = []
        # Преобразуем базовую интенсивность в ТС/сек: flow_rate/3600
        current_flow = self.get_flow_rate(current_time) / 3600.0
        # Вероятность появления ТС за dt
        if random.random() < current_flow * dt:
            veh = self.generate_vehicle()
            new_vehicles.append(veh)
            self.generated_vehicles += 1
        return new_vehicles

    def generate_vehicle(self):
        """
        Генерирует новое транспортное средство.
        
        Возвращает:
          DummyVehicle: Объект транспортного средства.
        """
        vehicle_type = self.determine_vehicle_type()
        route = self.determine_route(self.source_road)
        # Для упрощения используем DummyVehicle, импортируем его из simulators
        from simulation.simulator import DummyVehicle
        vehicle_id = f"{vehicle_type}_{uuid.uuid4()}"
        veh = DummyVehicle(vehicle_id, vehicle_type, position=0.0, speed=0.0)
        veh.route = route
        return veh

    def determine_vehicle_type(self):
        """
        Определяет тип транспортного средства по заданным вероятностям.
        
        Возвращает:
          str: Тип ТС.
        """
        rnd = random.random()
        cumulative = 0.0
        for v_type, prob in self.vehicle_types.items():
            cumulative += prob
            if rnd < cumulative:
                return v_type
        return list(self.vehicle_types.keys())[0]

    def determine_route(self, source):
        """
        Определяет маршрут транспортного средства.
        Stub-реализация – возвращает простой маршрут.
        
        Возвращает:
          list: Список идентификаторов маршрута.
        """
        return [source, "main_intersection"]

    def get_flow_rate(self, current_time):
        """
        Рассчитывает текущую интенсивность потока, возможно с учетом временного шаблона.
        
        Аргументы:
          current_time (float): Текущее время симуляции (в секундах).
          
        Возвращает:
          float: Интенсивность потока (ТС/час).
        """
        # Stub: используем базовый поток без изменений.
        return self.base_flow_rate

    def set_flow_rate(self, new_rate):
        """
        Изменяет базовую интенсивность потока.
        """
        self.base_flow_rate = new_rate

    def get_statistics(self):
        """
        Возвращает статистику генерации транспортных средств.
        
        Возвращает:
          dict: Статистика, например {"generated": ...}
        """
        return {"generated": self.generated_vehicles}


def main():
    """
    Демонстрация работы TrafficGenerator.
    """
    config = {
        "id": "north_generator",
        "source_road": "north_road",
        "position": [0, 100],
        "base_flow_rate": 600,
        "vehicle_types": {"car": 0.7, "bus": 0.1, "truck": 0.15, "motorcycle": 0.05},
        "time_pattern": {}
    }
    tg = TrafficGenerator(config)
    current_time = 0.0
    dt = 1.0
    total_generated = 0
    for _ in range(3600):  # моделируем один час (3600 сек)
        new_vehicles = tg.update(current_time, dt)
        total_generated += len(new_vehicles)
        current_time += dt
    print("Сгенерировано транспортных средств:", tg.get_statistics()["generated"])


if __name__ == '__main__':
    main()
