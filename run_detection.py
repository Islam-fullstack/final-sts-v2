#!/usr/bin/env python
"""
run_detection.py

Скрипт для обработки видео и обнаружения транспорта.
Функциональность:
  - Инициализация детектора транспорта.
  - Загрузка и обработка видеофайла (или потока с камеры).
  - Обнаружение и подсчет транспортных средств.
  - Визуализация результатов.
  - Сохранение статистики транспортного потока.
  - Опциональная интеграция с контроллером светофоров.
"""

import argparse
import yaml
from detection.detection_manager import DetectionManager

def main():
    parser = argparse.ArgumentParser(description="Run Traffic Detection")
    parser.add_argument("--video", required=True, help="Путь к видеофайлу или ID камеры")
    parser.add_argument("--output", help="Путь для сохранения обработанного видео")
    args = parser.parse_args()

    # Базовая конфигурация для детектора (stub)
    detection_config = {"skip_frames": 1, "resize_dim": (640, 480), "device": "cpu"}
    detector = DetectionManager(video_source=args.video,
                                output_path=args.output,
                                skip_frames=detection_config["skip_frames"],
                                resize_dim=detection_config["resize_dim"],
                                device=detection_config["device"])
    detector.process_stream()

if __name__ == "__main__":
    main()
