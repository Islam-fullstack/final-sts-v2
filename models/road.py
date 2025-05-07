#!/usr/bin/env python
"""
Файл: models/road.py

Реализует модели инфраструктуры:
  - Lane: полоса движения.
  - Road: участок дороги.
  - Intersection: перекрёсток.
"""

class Lane:
    def __init__(self, id, width, length, direction, max_speed, capacity):
        self.id = id
        self.width = width
        self.length = length
        self.direction = direction
        self.max_speed = max_speed
        self.vehicles = []
        self.capacity = capacity

    def add_vehicle(self, vehicle):
        if len(self.vehicles) < self.capacity:
            self.vehicles.append(vehicle)
        else:
            print(f"Lane {self.id} full. Cannot add vehicle {vehicle.id}.")

    def remove_vehicle(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def calculate_load(self):
        return (len(self.vehicles) / self.capacity) * 100 if self.capacity else 0.0

class Road:
    def __init__(self, id, name, lanes, start_point, end_point, speed_limit, traffic_lights=None):
        self.id = id
        self.name = name
        self.lanes = lanes  # список объектов Lane
        self.start_point = start_point
        self.end_point = end_point
        self.speed_limit = speed_limit
        self.traffic_lights = traffic_lights if traffic_lights is not None else []

    def add_vehicle(self, vehicle, lane_id):
        for lane in self.lanes:
            if lane.id == lane_id:
                lane.add_vehicle(vehicle)
                return
        print(f"Lane {lane_id} not found on road {self.name}.")

    def remove_vehicle(self, vehicle, lane_id):
        for lane in self.lanes:
            if lane.id == lane_id:
                lane.remove_vehicle(vehicle)
                return
        print(f"Lane {lane_id} not found on road {self.name}.")

    def calculate_average_speed(self):
        speeds = []
        for lane in self.lanes:
            for vehicle in lane.vehicles:
                speeds.append(vehicle.current_speed)
        return sum(speeds) / len(speeds) if speeds else 0.0

    def calculate_density(self):
        total_vehicles = sum(len(lane.vehicles) for lane in self.lanes)
        road_length = self.calculate_length() / 1000.0  # км
        return total_vehicles / road_length if road_length > 0 else 0.0

    def calculate_length(self):
        x1, y1 = self.start_point
        x2, y2 = self.end_point
        return ((x2 - x1)**2 + (y2 - y1)**2)**0.5

class Intersection:
    def __init__(self, id, name, incoming_roads, outgoing_roads, traffic_lights, connectivity_map):
        self.id = id
        self.name = name
        self.incoming_roads = incoming_roads  # список объектов Road
        self.outgoing_roads = outgoing_roads  # список объектов Road
        self.traffic_lights = traffic_lights    # список объектов TrafficLight
        self.connectivity_map = connectivity_map

    def manage_traffic(self):
        print(f"Managing traffic at {self.name}")

    def calculate_conflict_points(self):
        return len(self.incoming_roads) * len(self.outgoing_roads)

if __name__ == "__main__":
    lane1 = Lane("L1", 3.5, 500, "N", 33.33, 10)
    lane2 = Lane("L2", 3.5, 500, "N", 33.33, 10)
    road = Road("R1", "Main Road", [lane1, lane2], (0, 0), (0, 500), 33.33)
    print("Average speed on road:", road.calculate_average_speed())
    print("Density on road:", road.calculate_density())
    intersection = Intersection("I1", "Intersection 1", incoming_roads=[road], outgoing_roads=[road],
                                traffic_lights=[], connectivity_map={"N-E": True})
    intersection.manage_traffic()
    print("Conflict points:", intersection.calculate_conflict_points())
