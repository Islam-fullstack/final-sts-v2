#!/usr/bin/env python
"""
Файл: detection/detection_manager.py

Класс DetectionManager объединяет VideoProcessor и VehicleDetector для потоковой обработки видеопотока.
Он:
  - Обрабатывает каждый кадр (с возможной параллельной детекцией).
  - Рисует bounding box и метки на кадре.
  - Подсчитывает транспорт в заданных зонах интереса.
  - Сохраняет и загружает состояние (например, треки и статистику).
"""

import cv2
import pickle
from concurrent.futures import ThreadPoolExecutor
from detection.video_processor import VideoProcessor
from detection.vehicle_detector import VehicleDetector
import logging

class DetectionManager:
    def __init__(self, video_source, output_path=None, skip_frames=0, resize_dim=(640, 480), device="cpu"):
        self.video_processor = VideoProcessor(source=video_source, skip_frames=skip_frames,
                                               output_path=output_path, resize_dim=resize_dim)
        self.vehicle_detector = VehicleDetector(device=device)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.traffic_map = {}
        # Пример зон интереса – делим кадр на две части
        self.zones = [
            {"name": "left", "x1": 0, "y1": 0, "x2": resize_dim[0] // 2, "y2": resize_dim[1]},
            {"name": "right", "x1": resize_dim[0] // 2, "y1": 0, "x2": resize_dim[0], "y2": resize_dim[1]}
        ]
        self.latest_stats = {}
        self.logger = logging.getLogger(__name__)
    
    def process_stream(self):
        """
        Обрабатывает видеопоток, вызывая для каждого кадра callback (здесь отрисовка и статистика):
          - Выполняется детекция объектов с помощью ThreadPoolExecutor.
          - Отрисовываются bounding box и зоны интереса.
        """
        while True:
            frame = self.video_processor.get_frame()
            if frame is None:
                self.logger.info("Конец видеопотока.")
                break

            # Параллельная детекция транспортных средств
            future = self.executor.submit(self.vehicle_detector.detect, frame)
            tracks = future.result()

            # Отрисовка результатов детекции
            for obj in tracks:
                bbox = obj['bbox']
                track_id = obj['track_id']
                label = obj['label']
                confidence = obj['confidence']
                speed = obj.get('speed', 0.0)
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])),
                              (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                text = f"ID:{track_id} {label} {confidence:.2f} spd:{speed:.1f}"
                cv2.putText(frame, text, (int(bbox[0]), int(bbox[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Подсчет ТС в зонах интереса
            stats = {}
            for zone in self.zones:
                count = self.vehicle_detector.count_vehicles_in_zone(tracks, zone)
                stats[zone['name']] = count
                cv2.rectangle(frame, (zone['x1'], zone['y1']), (zone['x2'], zone['y2']), (255, 0, 0), 2)
                cv2.putText(frame, f"{zone['name']}: {count}", (zone['x1'] + 5, zone['y1'] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            self.latest_stats = stats

            cv2.imshow("Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_processor.release()
        self.executor.shutdown()

    def get_flow_statistics(self):
        """
        Возвращает текущую статистику транспортного потока.
        """
        return self.latest_stats

    def save_state(self, filepath):
        """
        Сохраняет состояние детектора (например, треки и статистику) в файл.
        """
        state = {
            'vehicle_detector_tracks': self.vehicle_detector.tracker.tracks,
            'latest_stats': self.latest_stats
        }
        with open(filepath, 'wb') as f:
            pickle.dump(state, f)

    def load_state(self, filepath):
        """
        Загружает состояние детектора из файла.
        """
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        self.vehicle_detector.tracker.tracks = state.get('vehicle_detector_tracks', {})
        self.latest_stats = state.get('latest_stats', {})

if __name__ == "__main__":
    # Демонстрация работы DetectionManager с камерой (или видеофайлом)
    # Если тестовое видео не указано, используется камера (0)
    detector_manager = DetectionManager(video_source=0, output_path=None, skip_frames=1, resize_dim=(640, 480))
    detector_manager.process_stream()
