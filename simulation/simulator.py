# simulation/simulator.py
import yaml
import random
import time
import pickle
import logging
import os

from simulation.traffic_generator import TrafficGenerator
from simulation.metrics_collector import MetricsCollector
from simulation.events import TrafficFlowChangeEvent, EmergencyVehicleEvent

# Для примера создаём dummy-объекты для дорог, перекрёстков и транспортных средств

class DummyRoad:
    def __init__(self, id, start, end, length, lanes, speed_limit):
        self.id = id
        self.start = start
        self.end = end
        self.length = length
        self.lanes = lanes
        self.speed_limit = speed_limit

class DummyIntersection:
    def __init__(self, id, position, type_):
        self.id = id
        self.position = position
        self.type = type_

class DummyVehicle:
    def __init__(self, id, vehicle_type, position=0.0, speed=0.0):
        self.id = id
        self.vehicle_type = vehicle_type
        self.position = position
        self.current_speed = speed
        self.waiting_time = 0.0
    
    def update(self, dt):
        # Простейшее движение: при ненулевой скорости перемещаем транспортное средство
        self.position += self.current_speed * dt
        # Если скорость равна нулю, накопление времени ожидания
        if self.current_speed <= 0:
            self.waiting_time += dt
        else:
            self.waiting_time = max(0, self.waiting_time - dt)

    def __str__(self):
        return f"Vehicle({self.id}, type={self.vehicle_type}, pos={self.position:.1f}, speed={self.current_speed:.1f})"


class TrafficSimulator:
    """
    Основной класс симулятора транспортного потока для тестирования алгоритмов управления светофорами.
    
    Атрибуты:
      - roads: список объектов дорог.
      - intersections: список объектов перекрёстков.
      - vehicles: список активных транспортных средств.
      - controllers: список контроллеров светофоров (традиционных/умных).
      - current_time: текущее время симуляции.
      - time_step: шаг моделирования (сек).
      - traffic_generators: генераторы транспортного потока.
      - scheduled_events: список запланированных событий.
      - metrics_collector: объект для сбора метрик эффективности.
      - random_seed: начальное значение генератора случайных чисел.
      - state_history: история состояний системы.
    """
    def __init__(self, config):
        """
        Инициализирует симулятор согласно конфигурации.
        
        Аргументы:
          config (dict): Конфигурация симуляции.
        """
        self.config = config
        self.roads = []
        self.intersections = []
        self.vehicles = []
        self.controllers = []  # контроллеры светофоров, задаются извне
        self.current_time = 0.0
        self.time_step = config.get("simulation", {}).get("time_step", 0.1)
        self.traffic_generators = []
        self.scheduled_events = []  # список событий (объекты SimulationEvent)
        self.metrics_collector = None
        self.random_seed = config.get("simulation", {}).get("random_seed", None)
        if self.random_seed is not None:
            random.seed(self.random_seed)
        self.state_history = []
        self.logger = logging.getLogger("TrafficSimulator")
        logging.basicConfig(level=logging.INFO)

    def setup_environment(self):
        """
        Настраивает окружение симуляции: дороги, перекрёстки, светофоры.
        """
        env_config = self.config.get("environment", {})
        # Настройка перекрёстков
        for inter_cfg in env_config.get("intersections", []):
            inter = DummyIntersection(
                id=inter_cfg.get("id"), 
                position=tuple(inter_cfg.get("position", [0, 0])),
                type_=inter_cfg.get("type", "unknown")
            )
            self.intersections.append(inter)
        # Настройка дорог
        for road_cfg in env_config.get("roads", []):
            road = DummyRoad(
                id=road_cfg.get("id"),
                start=tuple(road_cfg.get("start", [0, 0])),
                end=tuple(road_cfg.get("end", [0, 0])),
                length=road_cfg.get("length", 100),
                lanes=road_cfg.get("lanes", 1),
                speed_limit=road_cfg.get("speed_limit", 50)
            )
            self.roads.append(road)
        self.logger.info(f"Environment setup: {len(self.roads)} roads, {len(self.intersections)} intersections.")

    def setup_controllers(self):
        """
        Настраивает контроллеры светофоров.
        В данном примере контроллеры не реализованы вовсе – список оставляем пустым.
        """
        self.controllers = []  # Можно добавить традиционный и умный контроллер
        self.logger.info("Controllers setup: {} controllers initialized.".format(len(self.controllers)))

    def setup_traffic_generators(self):
        """
        Настраивает генераторы транспортного потока.
        """
        tg_config_list = self.config.get("traffic_generators", [])
        for gen_cfg in tg_config_list:
            tg = TrafficGenerator(gen_cfg)
            self.traffic_generators.append(tg)
        self.logger.info("Traffic generators setup: {} generators initialized.".format(len(self.traffic_generators)))

    def setup_metrics_collector(self):
        """
        Инициализирует сборщик метрик.
        """
        metrics_config = self.config.get("metrics", {})
        self.metrics_collector = MetricsCollector(self, metrics_config)
        self.logger.info("Metrics collector initialized.")

    def step(self):
        """
        Выполняет один шаг симуляции:
          – обновление времени,
          – генерация новых транспортных средств,
          – обновление состояния ТС,
          – выполнение запланированных событий,
          – сбор метрик.
        """
        dt = self.time_step
        self.current_time += dt

        # Генерация транспортных средств
        for generator in self.traffic_generators:
            new_vehicles = generator.update(self.current_time, dt)
            for veh in new_vehicles:
                self.add_vehicle(veh)

        # Обновление ТС
        self.update_vehicles(dt)

        # Обновление светофоров (при наличии контроллеров)
        for ctrl in self.controllers:
            ctrl.update(dt)

        # Выполнение запланированных событий
        events_to_execute = [ev for ev in self.scheduled_events if ev.time <= self.current_time]
        for ev in events_to_execute:
            ev.execute(self)
            self.scheduled_events.remove(ev)

        # Обновление метрик
        if self.metrics_collector:
            self.metrics_collector.update(self.current_time)

        # Сохраняем состояние симуляции
        self.state_history.append(self.get_traffic_state())

    def update_vehicles(self, dt):
        """
        Обновляет состояние всех транспортных средств.
        """
        for veh in self.vehicles:
            veh.update(dt)

    def update_traffic_lights(self, dt):
        """
        Обновляет светофоры, если они обновляются самостоятельно.
        """
        pass

    def update_metrics(self):
        """
        Обновляет метрики эффективности.
        """
        if self.metrics_collector:
            self.metrics_collector.update(self.current_time)

    def add_vehicle(self, vehicle):
        """
        Добавляет транспортное средство в симуляцию.
        """
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        """
        Удаляет транспортное средство из симуляции.
        """
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def get_traffic_state(self):
        """
        Возвращает общее состояние трафика.
        
        Возвращает:
          dict: {time, количество ТС, средняя скорость}
        """
        num_vehicles = len(self.vehicles)
        avg_speed = (sum(v.current_speed for v in self.vehicles) / num_vehicles) if num_vehicles > 0 else 0.0
        return {"time": self.current_time, "vehicles": num_vehicles, "avg_speed": avg_speed}

    def schedule_event(self, time_event, event):
        """
        Планирует событие.
        
        Аргументы:
          time_event (float): Время наступления события.
          event (SimulationEvent): Объект события.
        """
        event.time = time_event
        self.scheduled_events.append(event)
        self.logger.info(f"Event {event.__class__.__name__} scheduled at {time_event}s.")

    def run(self, duration):
        """
        Запускает симуляцию в течение заданного времени.
        
        Аргументы:
          duration (float): Продолжительность симуляции в секундах.
        """
        steps = int(duration / self.time_step)
        self.logger.info(f"Starting simulation for {duration} sec ({steps} steps)...")
        for _ in range(steps):
            self.step()
        self.logger.info("Simulation completed.")

    def reset(self):
        """
        Сбрасывает симуляцию в начальное состояние.
        """
        self.current_time = 0.0
        self.vehicles = []
        self.state_history = []
        self.scheduled_events = []
        if self.metrics_collector:
            self.metrics_collector.reset()
        self.logger.info("Simulation state reset.")

    def save_state(self, filename):
        """
        Сохраняет историю состояний симуляции в файл.
        
        Аргументы:
          filename (str): Имя файла для сохранения.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self.state_history, f)
        self.logger.info(f"Simulation state saved to {filename}.")

    def load_state(self, filename):
        """
        Загружает историю состояний симуляции из файла.
        
        Аргументы:
          filename (str): Имя файла.
        """
        with open(filename, 'rb') as f:
            self.state_history = pickle.load(f)
        self.logger.info(f"Simulation state loaded from {filename}.")


def main():
    """
    Основная функция демонстрации работы симулятора.
    
    Выполняется:
      – загрузка конфигурации;
      – настройка среды (дороги, перекрёстки, светофоры);
      – инициализация контроллеров, генераторов трафика и сборщика метрик;
      – запуск симуляции;
      – вывод ключевых метрик и генерация отчёта.
    """
    # Загрузка конфигурации
    config_file = "configs/simulation.yaml"
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    simulator = TrafficSimulator(config)
    simulator.setup_environment()
    simulator.setup_controllers()
    simulator.setup_traffic_generators()
    simulator.setup_metrics_collector()

    # Планирование запланированных событий (например, изменение интенсивности потока, аварийное событие)
    scheduled = config.get("scheduled_events", [])
    for ev_cfg in scheduled:
        if ev_cfg.get("type") == "traffic_flow_change":
            event = TrafficFlowChangeEvent(
                generator_id=ev_cfg.get("generator_id"),
                new_flow_rate=ev_cfg.get("new_flow_rate")
            )
            simulator.schedule_event(ev_cfg.get("time"), event)
        elif ev_cfg.get("type") == "emergency_vehicle":
            event = EmergencyVehicleEvent(route=ev_cfg.get("route"))
            simulator.schedule_event(ev_cfg.get("time"), event)
        # Дополнительные события можно добавить аналогичным образом

    # Запуск симуляции
    sim_duration = config.get("simulation", {}).get("duration", 3600)
    simulator.run(sim_duration)

    # Вывод собранных метрик
    if simulator.metrics_collector:
        metrics = simulator.metrics_collector.get_current_metrics()
        print("Ключевые метрики симуляции:")
        print(metrics)
        # Экспорт метрик в CSV
        export_path = config.get("metrics", {}).get("export_path", "results/metrics.csv")
        simulator.metrics_collector.export_to_csv(export_path)
        # Генерация отчёта
        report = simulator.metrics_collector.generate_report()
        print("Отчёт по метрикам:")
        print(report)
    else:
        print("Метрики не собраны.")


if __name__ == '__main__':
    main()
