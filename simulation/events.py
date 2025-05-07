#!/usr/bin/env python
"""
Файл: simulation/events.py

Модуль событий симуляции.
Определяет базовый класс SimulationEvent и его подклассы:
  - VehicleGenerationEvent: генерация транспортного средства.
  - TrafficFlowChangeEvent: изменение интенсивности потока.
  - TrafficLightOverrideEvent: принудительное изменение режима светофора.
  - EmergencyVehicleEvent: появление транспортного средства экстренных служб.
  - AccidentEvent: моделирование ДТП (stub).
  - RoadClosureEvent: закрытие участка дороги (stub).

Для корректного запуска модуля рекомендуется запускать его как часть пакета (например, python -m simulation.events).
"""

import random

class SimulationEvent:
    def __init__(self, time=0.0):
        self.time = time

    def execute(self, simulation):
        raise NotImplementedError("Метод execute() должен быть реализован в подклассах.")

class VehicleGenerationEvent(SimulationEvent):
    def __init__(self, generator_id):
        super().__init__()
        self.generator_id = generator_id

    def execute(self, simulation):
        for tg in simulation.traffic_generators:
            if tg.id == self.generator_id:
                veh = tg.generate_vehicle()
                simulation.add_vehicle(veh)
                simulation.logger.info(f"VehicleGenerationEvent: ТС {veh.id} сгенерирован от генератора {self.generator_id}.")
                break

class TrafficFlowChangeEvent(SimulationEvent):
    def __init__(self, generator_id, new_flow_rate):
        super().__init__()
        self.generator_id = generator_id
        self.new_flow_rate = new_flow_rate

    def execute(self, simulation):
        for tg in simulation.traffic_generators:
            if tg.id == self.generator_id:
                tg.set_flow_rate(self.new_flow_rate)
                simulation.logger.info(f"TrafficFlowChangeEvent: Интенсивность генератора {self.generator_id} изменена на {self.new_flow_rate} ТС/час.")
                break

class TrafficLightOverrideEvent(SimulationEvent):
    def __init__(self, traffic_light_id, new_state):
        super().__init__()
        self.traffic_light_id = traffic_light_id
        self.new_state = new_state

    def execute(self, simulation):
        found = False
        for ctrl in simulation.controllers:
            states = ctrl.get_traffic_light_states()
            if self.traffic_light_id in states:
                simulation.logger.info(f"TrafficLightOverrideEvent: Светофору {self.traffic_light_id} установлен режим {self.new_state}.")
                found = True
        if not found:
            simulation.logger.warning(f"TrafficLightOverrideEvent: Светофор {self.traffic_light_id} не найден.")

class EmergencyVehicleEvent(SimulationEvent):
    def __init__(self, route):
        super().__init__()
        self.route = route

    def execute(self, simulation):
        # Для создания TС экстренных служб используем DummyVehicle из simulation.simulator
        from simulation.simulator import DummyVehicle
        veh_id = f"emergency_{random.randint(1000, 9999)}"
        emergency_vehicle = DummyVehicle(veh_id, "emergency", position=0.0, speed=20.0)
        emergency_vehicle.route = self.route
        simulation.add_vehicle(emergency_vehicle)
        simulation.logger.info(f"EmergencyVehicleEvent: Экстренное ТС {veh_id} с маршрутом {self.route} добавлено.")

class AccidentEvent(SimulationEvent):
    def execute(self, simulation):
        simulation.logger.info("AccidentEvent: произошло ДТП (stub).")

class RoadClosureEvent(SimulationEvent):
    def execute(self, simulation):
        simulation.logger.info("RoadClosureEvent: участок дороги закрыт (stub).")

def main():
    """
    Демонстрация работы событий симуляции.
    Запускается как часть dummy-симуляции.
    """
    class DummySimulator:
        def __init__(self):
            self.traffic_generators = []
            self.vehicles = []
            self.controllers = []
            import logging
            self.logger = logging.getLogger("DummySimulator")
            self.logger.setLevel(10)
    sim = DummySimulator()
    from simulation.traffic_generator import TrafficGenerator
    tg_config = {
        "id": "north_generator",
        "source_road": "north_road",
        "position": [0, 100],
        "base_flow_rate": 600,
        "vehicle_types": {"car": 0.7, "bus": 0.1, "truck": 0.15, "motorcycle": 0.05}
    }
    tg = TrafficGenerator(tg_config)
    sim.traffic_generators.append(tg)

    event1 = TrafficFlowChangeEvent("north_generator", 900)
    event2 = EmergencyVehicleEvent(route=["south_road", "main_intersection", "north_road"])
    event1.time = 10
    event2.time = 20
    event1.execute(sim)
    event2.execute(sim)

if __name__ == "__main__":
    main()
