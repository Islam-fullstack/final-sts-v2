"""
Файл: models/vehicle.py

Описание:
  Реализована полная иерархия классов для транспортных средств:
    • Абстрактный базовый класс Vehicle с общими свойствами и методами.
    • Подклассы для разных типов ТС: Car, Bus, Truck, Motorcycle.
  
Каждый класс содержит следующие атрибуты:
  - id: Уникальный идентификатор.
  - vehicle_type: Тип транспортного средства.
  - length, width: Размеры (м).
  - max_speed, current_speed: Максимальная и текущая скорость (м/с).
  - acceleration, deceleration: Ускорение и замедление (м/с²).
  - position: Текущая позиция на дороге (м).
  - lane: Номер полосы.
  - direction: Направление движения.
  - route: Маршрут движения (список точек).
  - waiting_time: Время ожидания (сек).
  - status: Статус движения (driving, stopped, waiting).
  
Методы:
  - update(dt): Обновление положения за временной шаг dt.
  - accelerate(dt), decelerate(dt): Изменение скорости.
  - stop(), resume(): Остановка и возобновление движения.
  - change_lane(new_lane): Смена полосы.
  - calculate_fuel_consumption(): Расчёт расхода топлива.
  - calculate_emissions(): Расчёт выбросов CO2.
  - is_at_intersection(): Проверка нахождения на перекрёстке.

Для автономного тестирования реализована функция main().
"""

from abc import ABC, abstractmethod

class Vehicle(ABC):
    """
    Абстрактный базовый класс для транспортных средств.

    Атрибуты:
      id (str): Уникальный идентификатор.
      vehicle_type (str): Тип транспортного средства.
      length (float): Длина транспортного средства, м.
      width (float): Ширина транспортного средства, м.
      max_speed (float): Максимальная скорость, м/с.
      current_speed (float): Текущая скорость, м/с.
      acceleration (float): Ускорение, м/с².
      deceleration (float): Замедление, м/с².
      position (float): Текущая позиция на дороге, м.
      lane (int): Текущая полоса.
      direction (str): Направление движения.
      route (list): Маршрут движения.
      waiting_time (float): Время ожидания, сек.
      status (str): Статус (driving, stopped, waiting).
    """
    def __init__(self, id, vehicle_type, length, width, max_speed, acceleration, deceleration,
                 position=0.0, lane=1, direction="N", route=None, waiting_time=0.0, status="driving"):
        self.id = id
        self.vehicle_type = vehicle_type
        self.length = length
        self.width = width
        self.max_speed = max_speed
        self.current_speed = 0.0  # Начинаем с нулевой скорости
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.position = position
        self.lane = lane
        self.direction = direction
        self.route = route if route is not None else []
        self.waiting_time = waiting_time
        self.status = status

    @abstractmethod
    def update(self, dt):
        """
        Обновляет положение за временной шаг dt.
        dt (float): Временной интервал в секундах.
        """
        pass

    @abstractmethod
    def accelerate(self, dt):
        """
        Ускоряет транспортное средство за время dt.
        dt (float): Временной интервал в секундах.
        """
        pass

    @abstractmethod
    def decelerate(self, dt):
        """
        Замедляет транспортное средство за время dt.
        dt (float): Временной интервал в секундах.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Останавливает транспортное средство.
        """
        pass

    @abstractmethod
    def resume(self):
        """
        Возобновляет движение транспортного средства.
        """
        pass

    @abstractmethod
    def change_lane(self, new_lane):
        """
        Смена полосы движения.
        new_lane (int): Новый номер полосы.
        """
        pass

    @abstractmethod
    def calculate_fuel_consumption(self):
        """
        Расчитывает расход топлива.
        
        Возвращает:
           float: Условное значение расхода топлива.
        """
        pass

    @abstractmethod
    def calculate_emissions(self):
        """
        Расчитывает выбросы CO2.
        
        Возвращает:
           float: Условное значение выбросов.
        """
        pass

    @abstractmethod
    def is_at_intersection(self):
        """
        Проверяет, находится ли ТС на перекрёстке.
        
        Возвращает:
           bool: True, если ТС на перекрёстке, иначе False.
        """
        pass

# --- Подклассы ---

class Car(Vehicle):
    """Класс Car для легкового автомобиля."""
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Car",
                         length=kwargs.get("length", 4.5),
                         width=kwargs.get("width", 1.8),
                         max_speed=kwargs.get("max_speed", 33.33),  # ≈120 km/h
                         acceleration=kwargs.get("acceleration", 2.5),
                         deceleration=kwargs.get("deceleration", 3.0),
                         position=kwargs.get("position", 0.0),
                         lane=kwargs.get("lane", 1),
                         direction=kwargs.get("direction", "N"),
                         route=kwargs.get("route", []),
                         waiting_time=kwargs.get("waiting_time", 0.0),
                         status=kwargs.get("status", "driving"))

    def update(self, dt):
        if self.status == "driving":
            self.position += self.current_speed * dt
        else:
            self.waiting_time += dt

    def accelerate(self, dt):
        if self.status == "driving":
            self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)

    def decelerate(self, dt):
        if self.status == "driving":
            self.current_speed = max(self.current_speed - self.deceleration * dt, 0.0)

    def stop(self):
        self.current_speed = 0.0
        self.status = "stopped"

    def resume(self):
        if self.status == "stopped":
            self.status = "driving"

    def change_lane(self, new_lane):
        self.lane = new_lane

    def calculate_fuel_consumption(self):
        return 0.05 * (self.current_speed ** 2)

    def calculate_emissions(self):
        return 0.1 * self.calculate_fuel_consumption()

    def is_at_intersection(self):
        return 100 <= self.position <= 110


class Bus(Vehicle):
    """Класс Bus для автобуса."""
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Bus",
                         length=kwargs.get("length", 12.0),
                         width=kwargs.get("width", 2.5),
                         max_speed=kwargs.get("max_speed", 22.22),  # ~80 km/h
                         acceleration=kwargs.get("acceleration", 1.5),
                         deceleration=kwargs.get("deceleration", 2.0),
                         position=kwargs.get("position", 0.0),
                         lane=kwargs.get("lane", 1),
                         direction=kwargs.get("direction", "N"),
                         route=kwargs.get("route", []),
                         waiting_time=kwargs.get("waiting_time", 0.0),
                         status=kwargs.get("status", "driving"))

    def update(self, dt):
        if self.status == "driving":
            self.position += self.current_speed * dt
        else:
            self.waiting_time += dt

    def accelerate(self, dt):
        if self.status == "driving":
            self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)

    def decelerate(self, dt):
        if self.status == "driving":
            self.current_speed = max(self.current_speed - self.deceleration * dt, 0.0)

    def stop(self):
        self.current_speed = 0.0
        self.status = "stopped"

    def resume(self):
        if self.status == "stopped":
            self.status = "driving"

    def change_lane(self, new_lane):
        self.lane = new_lane

    def calculate_fuel_consumption(self):
        return 0.1 * (self.current_speed ** 2)

    def calculate_emissions(self):
        return 0.15 * self.calculate_fuel_consumption()

    def is_at_intersection(self):
        return 100 <= self.position <= 110


class Truck(Vehicle):
    """Класс Truck для грузового автомобиля."""
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Truck",
                         length=kwargs.get("length", 8.0),
                         width=kwargs.get("width", 2.5),
                         max_speed=kwargs.get("max_speed", 25.0),
                         acceleration=kwargs.get("acceleration", 1.8),
                         deceleration=kwargs.get("deceleration", 2.5),
                         position=kwargs.get("position", 0.0),
                         lane=kwargs.get("lane", 1),
                         direction=kwargs.get("direction", "N"),
                         route=kwargs.get("route", []),
                         waiting_time=kwargs.get("waiting_time", 0.0),
                         status=kwargs.get("status", "driving"))

    def update(self, dt):
        if self.status == "driving":
            self.position += self.current_speed * dt
        else:
            self.waiting_time += dt

    def accelerate(self, dt):
        if self.status == "driving":
            self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)

    def decelerate(self, dt):
        if self.status == "driving":
            self.current_speed = max(self.current_speed - self.deceleration * dt, 0.0)

    def stop(self):
        self.current_speed = 0.0
        self.status = "stopped"

    def resume(self):
        if self.status == "stopped":
            self.status = "driving"

    def change_lane(self, new_lane):
        self.lane = new_lane

    def calculate_fuel_consumption(self):
        return 0.12 * (self.current_speed ** 2)

    def calculate_emissions(self):
        return 0.18 * self.calculate_fuel_consumption()

    def is_at_intersection(self):
        return 100 <= self.position <= 110


class Motorcycle(Vehicle):
    """Класс Motorcycle для мотоцикла."""
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Motorcycle",
                         length=kwargs.get("length", 2.2),
                         width=kwargs.get("width", 0.8),
                         max_speed=kwargs.get("max_speed", 38.89),  # ~140 km/h
                         acceleration=kwargs.get("acceleration", 3.0),
                         deceleration=kwargs.get("deceleration", 3.5),
                         position=kwargs.get("position", 0.0),
                         lane=kwargs.get("lane", 1),
                         direction=kwargs.get("direction", "N"),
                         route=kwargs.get("route", []),
                         waiting_time=kwargs.get("waiting_time", 0.0),
                         status=kwargs.get("status", "driving"))

    def update(self, dt):
        if self.status == "driving":
            self.position += self.current_speed * dt
        else:
            self.waiting_time += dt

    def accelerate(self, dt):
        if self.status == "driving":
            self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)

    def decelerate(self, dt):
        if self.status == "driving":
            self.current_speed = max(self.current_speed - self.deceleration * dt, 0.0)

    def stop(self):
        self.current_speed = 0.0
        self.status = "stopped"

    def resume(self):
        if self.status == "stopped":
            self.status = "driving"

    def change_lane(self, new_lane):
        self.lane = new_lane

    def calculate_fuel_consumption(self):
        return 0.03 * (self.current_speed ** 2)

    def calculate_emissions(self):
        return 0.05 * self.calculate_fuel_consumption()

    def is_at_intersection(self):
        return 100 <= self.position <= 110


def main():
    """
    Тестирование классов транспортных средств.
    Создаются объекты каждого типа, выполняется обновление (с шагом dt = 1 секунда),
    выводятся значения позиции, скорости и других характеристик.
    """
    import time

    dt = 1.0  # временной шаг в секундах
    car = Car("car_1")
    bus = Bus("bus_1")
    truck = Truck("truck_1")
    motorcycle = Motorcycle("moto_1")
    vehicles = [car, bus, truck, motorcycle]

    # Начальное ускорение
    for v in vehicles:
        v.accelerate(dt)

    # Симуляция 5 временных шагов
    for t in range(5):
        print(f"Время: {t} сек")
        for v in vehicles:
            v.update(dt)
            print(f"{v.vehicle_type} ({v.id}): позиция = {v.position:.2f} м, скорость = {v.current_speed:.2f} м/с, статус = {v.status}")
        time.sleep(1)
        print("-" * 40)

    test_vehicle = car
    print(f"Расход топлива для {test_vehicle.vehicle_type}: {test_vehicle.calculate_fuel_consumption():.2f}")
    print(f"Выбросы CO2 для {test_vehicle.vehicle_type}: {test_vehicle.calculate_emissions():.2f}")
    print(f"На перекрестке: {test_vehicle.is_at_intersection()}")

if __name__ == '__main__':
    main()
