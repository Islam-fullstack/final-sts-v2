#!/usr/bin/env python
"""
Файл: visualization/traffic_visualizer.py

Класс TrafficVisualizer организует графическую визуализацию симуляции с использованием Pygame.
Он:
  - Инициализирует окно с заданными размерами и масштабом.
  - Отрисовывает фон, сетку, дороги, перекрестки, светофоры, транспортные средства, очереди, метрики, время и легенду.
  - Обрабатывает события пользователя (нажатия клавиш для управления камерой, масштабированием, паузой и прочее).
  - Запускает основной цикл визуализации.
"""

import sys
import pygame

class TrafficVisualizer:
    def __init__(self, simulation, config):
        """
        Инициализирует визуализатор.
        
        Аргументы:
          simulation: объект симулятора (должен иметь метод get_traffic_state()).
          config (dict): Конфигурация визуализации.
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
        self.colors = {}
        # Цвета: если не заданы, используются дефолтные значения
        self.colors["background"] = config.get("background_color", [240, 240, 240])
        self.colors["grid"] = config.get("grid_color", [200, 200, 200])
        colors_cfg = config.get("colors", {})
        self.colors["road"] = colors_cfg.get("road", [100, 100, 100])
        self.colors["lane_marking"] = colors_cfg.get("lane_marking", [255, 255, 255])
        self.colors["car"] = colors_cfg.get("car", [0, 0, 255])
        self.colors["bus"] = colors_cfg.get("bus", [0, 200, 0])
        self.colors["truck"] = colors_cfg.get("truck", [255, 100, 0])
        self.colors["motorcycle"] = colors_cfg.get("motorcycle", [255, 0, 0])
        self.colors["traffic_light_red"] = colors_cfg.get("traffic_light_red", [255, 0, 0])
        self.colors["traffic_light_yellow"] = colors_cfg.get("traffic_light_yellow", [255, 255, 0])
        self.colors["traffic_light_green"] = colors_cfg.get("traffic_light_green", [0, 255, 0])
        # Инициализация интерфейса
        pygame.init()
        self.display_surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Traffic Simulation Visualization")
        # Используем настройки шрифта из конфигурации UI
        ui_cfg = config.get("ui", {})
        font_name = ui_cfg.get("font", "Arial")
        font_size = ui_cfg.get("font_size", 14)
        self.font = pygame.font.SysFont(font_name, font_size)
        self.clock = pygame.time.Clock()

    def world_to_screen(self, pos):
        cam_x, cam_y = self.camera_position
        x = (pos[0] - cam_x) * self.zoom_level * self.scale + self.width // 2
        y = (pos[1] - cam_y) * self.zoom_level * self.scale + self.height // 2
        return (int(x), int(y))

    def draw_background(self):
        self.display_surface.fill(self.colors["background"])

    def draw_grid(self):
        if not self.show_grid:
            return
        gap = int(50 * self.zoom_level * self.scale)
        for x in range(0, self.width, gap):
            pygame.draw.line(self.display_surface, self.colors["grid"], (x, 0), (x, self.height))
        for y in range(0, self.height, gap):
            pygame.draw.line(self.display_surface, self.colors["grid"], (0, y), (self.width, y))

    def draw_roads(self):
        for road in self.simulation.roads:
            start = self.world_to_screen(road.start)
            end = self.world_to_screen(road.end)
            pygame.draw.line(self.display_surface, self.colors["road"], start, end, 5)

    def draw_intersections(self):
        for inter in self.simulation.intersections:
            pos = self.world_to_screen(inter.position)
            pygame.draw.circle(self.display_surface, (150, 150, 150), pos, 10)

    def draw_traffic_lights(self):
        # Для демонстрации: выводим прямоугольники в середине каждого дороги
        for road in self.simulation.roads:
            mid = ((road.start[0] + road.end[0]) / 2, (road.start[1] + road.end[1]) / 2)
            pos = self.world_to_screen(mid)
            # stub: случайное состояние, можно заменить на реальные данные
            state = "GREEN" if random.choice([True, False]) else "RED"
            color = self.colors["traffic_light_green"] if state.upper() == "GREEN" else self.colors["traffic_light_red"]
            pygame.draw.rect(self.display_surface, color, (pos[0], pos[1], 10, 20))
    
    def draw_vehicles(self):
        for veh in self.simulation.vehicles:
            # Здесь используем значение veh.position для обеих координат (stub)
            pos = self.world_to_screen((veh.position, veh.position))
            color = self.colors.get(veh.vehicle_type.lower(), (0, 0, 0))
            pygame.draw.circle(self.display_surface, color, pos, 5)

    def draw_queues(self):
        # Stub: рисуем текст возле перекрёстков с случайным числом
        for inter in self.simulation.intersections:
            text = self.font.render("Queue: " + str(random.randint(0, 20)), True, (0, 0, 0))
            pos = self.world_to_screen(inter.position)
            self.display_surface.blit(text, pos)

    def draw_metrics(self):
        if not self.show_metrics:
            return
        metrics = self.simulation.get_traffic_state()
        text = f"Time: {metrics.get('time', 0):.1f}s  Vehicles: {metrics.get('vehicles', 0)}"
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.display_surface.blit(text_surface, (10, 10))

    def draw_simulation_time(self):
        metrics = self.simulation.get_traffic_state()
        text_surface = self.font.render(f"Sim Time: {metrics.get('time', 0):.1f}s", True, (0, 0, 0))
        self.display_surface.blit(text_surface, (10, 30))

    def draw_legend(self):
        legend = ["Car: Blue", "Bus: Green", "Truck: Orange", "Motorcycle: Red"]
        for i, line in enumerate(legend):
            text_surface = self.font.render(line, True, (0, 0, 0))
            self.display_surface.blit(text_surface, (self.width - 150, 10 + i * 20))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.pause = not self.pause
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
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
        self.handle_events()
        # Обновляем камеру, если требуется

    def render(self):
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
        while True:
            dt = self.clock.tick(self.fps) / 1000.0 * self.speed_factor
            self.update(dt)
            self.render()

    def save_screenshot(self, filename):
        pygame.image.save(self.display_surface, filename)

    def toggle_metrics_display(self):
        self.show_metrics = not self.show_metrics

    def zoom_in(self):
        self.zoom_level *= 1.1

    def zoom_out(self):
        self.zoom_level /= 1.1

    def move_camera(self, dx, dy):
        x, y = self.camera_position
        self.camera_position = (x + dx, y + dy)

    def change_simulation_speed(self, factor):
        self.speed_factor = factor

def main():
    # Dummy симуляция для демонстрации визуализатора
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
            self.roads = [DummyRoad((-100, 0), (100, 0))]
            self.intersections = [DummyIntersection((0, 0))]
            self.vehicles = []
            for i in range(10):
                pos = (random.uniform(-100, 100))
                v_type = random.choice(["car", "bus", "truck", "motorcycle"])
                self.vehicles.append(DummyVehicle(pos, v_type))
        def get_traffic_state(self):
            return {"time": self.current_time, "vehicles": len(self.vehicles), "avg_speed": 20}

    import random
    sim = DummySimulation()
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
        "ui": {"font": "Arial", "font_size": 14},
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

if __name__ == "__main__":
    main()
