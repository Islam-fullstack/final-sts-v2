"""
Файл: models/traffic_flow.py

Описание:
  Реализованы модели транспортного потока:
    • Класс TrafficFlow представляет поток транспорта с атрибутами:
         source_road, target_road, volume, vehicle_distribution, time_distribution, current_vehicles.
       Методы: генерация транспортных средств и расчёт характеристик потока.
    • Класс TrafficDemand моделирует транспортный спрос с матрицей корреспонденций,
         временными периодами и функциями спроса. Методы рассчитывают спрос и генерируют потоки.

Для автономного тестирования реализована функция main().
"""

import random

class TrafficFlow:
    """
    Класс для представления потока транспорта.

    Атрибуты:
      source_road: Исходная дорога.
      target_road: Целевая дорога.
      volume (float): Объём транспорта (ТС/сек).
      vehicle_distribution (dict): Распределение типов ТС, например:
          {"Car": 0.7, "Bus": 0.1, "Truck": 0.15, "Motorcycle": 0.05}.
      time_distribution (dict): Распределение интенсивности по времени.
      current_vehicles (list): Текущие ТС в потоке.
    """
    def __init__(self, source_road, target_road, volume, vehicle_distribution, time_distribution):
        self.source_road = source_road
        self.target_road = target_road
        self.volume = volume
        self.vehicle_distribution = vehicle_distribution
        self.time_distribution = time_distribution
        self.current_vehicles = []

    def generate_vehicles(self, simulation_time, vehicle_class_factory):
        """
        Генерирует транспортные средства на основе объёма и распределения.

        Аргументы:
          simulation_time (float): Время симуляции, сек.
          vehicle_class_factory (func): Фабрика для создания объекта ТС по заданному типу.
        
        Возвращает:
          list: Сгенерированные транспортные средства.
        """
        num_vehicles = int(self.volume * simulation_time)
        vehicles = []
        for _ in range(num_vehicles):
            r = random.random()
            cumulative = 0.0
            vehicle_type = None
            for vt, prob in self.vehicle_distribution.items():
                cumulative += prob
                if r <= cumulative:
                    vehicle_type = vt
                    break
            if vehicle_type is None:
                vehicle_type = list(self.vehicle_distribution.keys())[0]
            vehicle = vehicle_class_factory(vehicle_type)
            vehicles.append(vehicle)
        self.current_vehicles.extend(vehicles)
        return vehicles

    def calculate_flow_characteristics(self):
        """
        Рассчитывает характеристики потока: средняя скорость и плотность.

        Возвращает:
          dict: Характеристики (например, {"average_speed": ..., "density": ...}).
        """
        if not self.current_vehicles:
            return {"average_speed": 0.0, "density": 0}
        total_speed = sum(vehicle.current_speed for vehicle in self.current_vehicles)
        average_speed = total_speed / len(self.current_vehicles)
        density = len(self.current_vehicles)  # Условный параметр
        return {"average_speed": average_speed, "density": density}


class TrafficDemand:
    """
    Класс для моделирования транспортного спроса.

    Атрибуты:
      origin_destination_matrix (dict): Матрица корреспонденций,
         например, {("Origin1", "Destination1"): 50, ...}.
      time_periods (dict): Временные периоды с соответствующими коэффициентами,
         например, {"morning": 1.2, "afternoon": 0.8, "evening": 1.5}.
      demand_functions (dict): Функции спроса для каждого периода (опционально).
    """
    def __init__(self, origin_destination_matrix, time_periods, demand_functions=None):
        self.origin_destination_matrix = origin_destination_matrix
        self.time_periods = time_periods
        self.demand_functions = demand_functions if demand_functions is not None else {}

    def calculate_demand(self, period):
        """
        Рассчитывает спрос для заданного периода.

        Аргументы:
          period (str): Временной период (например, "morning").
        
        Возвращает:
          dict: Спрос по каждому направлению.
        """
        factor = self.time_periods.get(period, 1.0)
        demand = {}
        for key, base in self.origin_destination_matrix.items():
            demand[key] = base * factor
        return demand

    def generate_flow(self, period, vehicle_class_factory, simulation_time):
        """
        Генерирует потоки транспорта для каждого направления исходя из спроса.

        Аргументы:
          period (str): Временной период.
          vehicle_class_factory (func): Фабрика для создания объекта ТС.
          simulation_time (float): Время симуляции, сек.
        
        Возвращает:
          dict: Потоки для каждой пары (origin, destination).
        """
        demand = self.calculate_demand(period)
        flows = {}
        for od, num in demand.items():
            volume = num / simulation_time
            vehicle_distribution = {"Car": 0.7, "Bus": 0.1, "Truck": 0.15, "Motorcycle": 0.05}
            time_distribution = {"default": 1.0}
            flow = TrafficFlow(source_road=od[0], target_road=od[1],
                               volume=volume, vehicle_distribution=vehicle_distribution,
                               time_distribution=time_distribution)
            flow.generate_vehicles(simulation_time, vehicle_class_factory)
            flows[od] = flow
        return flows


def main():
    """
    Демонстрация работы классов TrafficFlow и TrafficDemand.
    Создаются потоки транспорта и рассчитываются их характеристики.
    """
    # Фабрика для создания транспортных средств (Dummy-класс для теста)
    class DummyVehicle:
        def __init__(self, vehicle_type):
            self.vehicle_type = vehicle_type
            self.current_speed = random.uniform(10, 30)
            self.id = f"{vehicle_type}_{random.randint(1, 1000)}"
    def vehicle_factory(vt):
        return DummyVehicle(vt)

    # Тестирование TrafficFlow
    flow = TrafficFlow(source_road="Road_A", target_road="Road_B",
                       volume=5,  # 5 ТС/сек
                       vehicle_distribution={"Car": 0.8, "Bus": 0.1, "Truck": 0.1, "Motorcycle": 0.0},
                       time_distribution={"default": 1.0})
    sim_time = 10  # 10 секунд симуляции
    vehicles = flow.generate_vehicles(sim_time, vehicle_factory)
    characteristics = flow.calculate_flow_characteristics()
    print("Сгенерированные транспортные средства:")
    for v in vehicles:
        print(f"{v.id}: {v.vehicle_type}, скорость {v.current_speed:.2f} м/с")
    print("Характеристики потока:", characteristics)

    # Тестирование TrafficDemand
    od_matrix = {("Origin1", "Destination1"): 50,
                 ("Origin1", "Destination2"): 30,
                 ("Origin2", "Destination1"): 20}
    time_periods = {"morning": 1.2, "afternoon": 0.8, "evening": 1.5}
    demand = TrafficDemand(origin_destination_matrix=od_matrix, time_periods=time_periods)
    calculated_demand = demand.calculate_demand("morning")
    print("Рассчитанный утренний спрос:", calculated_demand)
    flows = demand.generate_flow("morning", vehicle_factory, simulation_time=10)
    for od, f in flows.items():
        char = f.calculate_flow_characteristics()
        print(f"Поток для {od}: {char}")

if __name__ == '__main__':
    main()
