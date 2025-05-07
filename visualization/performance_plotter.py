#!/usr/bin/env python
"""
Файл: visualization/performance_plotter.py

Класс PerformancePlotter строит графики и диаграммы по результатам симуляции с использованием Matplotlib и Seaborn.
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class PerformancePlotter:
    def __init__(self, metrics_collector, config):
        """
        Инициализирует построитель графиков.

        Аргументы:
          metrics_collector: объект, предоставляющий историю метрик (метод get_metrics_history()).
          config (dict): конфигурация построителя (figure_size, dpi, style, colors, output_directory).
        """
        self.metrics_collector = metrics_collector
        self.figure_size = tuple(config.get("figure_size", [10, 6]))
        self.dpi = config.get("dpi", 100)
        self.style = config.get("style", "default")
        self.colors = config.get("colors", {"traditional": "#1f77b4", 
                                              "smart": "#ff7f0e", 
                                              "hybrid": "#2ca02c"})
        self.output_directory = config.get("output_directory", "results/plots")
        os.makedirs(self.output_directory, exist_ok=True)
        try:
            plt.style.use(self.style)
        except Exception as e:
            print(f"Style {self.style} не найден, используется default. Ошибка: {e}")

    def plot_waiting_time(self, controller_types):
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        times = np.arange(0, 100, 1)
        for ctrl in controller_types:
            # В реальной реализации данные берутся из метрик; здесь используется stub
            waiting_time = [10 + (i % 10) for i in range(100)]
            plt.plot(times, waiting_time, label=ctrl, color=self.colors.get(ctrl.lower(), "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Average Waiting Time (s)")
        plt.title("Average Waiting Time over Simulation")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_queue_lengths(self, controller_types):
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        times = np.arange(0, 100, 1)
        for ctrl in controller_types:
            queue_lengths = np.random.uniform(5, 20, 100)
            plt.plot(times, queue_lengths, label=ctrl, color=self.colors.get(ctrl.lower(), "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Queue Length")
        plt.title("Queue Length over Simulation")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_throughput(self, controller_types):
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        times = np.arange(0, 100, 1)
        for ctrl in controller_types:
            throughput = np.random.uniform(50, 100, 100)
            plt.plot(times, throughput, label=ctrl, color=self.colors.get(ctrl.lower(), "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Throughput (vehicles)")
        plt.title("Throughput over Simulation")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_fuel_consumption(self, controller_types):
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        times = np.arange(0, 100, 1)
        for ctrl in controller_types:
            fuel = np.random.uniform(0, 10, 100)
            plt.plot(times, fuel, label=ctrl, color=self.colors.get(ctrl.lower(), "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Fuel Consumption")
        plt.title("Fuel Consumption over Simulation")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_emissions(self, controller_types):
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        times = np.arange(0, 100, 1)
        for ctrl in controller_types:
            emissions = np.random.uniform(0, 5, 100)
            plt.plot(times, emissions, label=ctrl, color=self.colors.get(ctrl.lower(), "#000000"))
        plt.xlabel("Time (s)")
        plt.ylabel("Emissions")
        plt.title("Emissions over Simulation")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def plot_comparison_bar_chart(self, metric_name):
        labels = ["Traditional", "Smart", "Hybrid"]
        values = [np.random.uniform(20, 40) for _ in labels]
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.bar(labels, values, color=[self.colors.get(label.lower(), "#000000") for label in labels])
        plt.xlabel("Controller Type")
        plt.ylabel(metric_name)
        plt.title(f"Comparison of {metric_name}")
        plt.tight_layout()
        plt.show()

    def plot_heatmap(self, metric_name):
        data = np.random.rand(10, 10)
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        sns.heatmap(data, annot=True, cmap="viridis")
        plt.title(f"Heatmap of {metric_name}")
        plt.tight_layout()
        plt.show()

    def plot_metrics_history(self, metric_name):
        history = self.metrics_collector.get_metrics_history()
        if not history:
            print("Нет данных для графика истории!")
            return
        times = [entry["time"] for entry in history]
        values = [entry.get(metric_name, 0) for entry in history]
        plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.plot(times, values, marker="o")
        plt.xlabel("Time (s)")
        plt.ylabel(metric_name)
        plt.title(f"History of {metric_name}")
        plt.tight_layout()
        plt.show()

    def create_performance_dashboard(self):
        fig, axs = plt.subplots(2, 2, figsize=self.figure_size, dpi=self.dpi)
        axs[0, 0].plot(range(50), np.random.uniform(0, 20, 50))
        axs[0, 0].set_title("Waiting Time")
        axs[0, 1].plot(range(50), np.random.uniform(5, 25, 50))
        axs[0, 1].set_title("Queue Length")
        axs[1, 0].plot(range(50), np.random.uniform(50, 100, 50))
        axs[1, 0].set_title("Throughput")
        axs[1, 1].plot(range(50), np.random.uniform(0, 10, 50))
        axs[1, 1].set_title("Fuel Consumption")
        plt.tight_layout()
        plt.show()

    def create_pdf_report(self, filename):
        fig = plt.figure(figsize=self.figure_size, dpi=self.dpi)
        plt.text(0.5, 0.5, "Performance Report", fontsize=24, ha="center")
        plt.axis("off")
        self.save_plot(fig, filename)
        plt.close(fig)

    def save_plot(self, figure, filename):
        figure.savefig(filename)
        print(f"Plot saved to {filename}")

    def show_plots(self):
        plt.show()

    def create_animation(self, metric_name, filename):
        import matplotlib.animation as animation
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        history = self.metrics_collector.get_metrics_history()
        times = [entry["time"] for entry in history]
        values = [entry.get(metric_name, 0) for entry in history]
        line, = ax.plot([], [], lw=2)
        if times:
            ax.set_xlim(0, max(times))
            ax.set_ylim(min(values), max(values))
        else:
            ax.set_xlim(0, 100)
            ax.set_ylim(0, 10)
        def init():
            line.set_data([], [])
            return (line,)
        def animate(i):
            x = times[:i]
            y = values[:i]
            line.set_data(x, y)
            return (line,)
        ani = animation.FuncAnimation(fig, animate, init_func=init, frames=len(times), interval=200, blit=True)
        ani.save(filename, writer='imagemagick')
        plt.close(fig)

def main():
    # Dummy-сборщик метрик для теста
    class DummyMetricsCollector:
        def __init__(self):
            self.history = [{"time": t, "average_waiting_time": np.random.uniform(10, 30)} for t in range(0, 300, 30)]
        def get_metrics_history(self):
            return self.history

    dummy_collector = DummyMetricsCollector()
    config = {
        "figure_size": [10, 6],
        "dpi": 100,
        "style": "default",
        "colors": {"traditional": "#1f77b4", "smart": "#ff7f0e", "hybrid": "#2ca02c"},
        "output_directory": "results/plots"
    }
    plotter = PerformancePlotter(dummy_collector, config)
    plotter.plot_waiting_time(["Traditional", "Smart"])
    plotter.plot_comparison_bar_chart("Average Waiting Time")
    plotter.create_performance_dashboard()
    plotter.create_pdf_report("results/plot_report.pdf")
    print("Performance plots demonstration completed.")

if __name__ == "__main__":
    main()
