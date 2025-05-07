"""
Файл: visualization/traffic_visualizer.py

Реализует класс TrafficVisualizer для графического отображения симуляции.
Ключевые возможности:
  - Инициализация графического окна с заданными параметрами из конфигурации.
  - Отрисовка фона, сетки, дорог, перекрёстков, светофоров, транспортных средств, очередей.
  - Отображение метрик симуляции, времени, легенды.
  - Обработка пользовательского ввода (паузу, масштабирование, перемещение камеры, сохранение скриншотов).
  - Запуск основного цикла визуализации с контролем FPS.
"""

import sys
import random
import pygame


class TrafficVisualizer:
    def __init__(self, simulation, config):
        """
        Инициализация визуализатора.
        
        Аргументы:
          simulation (object): Объект симуляции (должен реализовывать метод get_traffic_state()).
          config (dict): Конфигурация визуализации, содержащая размеры окна, настройки камеры, цвета, интерфейс и т.д.
        """
        self.simulation = simulation
        self.width = config.get("window_width", 1280)
        self.height = config.get("window_height", 720)
        self.fps = config.get("fps", 60)
        self.scale = config.get("scale", 2)
        self.show_metrics = config.get("show_metrics", True)
        self.show_grid = config.get("show_grid", True)
        self.camera_position = tuple(config.get("camera", {}).get("initial_position", [0, 0]))
        self.zoom_level = config.get("camera", {}).get("initial_zoom", 1.0)
        self.pause = False
        self.speed_factor = 1.0

        # Цветовая схема: приоритетно берём основной набор из config, если отсутствует – значения по умолчанию.
        self.colors = {}
        self.colors["background"] = config.get("background_color", [240, 240, 240])
        self.colors["grid"] = config.get("grid_color", [200, 200, 200])
        cconf = config.get("colors", {})
        self.colors["road"] = cconf.get("road", [100, 100, 100])
        self.colors["lane_marking"] = cconf.get("lane_marking", [255, 255, 255])
        self.colors["car"] = cconf.get("car", [0, 0, 255])
        self.colors["bus"] = cconf.get("bus", [0, 200, 0])
        self.colors["truck"] = cconf.get("truck", [255, 100, 0])
        self.colors["motorcycle"] = cconf.get("motorcycle", [255, 0, 0])
        self.colors["traffic_light_red"] = cconf.get("traffic_light_red", [255, 0, 0])
        self.colors["traffic_light_yellow"] = cconf.get("traffic_light_yellow", [255, 255, 0])
        self.colors["traffic_light_green"] = cconf.get("traffic_light_green", [0, 255, 0])

        # Инициализация модуля визуализации Pygame
        self.display_surface = None
        self.clock = pygame.time.Clock()
        self.font = None
        self.initialize_display()

    def initialize_display(self):
        """Инициализирует окно визуализации, шрифт и заголовок окна."""
        pygame.init()
        self.display_surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Traffic Simulation Visualization")
        self.font = pygame.font.SysFont(config.get("ui", {}).get("font", "Arial"),
                                         config.get("ui", {}).get("font_size", 14))

    def draw_background(self):
        """Отрисовывает фон."""
        self.display_surface.fill(self.colors["background"])

    def draw_grid(self):
        """Отрисовывает координатную сетку (если включена)."""
        if not self.show_grid:
            return
        grid_color = self.colors["grid"]
        gap = int(50 * self.zoom_level * self.scale)
        for x in range(0, self.width, gap):
            pygame.draw.line(self.display_surface, grid_color, (x, 0), (x, self.height))
        for y in range(0, self.height, gap):
            pygame.draw.line(self.display_surface, grid_color, (0, y), (self.width, y))

    def draw_roads(self):
        """
        Отрисовывает дороги из симуляции.
        Здесь roads предполагается как список объектов, у которых есть атрибуты start и end (кортежи координат).
        """
        for road in self.simulation.roads:
            start = self.world_to_screen(road.start)
            end = self.world_to_screen(road.end)
            pygame.draw.line(self.display_surface, self.colors["road"], start, end, 5)

    def draw_intersections(self):
        """Отрисовывает перекрёстки (выводит их в виде кругов)."""
        for inter in self.simulation.intersections:
            pos = self.world_to_screen(inter.position)
            pygame.draw.circle(self.display_surface, (150, 150, 150), pos, 10)

    def draw_traffic_lights(self):
        """
        Отрисовывает светофоры.
        Для демонстрации каждая дорога получает один светофор, отрисовываемый как прямоугольник с цветом, зависящим от состояния.
        Здесь используется stub-логика для определения состояния.
        """
        for road in self.simulation.roads:
            mid = ((road.start[0] + road.end[0]) / 2, (road.start[1] + road.end[1]) / 2)
            pos = self.world_to_screen(mid)
            state = random.choice(["RED", "YELLOW", "GREEN"])
            if state == "RED":
                color = self.colors["traffic_light_red"]
            elif state == "YELLOW":
                color = self.colors["traffic_light_yellow"]
            else:
                color = self.colors["traffic_light_green"]
            pygame.draw.rect(self.display_surface, color, (pos[0], pos[1], 10, 20))

    def draw_vehicles(self):
        """
        Отрисовывает транспортные средства.
        Каждый объект автомобиля должен иметь атрибут vehicle_type и позицию (для демонстрации используем его как координаты).
        """
        for veh in self.simulation.vehicles:
            # В данном примере для упрощения использует координату vehicle.position для обоих осей
            pos = self.world_to_screen((veh.position, veh.position))
            color = self.colors.get(veh.vehicle_type, (0, 0, 0))
            pygame.draw.circle(self.display_surface, color, pos, 5)

    def draw_queues(self):
        """Отрисовывает очереди – stub: выводит текст с случайным числом возле каждого перекрёстка."""
        for inter in self.simulation.intersections:
            text = self.font.render("Queue: {}".format(random.randint(0, 20)), True, (0, 0, 0))
            pos = self.world_to_screen(inter.position)
            self.display_surface.blit(text, pos)

    def draw_metrics(self):
        """Отрисовывает текущие метрики (например, время симуляции, количество автомобилей)."""
        if not self.show_metrics:
            return
        metrics = self.simulation.get_traffic_state()
        text = f"Time: {metrics.get('time', 0):.1f}s  Vehicles: {metrics.get('vehicles', 0)}"
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.display_surface.blit(text_surface, (10, 10))

    def draw_simulation_time(self):
        """Отрисовывает время симуляции отдельно (можно объединить с метриками)."""
        metrics = self.simulation.get_traffic_state()
        text_surface = self.font.render(f"Sim Time: {metrics.get('time', 0):.1f}s", True, (0, 0, 0))
        self.display_surface.blit(text_surface, (10, 30))

    def draw_legend(self):
        """Отрисовывает легенду для отображения цветов объектов."""
        legend = ["Car: Blue", "Bus: Green", "Truck: Orange", "Motorcycle: Red"]
        for i, line in enumerate(legend):
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.display_surface.blit(text_surface, (self.width - 150, 10 + i * 20))

    def handle_events(self):
        """Обрабатывает события пользователя: нажатия клавиш для управления камерой, пауза, масштаб и т.д."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause_simulation()
                elif event.key == pygame.K_m:
                    self.toggle_metrics_display()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    self.zoom_in()
                elif event.key == pygame.K_MINUS:
                    self.zoom_out()
                elif event.key == pygame.K_UP:
                    self.move_camera(0, -10)
                elif event.key == pygame.K_DOWN:
                    self.move_camera(0, 10)
                elif event.key == pygame.K_LEFT:
                    self.move_camera(-10, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_camera(10, 0)
                elif event.key == pygame.K_s:
                    self.save_screenshot("screenshot.png")
                elif event.key == pygame.K_SPACE:
                    self.change_simulation_speed(2.0)

    def update(self, dt):
        """Обновляет состояние визуализации (обработка ввода и динамики камеры)."""
        self.handle_events()
        # Можно добавить логику обновления камеры здесь

    def render(self):
        """Отрисовывает текущий кадр с фоном, объектами, метриками и легендой."""
        self.draw_background()
        self.draw_grid()
        self.draw_roads()
        self.draw_intersections()
        self.draw_traffic_lights()
        self.draw_vehicles()
        self.draw_queues()
        self.draw_metrics()
        self.draw_simulation_time()
        self.draw_legend()
        pygame.display.update()

    def run(self):
        """Запускает основной цикл визуализации."""
        while True:
            dt = self.clock.tick(self.fps) / 1000.0 * self.speed_factor
            self.update(dt)
            self.render()

    def save_screenshot(self, filename):
        """Сохраняет текущий кадр в файл."""
        pygame.image.save(self.display_surface, filename)

    def toggle_metrics_display(self):
        """Переключает отображение метрик."""
        self.show_metrics = not self.show_metrics

    def zoom_in(self):
        """Увеличивает масштаб камеры."""
        self.zoom_level *= 1.1

    def zoom_out(self):
        """Уменьшает масштаб камеры."""
        self.zoom_level /= 1.1

    def move_camera(self, dx, dy):
        """Перемещает камеру на заданное смещение."""
        x, y = self.camera_position
        self.camera_position = (x + dx, y + dy)

    def pause_simulation(self):
        """Переключает режим паузы симуляции."""
        self.pause = not self.pause

    def change_simulation_speed(self, factor):
        """Изменяет коэффициент ускорения симуляции."""
        self.speed_factor = factor

    def world_to_screen(self, pos):
        """
        Преобразует мировые координаты в экранные с учетом позиции камеры и масштаба.
        
        Аргументы:
          pos (tuple): (x, y) в мировых координатах.
        Возвращает:
          tuple: (x, y) на экране.
        """
        cam_x, cam_y = self.camera_position
        x = (pos[0] - cam_x) * self.zoom_level * self.scale + self.width // 2
        y = (pos[1] - cam_y) * self.zoom_level * self.scale + self.height // 2
        return (int(x), int(y))


def main():
    """
    Демонстрирует работу TrafficVisualizer.
    Для демонстрации создаётся dummy-симуляция с простыми объектами (дороги, перекрёстки, ТС).
    """
    # Определим dummy-объекты для симуляции
    class DummyRoad:
        def __init__(self, start, end):
            self.start = start
            self.end = end

    class DummyIntersection:
        def __init__(self, position):
            self.position = position

    class DummyVehicle:
        def __init__(self, position, vehicle_type):
            self.position = position
            self.vehicle_type = vehicle_type

    class DummySimulation:
        def __init__(self):
            self.current_time = 0.0
            # Простейшая дорога горизонтально
            self.roads = [DummyRoad((-100, 0), (100, 0))]
            self.intersections = [DummyIntersection((0, 0))]
            # Сгенерируем несколько dummy-ТС с случайным положением
            self.vehicles = []
            for i in range(10):
                pos = random.uniform(-100, 100)
                veh_type = random.choice(["car", "bus", "truck", "motorcycle"])
                self.vehicles.append(DummyVehicle(pos, veh_type))
        def get_traffic_state(self):
            return {"time": self.current_time, "vehicles": len(self.vehicles), "avg_speed": 20}

    sim = DummySimulation()
    
    # Пример конфигурации для визуализации
    config = {
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
    visualizer = TrafficVisualizer(sim, config)
    visualizer.run()


if __name__ == '__main__':
    main()
