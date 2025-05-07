# simulation/events.py
import random

class SimulationEvent:
    """
    Базовый класс для событий симуляции.
    
    Атрибуты:
      - time (float): Время наступления события.
    """
    def __init__(self, time=0.0):
        self.time = time

    def execute(self, simulation):
        """
        Выполняет событие.
        
        Аргументы:
          simulation: объект симулятора.
        """
        raise NotImplementedError("Метод execute() должен быть реализован в подклассах.")

class VehicleGenerationEvent(SimulationEvent):
    """
    Событие генерации транспортного средства.
    """
    def __init__(self, generator_id):
        super().__init__()
        self.generator_id = generator_id

    def execute(self, simulation):
        for tg in simulation.traffic_generators:
            if tg.id == self.generator_id:
                veh = tg.generate_vehicle()
                simulation.add_vehicle(veh)
                simulation.logger.info(f"VehicleGenerationEvent: сгенерирован ТС {veh.id} от генератора {self.generator_id}.")
                break

class TrafficFlowChangeEvent(SimulationEvent):
    """
    Событие изменения интенсивности потока.
    """
    def __init__(self, generator_id, new_flow_rate):
        super().__init__()
        self.generator_id = generator_id
        self.new_flow_rate = new_flow_rate

    def execute(self, simulation):
        for tg in simulation.traffic_generators:
            if tg.id == self.generator_id:
                tg.set_flow_rate(self.new_flow_rate)
                simulation.logger.info(f"TrafficFlowChangeEvent: интенсивность генератора {self.generator_id} изменена на {self.new_flow_rate} ТС/час.")
                break

class TrafficLightOverrideEvent(SimulationEvent):
    """
    Событие принудительного изменения режима светофора.
    """
    def __init__(self, traffic_light_id, new_state):
        super().__init__()
        self.traffic_light_id = traffic_light_id
        self.new_state = new_state

    def execute(self, simulation):
        # Stub - демонстрация: вывод сообщения
        simulation.logger.info(f"TrafficLightOverrideEvent: светофору {self.traffic_light_id} задан режим {self.new_state} (stub).")

class EmergencyVehicleEvent(SimulationEvent):
    """
    Событие появления автомобиля экстренных служб.
    """
    def __init__(self, route):
        super().__init__()
        self.route = route

    def execute(self, simulation):
        from simulation.simulator import DummyVehicle
        veh_id = f"emergency_{random.randint(1000, 9999)}"
        emergency_vehicle = DummyVehicle(veh_id, "emergency", position=0.0, speed=20.0)
        emergency_vehicle.route = self.route
        simulation.add_vehicle(emergency_vehicle)
        simulation.logger.info(f"EmergencyVehicleEvent: добавлен ТС экстренных служб {veh_id} с маршрутом {self.route}.")

class AccidentEvent(SimulationEvent):
    """
    Событие моделирования ДТП.
    """
    def execute(self, simulation):
        simulation.logger.info("AccidentEvent: произошло ДТП (stub).")

class RoadClosureEvent(SimulationEvent):
    """
    Событие закрытия участка дороги.
    """
    def execute(self, simulation):
        simulation.logger.info("RoadClosureEvent: участок дороги закрыт (stub).")


def main():
    """
    Демонстрация работы событий симуляции.
    Создаётся dummy-симулятор, добавляется dummy-генератор, затем выполняются события.
    """
    class DummySimulator:
        def __init__(self):
            self.traffic_generators = []
            self.vehicles = []
            self.logger = __import__("logging").getLogger("DummySimulator")
    sim = DummySimulator()
    # Создаём dummy-генератор
    from simulation.traffic_generator import TrafficGenerator
    tg_config = {"id": "north_generator", "source_road": "north_road", "position": [0, 100], "base_flow_rate": 600, "vehicle_types": {"car": 0.7, "bus": 0.1, "truck": 0.15, "motorcycle": 0.05}}
    tg = TrafficGenerator(tg_config)
    sim.traffic_generators.append(tg)

    # Создаём и выполняем события
    event1 = TrafficFlowChangeEvent("north_generator", 900)
    event2 = EmergencyVehicleEvent(route=["south_road", "main_intersection", "north_road"])
    event1.time = 10
    event2.time = 20
    event1.execute(sim)
    event2.execute(sim)

if __name__ == '__main__':
    main()
