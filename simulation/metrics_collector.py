# simulation/metrics_collector.py
import csv
import os

class MetricsCollector:
    """
    Класс для сбора и анализа метрик эффективности симуляции.
    
    Атрибуты:
      - simulation: ссылка на объект симулятора.
      - collection_interval: интервал сбора данных (сек).
      - last_collection_time: время последнего сбора.
      - metrics_history: история собранных метрик.
      - metrics_to_collect: перечень метрик для сбора.
    """
    def __init__(self, simulation, config):
        self.simulation = simulation
        self.collection_interval = config.get("collection_interval", 30)
        self.metrics_to_collect = config.get("metrics_to_collect", ["average_waiting_time", "average_speed", "queue_length", "throughput", "fuel_consumption", "emissions"])
        self.last_collection_time = 0.0
        self.metrics_history = []

    def update(self, current_time):
        """
        Обновляет метрики, если прошёл интервал сбора.
        
        Аргументы:
          current_time (float): Текущее время симуляции.
        """
        if current_time - self.last_collection_time >= self.collection_interval:
            metrics = self.collect_metrics()
            self.metrics_history.append(metrics)
            self.last_collection_time = current_time

    def collect_metrics(self):
        """
        Собирает метрики по транспортным средствам, очередям и светофорам.
        
        Возвращает:
          dict: Собранные метрики с текущим временем.
        """
        vehicle_metrics = self.collect_vehicle_metrics()
        queue_metrics = self.collect_queue_metrics()
        tl_metrics = self.collect_traffic_light_metrics()
        metrics = {**vehicle_metrics, **queue_metrics, **tl_metrics, "time": self.simulation.current_time}
        return metrics

    def collect_vehicle_metrics(self):
        """
        Собирает метрики по транспортным средствам: среднее время ожидания, средняя скорость, throughput.
        
        Возвращает:
          dict: {average_waiting_time, average_speed, throughput}
        """
        vehicles = self.simulation.vehicles
        if not vehicles:
            return {"average_waiting_time": 0, "average_speed": 0, "throughput": 0}
        total_wait = sum(v.waiting_time for v in vehicles)
        total_speed = sum(v.current_speed for v in vehicles)
        avg_wait = total_wait / len(vehicles)
        avg_speed = total_speed / len(vehicles)
        throughput = len(vehicles)
        return {"average_waiting_time": avg_wait, "average_speed": avg_speed, "throughput": throughput}

    def collect_queue_metrics(self):
        """
        Собирает метрики по очередям.
        Stub-реализация – возвращает случайное значение.
        
        Возвращает:
          dict: {queue_length: value}
        """
        import random
        return {"queue_length": random.uniform(5, 20)}

    def collect_traffic_light_metrics(self):
        """
        Собирает метрики по светофорам.
        Stub-реализация – рассчитывает долю зелёных сигналов, если контроллеры присутствуют.
        
        Возвращает:
          dict: {green_ratio: value}
        """
        if self.simulation.controllers:
            total = 0
            green = 0
            for ctrl in self.simulation.controllers:
                states = ctrl.get_traffic_light_states()
                for s in states.values():
                    total += 1
                    if s.upper() == "GREEN":
                        green += 1
            ratio = (green / total * 100) if total > 0 else 0
            return {"green_ratio": ratio}
        return {"green_ratio": 0}

    def calculate_average_waiting_time(self):
        vehicles = self.simulation.vehicles
        return (sum(v.waiting_time for v in vehicles) / len(vehicles)) if vehicles else 0

    def calculate_average_speed(self):
        vehicles = self.simulation.vehicles
        return (sum(v.current_speed for v in vehicles) / len(vehicles)) if vehicles else 0

    def calculate_throughput(self):
        return len(self.simulation.vehicles)

    def calculate_fuel_consumption(self):
        # Stub: возвращает 0
        return 0

    def calculate_emissions(self):
        # Stub: возвращает 0
        return 0

    def get_current_metrics(self):
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}

    def get_metrics_history(self):
        return self.metrics_history

    def export_to_csv(self, filename):
        """
        Экспортирует историю метрик в CSV файл.
        
        Аргументы:
          filename (str): Путь к файлу.
        """
        if not self.metrics_history:
            return
        keys = self.metrics_history[0].keys()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for row in self.metrics_history:
                writer.writerow(row)

    def generate_report(self):
        """
        Генерирует текстовый отчёт с последними метриками.
        
        Возвращает:
          str: Отчёт.
        """
        current = self.get_current_metrics()
        report = "Simulation Metrics Report:\n"
        for key, value in current.items():
            report += f"{key}: {value}\n"
        return report

    def reset(self):
        self.metrics_history = []
        self.last_collection_time = 0.0


def main():
    """
    Демонстрация работы MetricsCollector.
    Создаётся dummy-симулятор с dummy-транспортными средствами, собирается метрика.
    """
    class DummySimulator:
        def __init__(self):
            self.current_time = 0
            self.vehicles = []
            self.controllers = []
    sim = DummySimulator()
    # Добавим dummy-транспортные средства
    for i in range(10):
        from simulation.simulator import DummyVehicle
        veh = DummyVehicle(f"veh_{i}", "car", position=0.0, speed=random.uniform(10, 30))
        veh.waiting_time = random.uniform(0, 100)
        sim.vehicles.append(veh)
    config = {"collection_interval": 10, "metrics_to_collect": ["average_waiting_time", "average_speed", "throughput"]}
    collector = MetricsCollector(sim, config)
    sim.current_time = 10
    collector.update(sim.current_time)
    print("Собранные метрики:", collector.get_current_metrics())

if __name__ == '__main__':
    main()
