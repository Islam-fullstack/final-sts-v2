#!/usr/bin/env python
"""
Файл: simulation/traffic_generator.py

Класс TrafficGenerator генерирует транспортный поток.
Переводит базовый поток (ТС/час) в вероятность генерации ТС за dt.
Использует DummyVehicle для создания транспортных средств.
"""

import random
import uuid

class TrafficGenerator:
    def __init__(self, config):
        self.id = config.get("id", "tg_" + str(uuid.uuid4()))
        self.source_road = config.get("source_road")
        self.position = tuple(config.get("position", [0, 0]))
        self.base_flow_rate = config.get("base_flow_rate", 600)  # ТС/час
        self.vehicle_types = config.get("vehicle_types", {"car": 0.7, "bus": 0.1, "truck": 0.15, "motorcycle": 0.05})
        self.time_pattern = config.get("time_pattern", {})
        self.generated_vehicles = 0

    def update(self, current_time, dt):
        new_vehicles = []
        current_flow = self.get_flow_rate(current_time) / 3600.0
        if random.random() < current_flow * dt:
            veh = self.generate_vehicle()
            new_vehicles.append(veh)
            self.generated_vehicles += 1
        return new_vehicles

    def generate_vehicle(self):
        vehicle_type = self.determine_vehicle_type()
        route = self.determine_route(self.source_road)
        # Используем относительный импорт: для запуска из корня убедитесь, что проект запущен как пакет
        from simulation.simulator import DummyVehicle
        vehicle_id = f"{vehicle_type}_{uuid.uuid4()}"
        veh = DummyVehicle(vehicle_id, vehicle_type, position=0.0, speed=random.uniform(10, 30))
        veh.route = route
        return veh

    def determine_vehicle_type(self):
        rnd = random.random()
        cumulative = 0.0
        for v_type, prob in self.vehicle_types.items():
            cumulative += prob
            if rnd < cumulative:
                return v_type
        return list(self.vehicle_types.keys())[0]

    def determine_route(self, source):
        return [source, "main_intersection"]

    def get_flow_rate(self, current_time):
        return self.base_flow_rate

    def set_flow_rate(self, new_rate):
        self.base_flow_rate = new_rate

    def get_statistics(self):
        return {"generated": self.generated_vehicles}

if __name__ == "__main__":
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
    for _ in range(3600):
        tg.update(current_time, dt)
        current_time += dt
    print("Vehicles generated:", tg.get_statistics()["generated"])
