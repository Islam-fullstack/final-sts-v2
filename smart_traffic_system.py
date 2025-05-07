#!/usr/bin/env python
"""
smart_traffic_system.py

Класс SmartTrafficSystem для управления всей системой умных светофоров.
Атрибуты:
  - config: Конфигурация системы.
  - simulator: Экземпляр симулятора.
  - detector: Детектор транспорта.
  - controllers: Словарь контроллеров (традиционный, умный и т.д.).
  - visualizer: Визуализатор.
  - metrics_collector: Коллектор метрик.
  - logger: Логгер системы.
  - status: Текущий статус системы.
  
Методы:
  - __init__(config) - инициализация.
  - initialize_components() - инициализация всех компонентов.
  - start() - запуск системы.
  - stop() - остановка системы.
  - pause(), resume() - пауза и возобновление.
  - switch_controller(controller_type) - переключение контроллера.
  - collect_metrics() - сбор метрик.
  - save_state(filename) - сохранение состояния системы.
  - load_state(filename) - загрузка состояния системы.
  - run_simulation(duration) - запуск симуляции.
  - run_visualization() - запуск визуализации.
  - run_detection(video_source) - запуск детекции.
  - run_comparison(controller_types) - запуск сравнения.
  - generate_report() - генерация отчета.
"""

import os
import yaml
from utils.logger import Logger
from simulation.simulator import TrafficSimulator
from detection.detection_manager import DetectionManager
from visualization.traffic_visualizer import TrafficVisualizer
# Импорт других необходимых модулей можно расширить по необходимости

class SmartTrafficSystem:
    def __init__(self, config):
        self.config = config
        self.simulator = None
        self.detector = None
        self.controllers = {}
        self.visualizer = None
        self.metrics_collector = None
        self.logger = Logger.get_logger("SmartTrafficSystem")
        self.status = "initialized"

    def initialize_components(self, controller_type="smart", load_gui=True):
        # Инициализация симулятора
        from simulation.simulator import TrafficSimulator
        self.simulator = TrafficSimulator(self.config)
        self.simulator.setup_environment()
        self.simulator.setup_controllers()  # контроллеры выбираются внутри симулятора
        self.simulator.setup_traffic_generators()
        self.simulator.setup_metrics_collector()
        
        # Инициализация детектора
        from detection.detection_manager import DetectionManager
        self.detector = DetectionManager(video_source=self.config.get("video_source", 0),
                                         output_path=self.config.get("detection_output", None),
                                         skip_frames=1,
                                         resize_dim=(640, 480),
                                         device="cpu")
        
        # Инициализация визуализатора, если GUI разрешен
        if load_gui:
            from visualization.traffic_visualizer import TrafficVisualizer
            vis_config = self.config.get("visualization", {})
            self.visualizer = TrafficVisualizer(self.simulator, vis_config)
        
        self.status = "components_initialized"
        self.logger.info("Все компоненты системы инициализированы.")

    def start(self):
        mode = self.config.get("mode", "simulation")
        self.logger.info(f"Запуск системы в режиме {mode}.")
        if mode == "simulation":
            duration = self.config.get("simulation", {}).get("duration", 3600)
            self.run_simulation(duration)
        elif mode == "visualization":
            self.run_visualization()
        elif mode == "detection":
            video_source = self.config.get("video_source", 0)
            self.run_detection(video_source)
        elif mode == "comparison":
            ctrl_type = self.config.get("controller", "smart")
            self.run_comparison(ctrl_type)
        else:
            self.logger.error("Неизвестный режим работы.")
        self.status = "running"

    def stop(self):
        self.status = "stopped"
        self.logger.info("Система остановлена.")

    def pause(self):
        if self.simulator:
            self.simulator.pause = True
        self.status = "paused"
        self.logger.info("Система приостановлена.")

    def resume(self):
        if self.simulator:
            self.simulator.pause = False
        self.status = "running"
        self.logger.info("Система возобновлена.")

    def switch_controller(self, controller_type):
        self.config["controller"] = controller_type
        self.logger.info(f"Переключение на контроллер {controller_type}.")

    def collect_metrics(self):
        if self.simulator and self.simulator.metrics_collector:
            return self.simulator.metrics_collector.get_current_metrics()
        return {}

    def save_state(self, filename):
        if self.simulator:
            self.simulator.save_state(filename)
            self.logger.info(f"Состояние системы сохранено в {filename}")

    def load_state(self, filename):
        if self.simulator:
            self.simulator.load_state(filename)
            self.logger.info(f"Состояние системы загружено из {filename}")

    def run_simulation(self, duration):
        if self.simulator:
            self.simulator.run(duration)

    def run_visualization(self):
        if self.visualizer:
            self.visualizer.run()

    def run_detection(self, video_source):
        from run_detection import main as detection_main
        detection_main()

    def run_comparison(self, controller_types):
        from run_comparison import main as comparison_main
        comparison_main()

    def generate_report(self):
        metrics = self.collect_metrics()
        report = "Final Report:\n"
        for k, v in metrics.items():
            report += f"{k}: {v}\n"
        self.logger.info(report)
        print(report)

if __name__ == "__main__":
    # Пример автономного запуска системы с базовой конфигурацией
    default_config = {
        "mode": "simulation",
        "controller": "smart",
        "simulation": {"duration": 600},
        "video_source": 0,
        "visualization": {
            "window_width": 1280,
            "window_height": 720,
            "fps": 60,
            "scale": 2,
            "background_color": [240, 240, 240],
            "grid_color": [200, 200, 200],
            "show_metrics": True,
            "show_grid": True,
            "camera": {"initial_position": [0, 0], "initial_zoom": 1.0},
            "colors": {
                "road": [100, 100, 100],
                "lane_marking": [255, 255, 255],
                "car": [0, 0, 255],
                "bus": [0, 200, 0],
                "truck": [255, 100, 0],
                "motorcycle": [255, 0, 0],
                "traffic_light_red": [255, 0, 0],
                "traffic_light_yellow": [255, 255, 0],
                "traffic_light_green": [0, 255, 0]
            }
        }
    }
    system = SmartTrafficSystem(default_config)
    system.initialize_components()
    system.start()
