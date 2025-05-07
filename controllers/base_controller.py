"""
Файл: controllers/base_controller.py

Описание:
  Абстрактный базовый класс для контроллеров светофоров. Класс определяет
  абстрактные методы:
    - update(time_step): обновление состояния на временном шаге;
    - get_traffic_light_states(): получение текущих состояний светофоров;
    - reset(): сброс контроллера в начальное состояние.
    
  Кроме того, реализованы конкретные методы:
    - __init__(traffic_lights, config): инициализация с набором светофоров и конфигурацией;
    - register_traffic_light(traffic_light): регистрация светофора в контроллере;
    - get_performance_metrics(): сбор метрик эффективности;
    - log_state(logger): логирование текущего состояния.
"""

from abc import ABC, abstractmethod
import logging


class BaseController(ABC):
    def __init__(self, traffic_lights=None, config=None):
        """
        Инициализация базового контроллера.

        Аргументы:
          traffic_lights (list): Список объектов светофоров.
          config (dict): Конфигурация контроллера.
        """
        self.traffic_lights = traffic_lights if traffic_lights is not None else []
        self.config = config
        self.metrics = {}

    def register_traffic_light(self, traffic_light):
        """Регистрирует новый объект светофора."""
        self.traffic_lights.append(traffic_light)

    def get_performance_metrics(self):
        """Возвращает собранные показатели эффективности контроллера."""
        return self.metrics

    def log_state(self, logger):
        """
        Логирует текущие состояния светофоров через переданный logger.
        
        Аргументы:
          logger (logging.Logger): Логгер для вывода информации.
        """
        state_info = self.get_traffic_light_states()
        logger.info("Current Traffic Lights States: " + str(state_info))

    @abstractmethod
    def update(self, time_step):
        """
        Обновление состояния контроллера.
        
        Аргументы:
          time_step (float): Временной интервал обновления.
        """
        pass

    @abstractmethod
    def get_traffic_light_states(self):
        """
        Возвращает текущие состояния всех светофоров.
        
        Возвращает:
          dict: {id светофора: его состояние}.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        Сбрасывает контроллер в начальное состояние.
        """
        pass


def main():
    """
    Демонстрация работы BaseController.
    Создаются фейковые светофоры и контроллер (DummyController),
    производится обновление состояний, логирование и сброс.
    """
    class DummyTrafficLight:
        def __init__(self, id, state="RED"):
            self.id = id
            self.state = state

        def __str__(self):
            return f"DummyTrafficLight({self.id}: {self.state})"

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

    tl1 = DummyTrafficLight("TL1", "RED")
    tl2 = DummyTrafficLight("TL2", "RED")
    dummy_controller = DummyController(traffic_lights=[tl1, tl2], config={"dummy": True})
    logger = logging.getLogger("BaseControllerTest")
    logging.basicConfig(level=logging.INFO)

    print("Начальное состояние:", dummy_controller.get_traffic_light_states())
    dummy_controller.update(1)
    print("После обновления:", dummy_controller.get_traffic_light_states())
    dummy_controller.log_state(logger)
    dummy_controller.reset()
    print("После сброса:", dummy_controller.get_traffic_light_states())


if __name__ == '__main__':
    main()
