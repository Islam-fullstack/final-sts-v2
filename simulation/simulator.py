#!/usr/bin/env python
"""
Файл: simulation/simulator.py

Класс TrafficSimulator моделирует транспортный поток для тестирования алгоритмов управления светофорами.
Также определён класс DummyVehicle для генерации транспортных средств.
"""

import time
import pickle
import random
import logging

class DummyVehicle:
    def __init__(self, id, vehicle_type, position=0.0, speed=0.0):
        self.id = id
        self.vehicle_type = vehicle_type
        self.position = position
        self.current_speed = speed
        self.waiting_time = 0.0
        self.route = []

    def update(self, dt):
        if self.current_speed > 0:
            self.position += self.current_speed * dt
        else:
            self.waiting_time += dt

    def __str__(self):
        return f"DummyVehicle({self.id}, {self.vehicle_type}, pos={self.position:.2f}, speed={self.current_speed:.2f})"

class TrafficSimulator:
    def __init__(self, config):
        self.config = config
        self.roads = []
        self.intersections = []
        self.vehicles = []
        self.controllers = []
        self.current_time = 0.0
        self.time_step = config.get("simulation", {}).get("time_step", 0.1)
        self.traffic_generators = []
        self.scheduled_events = []
        self.metrics_collector = None
        self.random_seed = config.get("simulation", {}).get("random_seed", None)
        if self.random_seed is not None:
            random.seed(self.random_seed)
        self.state_history = []
        self.logger = logging.getLogger("TrafficSimulator")
        self.logger.setLevel(logging.INFO)

    def setup_environment(self):
        env_config = self.config.get("environment", {})
        for inter_cfg in env_config.get("intersections", []):
            inter = type("DummyIntersection", (), {})()
            inter.id = inter_cfg.get("id")
            inter.position = tuple(inter_cfg.get("position", [0, 0]))
            inter.type = inter_cfg.get("type", "four_way")
            self.intersections.append(inter)
        for road_cfg in env_config.get("roads", []):
            road = type("DummyRoad", (), {})()
            road.id = road_cfg.get("id")
            road.start = tuple(road_cfg.get("start", [0, 0]))
            road.end = tuple(road_cfg.get("end", [0, 0]))
            road.length = road_cfg.get("length", 100)
            road.lanes = road_cfg.get("lanes", 2)
            road.speed_limit = road_cfg.get("speed_limit", 50)
            self.roads.append(road)
        self.logger.info(f"Environment: {len(self.roads)} roads, {len(self.intersections)} intersections.")

    def setup_controllers(self):
        self.controllers = []
        self.logger.info("Controllers setup completed.")

    def setup_traffic_generators(self):
        tg_configs = self.config.get("traffic_generators", [])
        from simulation.traffic_generator import TrafficGenerator
        for tg_cfg in tg_configs:
            tg = TrafficGenerator(tg_cfg)
            self.traffic_generators.append(tg)
        self.logger.info(f"Initialized {len(self.traffic_generators)} traffic generators.")

    def setup_metrics_collector(self):
        from simulation.metrics_collector import MetricsCollector
        metrics_config = self.config.get("metrics", {})
        self.metrics_collector = MetricsCollector(self, metrics_config)
        self.logger.info("Metrics collector initialized.")

    def step(self):
        dt = self.time_step
        self.current_time += dt
        for generator in self.traffic_generators:
            new_vehicles = generator.update(self.current_time, dt)
            for veh in new_vehicles:
                self.add_vehicle(veh)
        self.update_vehicles(dt)
        for ctrl in self.controllers:
            ctrl.update(dt)
        self.state_history.append(self.get_traffic_state())
        if self.metrics_collector:
            self.metrics_collector.update(self.current_time)

    def update_vehicles(self, dt):
        for veh in self.vehicles:
            veh.update(dt)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def get_traffic_state(self):
        num = len(self.vehicles)
        avg_speed = sum(v.current_speed for v in self.vehicles) / num if num else 0.0
        return {"time": self.current_time, "vehicles": num, "avg_speed": avg_speed}

    def schedule_event(self, event_time, event):
        event.time = event_time
        self.scheduled_events.append(event)
        self.logger.info(f"Event {event.__class__.__name__} scheduled at {event_time} s.")

    def run(self, duration):
        end_time = self.current_time + duration
        while self.current_time < end_time:
            self.step()
        self.logger.info("Simulation completed.")

    def reset(self):
        self.current_time = 0.0
        self.vehicles = []
        self.state_history = []
        self.scheduled_events = []
        if self.metrics_collector:
            self.metrics_collector.reset()
        self.logger.info("Simulation reset.")

    def save_state(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.state_history, f)
        self.logger.info(f"Simulation state saved to {filename}.")

    def load_state(self, filename):
        with open(filename, 'rb') as f:
            self.state_history = pickle.load(f)
        self.logger.info(f"Simulation state loaded from {filename}.")

if __name__ == "__main__":
    config = {
        "simulation": {"time_step": 0.1, "duration": 10, "random_seed": 42},
        "environment": {
            "intersections": [{"id": "main_intersection", "position": [0, 0], "type": "four_way"}],
            "roads": [
                {"id": "north_road", "start": [0, 100], "end": [0, 0], "length": 100, "lanes": 2, "speed_limit": 50},
                {"id": "south_road", "start": [0, 0], "end": [0, -100], "length": 100, "lanes": 2, "speed_limit": 50}
            ]
        },
        "traffic_generators": [],
        "metrics": {"collection_interval": 10, "metrics_to_collect": ["avg_speed", "vehicles"]}
    }
    simulator = TrafficSimulator(config)
    simulator.setup_environment()
    simulator.setup_controllers()
    simulator.setup_traffic_generators()
    simulator.setup_metrics_collector()
    simulator.run(5)
    print("Final traffic state:", simulator.get_traffic_state())
