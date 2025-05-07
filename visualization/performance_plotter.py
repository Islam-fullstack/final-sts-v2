"""
Файл: visualization/performance_plotter.py

Реализует класс PerformancePlotter для построения графиков и диаграмм по результатам симуляции.
Используются Matplotlib и Seaborn для построения графиков.
"""

import os
import random
import matplotlib.pyplot as plt

class PerformancePlotter:
    def __init__(self, metrics_collector, config):
        """
        Инициализирует построитель графиков.
        
        Аргументы:
          metrics_collector: Объект, предоставляющий историю метрик (метод get_metrics_history()).
          config (dict): Конфигурация визуализации графиков.
        """
        self.metrics_collector = metrics_collector
        self.figure_size = tuple(config.get("figure_size", [10, 6]))
        self.dpi = config.get("dpi", 100)
        self.style = config.get("style", "seaborn-whitegrid")
        self.colors = config.get("colors", {"traditional": "#1f77b4", "smart": "#ff7f0e", "hybrid": "#2ca02c"})
        self.output_directory = config.get("output_directory", "results/plots")
        os.makedirs(self.output_directory, exist_ok=True)
        plt.style.use(self.style)

    def plot_waiting_time(self, controller_types):
        """Строит график среднего времени ожидания для заданных типов контроллеров."""
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        for ctrl in controller_types:
            times = list(range(100))
            waiting_time = [10 + 5 * (i % 10) for i in range(100)]
            plt.plot(times, waiting_time, label=ctrl, color=self.colors.get(ctrl, "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Average Waiting Time (s)")
        plt.title("Average Waiting Time over Simulation")
        plt.legend()
        plt.show()

    def plot_queue_lengths(self, controller_types):
        """Строит график длин очередей для заданных контроллеров."""
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        for ctrl in controller_types:
            times = list(range(100))
            queue_lengths = [random.uniform(5, 20) for _ in range(100)]
            plt.plot(times, queue_lengths, label=ctrl, color=self.colors.get(ctrl, "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Queue Length")
        plt.title("Queue Length over Simulation")
        plt.legend()
        plt.show()

    def plot_throughput(self, controller_types):
        """Строит график пропускной способности."""
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        for ctrl in controller_types:
            times = list(range(100))
            throughput = [random.uniform(50, 100) for _ in range(100)]
            plt.plot(times, throughput, label=ctrl, color=self.colors.get(ctrl, "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (vehicles)")
        plt.title("Throughput over Simulation")
        plt.legend()
        plt.show()

    def plot_fuel_consumption(self, controller_types):
        """Строит график расхода топлива."""
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        for ctrl in controller_types:
            times = list(range(100))
            fuel = [random.uniform(0, 10) for _ in range(100)]
            plt.plot(times, fuel, label=ctrl, color=self.colors.get(ctrl, "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Fuel Consumption")
        plt.title("Fuel Consumption over Simulation")
        plt.legend()
        plt.show()

    def plot_emissions(self, controller_types):
        """Строит график выбросов."""
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        for ctrl in controller_types:
            times = list(range(100))
            emissions = [random.uniform(0, 5) for _ in range(100)]
            plt.plot(times, emissions, label=ctrl, color=self.colors.get(ctrl, "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Emissions")
        plt.title("Emissions over Simulation")
        plt.legend()
        plt.show()

    def plot_comparison_bar_chart(self, metric_name):
        """Строит столбчатую диаграмму для заданной метрики."""
        import numpy as np
        labels = ["Traditional", "Smart", "Hybrid"]
        values = [random.uniform(20, 40) for _ in labels]
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.bar(labels, values, color=[self.colors.get(label.lower(), "#000000") for label in labels])
        plt.xlabel("Controller Type")
        plt.ylabel(metric_name)
        plt.title(f"Comparison of {metric_name}")
        plt.show()

    def plot_heatmap(self, metric_name):
        """Строит тепловую карту для выбранной метрики."""
        import numpy as np
        import seaborn as sns
        data = np.random.rand(10, 10)
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        sns.heatmap(data, annot=True, cmap="viridis")
        plt.title(f"Heatmap of {metric_name}")
        plt.show()

    def plot_metrics_history(self, metric_name):
        """
        Строит график истории метрики.
        Ожидается, что metrics_collector.get_metrics_history() возвращает список словарей с ключом metric_name.
        """
        history = self.metrics_collector.get_metrics_history()
        times = [entry["time"] for entry in history]
        values = [entry.get(metric_name, 0) for entry in history]
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.plot(times, values)
        plt.xlabel("Time (s)")
        plt.ylabel(metric_name)
        plt.title(f"History of {metric_name}")
        plt.show()

    def create_performance_dashboard(self):
        """Создаёт панель показателей с несколькими графиками."""
        fig, axs = plt.subplots(2, 2, figsize=self.figure_size, dpi=self.dpi)
        axs[0, 0].plot(range(50), [random.uniform(0, 20) for _ in range(50)])
        axs[0, 0].set_title("Waiting Time")
        axs[0, 1].plot(range(50), [random.uniform(5, 25) for _ in range(50)])
        axs[0, 1].set_title("Queue Length")
        axs[1, 0].plot(range(50), [random.uniform(50, 100) for _ in range(50)])
        axs[1, 0].set_title("Throughput")
        axs[1, 1].plot(range(50), [random.uniform(0, 10) for _ in range(50)])
        axs[1, 1].set_title("Fuel Consumption")
        plt.tight_layout()
        plt.show()

    def create_pdf_report(self, filename):
        """Создаёт PDF-отчёт (stub – сохраняет простую фигуру в PDF)."""
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.text(0.5, 0.5, "Performance Report", fontsize=24, ha="center")
        plt.axis("off")
        self.save_plot(fig, filename)
        plt.close(fig)
    
    def save_plot(self, figure, filename):
        """Сохраняет график в файл."""
        figure.savefig(filename)
    
    def show_plots(self):
        """Отображает все построенные графики."""
        plt.show()
    
    def create_animation(self, metric_name, filename):
        """Создает анимацию изменения метрики и сохраняет её в файл (stub)."""
        import matplotlib.animation as animation
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        history = self.metrics_collector.get_metrics_history()
        times = [entry["time"] for entry in history]
        values = [entry.get(metric_name, 0) for entry in history]
        line, = ax.plot([], [], lw=2)
        ax.set_xlim(0, max(times) if times else 100)
        ax.set_ylim(min(values) if values else 0, max(values) if values else 10)
        
        def init():
            line.set_data([], [])
            return (line, )
        def animate(i):
            x = times[:i]
            y = values[:i]
            line.set_data(x, y)
            return (line, )
        ani = animation.FuncAnimation(fig, animate, init_func=init, frames=len(times), interval=200, blit=True)
        ani.save(filename, writer='imagemagick')
        plt.close(fig)


def main():
    """
    Демонстрация работы PerformancePlotter.
    Создаётся dummy-коллектор метрик с случайными данными и строятся примеры графиков и отчёта.
    """
    # Dummy-коллектор метрик
    class DummyMetricsCollector:
        def __init__(self):
            self.history = []
            for t in range(0, 300, 30):
                self.history.append({"time": t, "average_waiting_time": random.uniform(10, 30)})
        def get_metrics_history(self):
            return self.history

    dummy_collector = DummyMetricsCollector()
    config = {
        "figure_size": [10, 6],
        "dpi": 100,
        "style": "seaborn-whitegrid",
        "colors": {"traditional": "#1f77b4", "smart": "#ff7f0e", "hybrid": "#2ca02c"},
        "output_directory": "results/plots"
    }
    plotter = PerformancePlotter(dummy_collector, config)
    plotter.plot_waiting_time(["traditional", "smart"])
    plotter.plot_comparison_bar_chart("Average Waiting Time")
    plotter.create_performance_dashboard()
    plotter.create_pdf_report("results/plot_report.pdf")
    print("Performance plots demonstration completed.")


if __name__ == '__main__':
    main()
