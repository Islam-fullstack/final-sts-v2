#!/usr/bin/env python
"""
Файл: controllers/base_controller.py

Абстрактный базовый класс контроллера светофоров.

Абстрактные методы:
  - update(time_step): обновление состояния на временном шаге.
  - get_traffic_light_states(): получение текущих состояний светофоров.
  - reset(): сброс контроллера в начальное состояние.
  
Конкретные методы:
  - __init__(traffic_lights, config): инициализация контроллера.
  - register_traffic_light(traffic_light): регистрация светофора.
  - get_performance_metrics(): сбор метрик эффективности.
  - log_state(logger): логирование текущего состояния.
"""

from abc import ABC, abstractmethod

class BaseController(ABC):
    def __init__(self, traffic_lights=None, config=None):
        self.traffic_lights = traffic_lights if traffic_lights is not None else []
        self.config = config or {}
        self.metrics = {}
    
    def register_traffic_light(self, traffic_light):
        self.traffic_lights.append(traffic_light)
    
    def get_performance_metrics(self):
        return self.metrics
    
    def log_state(self, logger):
        state_info = self.get_traffic_light_states()
        logger.info("Current Traffic Light States: " + str(state_info))
    
    @abstractmethod
    def update(self, time_step):
        pass
    
    @abstractmethod
    def get_traffic_light_states(self):
        pass
    
    @abstractmethod
    def reset(self):
        pass

if __name__ == "__main__":
    # Простейшая демонстрация базового контроллера (Dummy пример)
    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state

    class DummyController(BaseController):
        def update(self, time_step):
            for tl in self.traffic_lights:
                tl.state = "GREEN" if tl.state == "RED" else "RED"
            self.metrics['updates'] = self.metrics.get('updates', 0) + 1

        def get_traffic_light_states(self):
            return {tl.id: tl.state for tl in self.traffic_lights}

        def reset(self):
            for tl in self.traffic_lights:
                tl.state = "RED"
            self.metrics = {}
    
    tl1 = DummyTrafficLight("TL1")
    tl2 = DummyTrafficLight("TL2")
    ctrl = DummyController([tl1, tl2], config={"dummy": True})
    print("Initial states:", ctrl.get_traffic_light_states())
    ctrl.update(1)
    print("After update:", ctrl.get_traffic_light_states())
    ctrl.reset()
    print("After reset:", ctrl.get_traffic_light_states())
