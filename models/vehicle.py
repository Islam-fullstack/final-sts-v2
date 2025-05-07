#!/usr/bin/env python
"""
Файл: models/vehicle.py

Определяет иерархию классов транспортных средств для моделирования:
- Абстрактный класс Vehicle с общими атрибутами и методами.
- Конкретные классы: Car, Bus, Truck, Motorcycle.

Атрибуты:
  • id: уникальный идентификатор
  • vehicle_type: тип транспортного средства
  • length, width: размеры (метры)
  • max_speed, current_speed: максимальная и текущая скорость (м/с)
  • acceleration, deceleration: ускорение и замедление (м/с²)
  • position: положение на дороге (м)
  • lane: номер полосы
  • direction: направление движения
  • route: маршрут движения (список точек)
  • waiting_time: время ожидания (сек)
  • status: статус движения ("driving", "stopped", "waiting")

Методы:
  • update(dt): обновление положения за временной шаг dt
  • accelerate(dt)/decelerate(dt): изменение скорости
  • stop()/resume(): остановка и возобновление движения
  • change_lane(new_lane): смена полосы
  • calculate_fuel_consumption(): расчет расхода топлива (stub)
  • calculate_emissions(): расчет выбросов CO₂ (stub)
  • is_at_intersection(): проверка нахождения на перекрёстке (stub)
"""

from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self, id, vehicle_type, length, width, max_speed, acceleration, deceleration,
                 position=0.0, lane=1, direction="N", route=None, waiting_time=0.0, status="driving"):
        self.id = id
        self.vehicle_type = vehicle_type
        self.length = length
        self.width = width
        self.max_speed = max_speed
        self.current_speed = 0.0
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
        pass

    @abstractmethod
    def accelerate(self, dt):
        pass

    @abstractmethod
    def decelerate(self, dt):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def resume(self):
        pass

    @abstractmethod
    def change_lane(self, new_lane):
        pass

    @abstractmethod
    def calculate_fuel_consumption(self):
        pass

    @abstractmethod
    def calculate_emissions(self):
        pass

    @abstractmethod
    def is_at_intersection(self):
        pass

class Car(Vehicle):
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Car",
                         length=kwargs.get("length", 4.5),
                         width=kwargs.get("width", 1.8),
                         max_speed=kwargs.get("max_speed", 33.33),
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
        self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)
    def decelerate(self, dt):
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
        # Stub: ТС считается на перекрёстке, если его позиция между 100 и 110 м.
        return 100 <= self.position <= 110

class Bus(Vehicle):
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Bus",
                         length=kwargs.get("length", 12.0),
                         width=kwargs.get("width", 2.5),
                         max_speed=kwargs.get("max_speed", 22.22),
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
        self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)
    def decelerate(self, dt):
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
        self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)
    def decelerate(self, dt):
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
    def __init__(self, id, **kwargs):
        super().__init__(id, vehicle_type="Motorcycle",
                         length=kwargs.get("length", 2.2),
                         width=kwargs.get("width", 0.8),
                         max_speed=kwargs.get("max_speed", 38.89),
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
        self.current_speed = min(self.current_speed + self.acceleration * dt, self.max_speed)
    def decelerate(self, dt):
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

if __name__ == "__main__":
    import time
    dt = 1.0
    car = Car("car_1")
    bus = Bus("bus_1")
    truck = Truck("truck_1")
    moto = Motorcycle("moto_1")
    vehicles = [car, bus, truck, moto]
    for v in vehicles:
        v.accelerate(dt)
    for t in range(5):
        print(f"Time: {t} sec")
        for v in vehicles:
            v.update(dt)
            print(f"{v.vehicle_type} ({v.id}): pos={v.position:.2f}, speed={v.current_speed:.2f}, status={v.status}")
        time.sleep(1)
        print("-" * 40)
    print(f"Car fuel consumption: {car.calculate_fuel_consumption():.2f}")
    print(f"Car emissions: {car.calculate_emissions():.2f}")
    print(f"Is Car at intersection? {car.is_at_intersection()}")
