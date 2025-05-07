"""
Файл: models/road.py

Описание:
  Реализованы классы для дорожной инфраструктуры:
    • Класс Lane – представляет полосу движения с атрибутами: id, width, length, direction, max_speed, vehicles, capacity.
      Методы: добавление/удаление ТС, расчет загруженности.
    • Класс Road – представляет участок дороги с атрибутами: id, name, список полос (lanes), координаты начала/конца,
      светофоры, ограничение скорости. Методы: добавление/удаление ТС, расчёт средней скорости и плотности.
    • Класс Intersection – моделирует перекрёсток с входящими/исходящими дорогами, светофорами и матрицей связности.
      Методы: управление движением и расчет конфликтных точек.

Для автономного тестирования реализована функция main().
"""

class Lane:
    """
    Класс для представления полосы движения.

    Атрибуты:
      id (str): Идентификатор полосы.
      width (float): Ширина полосы, м.
      length (float): Длина полосы, м.
      direction (str): Направление движения ("N", "S", "E", "W").
      max_speed (float): Ограничение скорости, м/с.
      vehicles (list): Список ТС на полосе.
      capacity (int): Максимальное количество ТС.
    """
    def __init__(self, id, width, length, direction, max_speed, capacity):
        self.id = id
        self.width = width
        self.length = length
        self.direction = direction
        self.max_speed = max_speed
        self.capacity = capacity
        self.vehicles = []

    def add_vehicle(self, vehicle):
        """Добавляет транспортное средство на полосу, если есть место."""
        if len(self.vehicles) < self.capacity:
            self.vehicles.append(vehicle)
        else:
            print(f"Полоса {self.id} заполнена. Невозможно добавить ТС {vehicle.id}.")

    def remove_vehicle(self, vehicle):
        """Удаляет транспортное средство с полосы."""
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def calculate_load(self):
        """
        Рассчитывает загруженность полосы в %.
        
        Возвращает:
           float: Процент загруженности.
        """
        return (len(self.vehicles) / self.capacity) * 100 if self.capacity else 0.0


class Road:
    """
    Класс для представления участка дороги.

    Атрибуты:
      id (str): Идентификатор дороги.
      name (str): Название дороги.
      lanes (list): Список объектов Lane.
      start_point (tuple): Координаты начала (x, y).
      end_point (tuple): Координаты конца (x, y).
      speed_limit (float): Ограничение скорости, м/с.
      traffic_lights (list): Список светофоров на дороге.
    """
    def __init__(self, id, name, lanes, start_point, end_point, speed_limit, traffic_lights=None):
        self.id = id
        self.name = name
        self.lanes = lanes
        self.start_point = start_point
        self.end_point = end_point
        self.speed_limit = speed_limit
        self.traffic_lights = traffic_lights if traffic_lights is not None else []

    def add_vehicle(self, vehicle, lane_id):
        """
        Добавляет ТС на указанную полосу дороги.

        Аргументы:
          vehicle: Объект транспортного средства.
          lane_id (str): Идентификатор полосы.
        """
        for lane in self.lanes:
            if lane.id == lane_id:
                lane.add_vehicle(vehicle)
                return
        print(f"Полоса {lane_id} не найдена на дороге {self.name}.")

    def remove_vehicle(self, vehicle, lane_id):
        """Удаляет ТС с указанной полосы."""
        for lane in self.lanes:
            if lane.id == lane_id:
                lane.remove_vehicle(vehicle)
                return
        print(f"Полоса {lane_id} не найдена на дороге {self.name}.")

    def calculate_average_speed(self):
        """
        Рассчитывает среднюю скорость всех ТС на дороге.
        
        Возвращает:
          float: Средняя скорость, м/с.
        """
        speeds = []
        for lane in self.lanes:
            for vehicle in lane.vehicles:
                speeds.append(vehicle.current_speed)
        return sum(speeds) / len(speeds) if speeds else 0.0

    def calculate_density(self):
        """
        Рассчитывает плотность ТС по длине дороги (ТС на км).

        Возвращает:
          float: Плотность.
        """
        total_vehicles = sum(len(lane.vehicles) for lane in self.lanes)
        road_length = (( (self.end_point[0]-self.start_point[0])**2 + (self.end_point[1]-self.start_point[1])**2 ) ** 0.5) / 1000
        return total_vehicles / road_length if road_length else 0.0


class Intersection:
    """
    Класс для моделирования перекрёстка.

    Атрибуты:
      id (str): Идентификатор.
      name (str): Название.
      incoming_roads (list): Входящие дороги.
      outgoing_roads (list): Исходящие дороги.
      traffic_lights (list): Светофоры на перекрёстке.
      connections (dict): Матрица/словарь связности направлений.
    """
    def __init__(self, id, name, incoming_roads, outgoing_roads, traffic_lights, connections):
        self.id = id
        self.name = name
        self.incoming_roads = incoming_roads
        self.outgoing_roads = outgoing_roads
        self.traffic_lights = traffic_lights
        self.connections = connections

    def manage_traffic(self):
        """Пример управления движением на перекрёстке."""
        print(f"Управление движением на перекрёстке {self.name}.")

    def calculate_conflict_points(self):
        """
        Рассчитывает количество конфликтных точек.
        
        Возвращает:
          int: Количество конфликтных точек.
        """
        return len(self.incoming_roads) * len(self.outgoing_roads)


def main():
    """
    Демонстрация работы классов Lane, Road и Intersection.
    Создаются полосы, дорога и перекрёсток, выполняется добавление ТС
    и вычисление характеристик.
    """
    # Создаем полосы
    lane1 = Lane(id="L1", width=3.5, length=500, direction="N", max_speed=33.33, capacity=10)
    lane2 = Lane(id="L2", width=3.5, length=500, direction="N", max_speed=33.33, capacity=10)

    # Создаем дорогу с двумя полосами
    road = Road(id="R1", name="Улица Пушкина", lanes=[lane1, lane2],
                start_point=(0, 0), end_point=(0, 500), speed_limit=33.33)

    # Создаем тестовые транспортные средства (Dummy)
    class DummyVehicle:
        def __init__(self, id, current_speed):
            self.id = id
            self.current_speed = current_speed

    vehicle1 = DummyVehicle("D1", current_speed=15.0)
    vehicle2 = DummyVehicle("D2", current_speed=20.0)
    
    road.add_vehicle(vehicle1, lane_id="L1")
    road.add_vehicle(vehicle2, lane_id="L2")

    print(f"Средняя скорость на дороге: {road.calculate_average_speed():.2f} м/с")
    print(f"Плотность на дороге: {road.calculate_density():.2f} ТС на км")

    # Создаем перекрёсток
    intersection = Intersection(id="I1", name="Перекресток 1", 
                                incoming_roads=[road], outgoing_roads=[road],
                                traffic_lights=[], connections={"N-E": True, "E-S": True})
    intersection.manage_traffic()
    print(f"Конфликтных точек: {intersection.calculate_conflict_points()}")

if __name__ == '__main__':
    main()
