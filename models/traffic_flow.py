#!/usr/bin/env python
"""
Файл: models/traffic_flow.py

Модели транспортного потока:
  - TrafficFlow: представление потока (список ТС).
  - TrafficDemand: моделирование транспортного спроса.
"""

class TrafficFlow:
    def __init__(self):
        self.vehicles = []

    def update_flow(self, dt):
        for vehicle in self.vehicles:
            vehicle.update(dt)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

class TrafficDemand:
    def __init__(self, origin_destination_matrix, time_periods, demand_functions=None):
        self.origin_destination_matrix = origin_destination_matrix
        self.time_periods = time_periods
        self.demand_functions = demand_functions if demand_functions is not None else {}

    def calculate_demand(self, period):
        factor = self.time_periods.get(period, 1.0)
        demand = {}
        for key, base in self.origin_destination_matrix.items():
            demand[key] = base * factor
        return demand

    def generate_flow(self, period, vehicle_class_factory, simulation_time):
        demand = self.calculate_demand(period)
        flows = {}
        for od, num in demand.items():
            volume = num / simulation_time
            flow = TrafficFlow()
            for _ in range(int(volume * simulation_time)):
                flow.add_vehicle(vehicle_class_factory(od))
            flows[od] = flow
        return flows

if __name__ == "__main__":
    import random
    def vehicle_factory(od):
        return type("DummyVehicle", (), {"id": f"veh_{random.randint(1, 1000)}", "current_speed": random.uniform(10, 30)})()
    od_matrix = {("Origin1", "Destination1"): 50,
                 ("Origin1", "Destination2"): 30,
                 ("Origin2", "Destination1"): 20}
    time_periods = {"morning": 1.2, "afternoon": 0.8, "evening": 1.5}
    demand = TrafficDemand(od_matrix, time_periods)
    flows = demand.generate_flow("morning", vehicle_factory, simulation_time=10)
    for od, flow in flows.items():
        print(f"Flow for {od}: {len(flow.vehicles)} vehicles")
