"""
Модуль detection_manager.py
---------------------------
Класс DetectionManager объединяет VideoProcessor и VehicleDetector для потоковой обработки видеопотока.
Он отвечает за:
  - получение кадров и запуск детекции в параллельном режиме (с использованием concurrent.futures),
  - отображение результатов (bounding boxes, ID, метки, условная скорость) на кадре,
  - подсчёт ТС в заданных зонах интереса,
  - сохранение и загрузку состояния системы (например, для поддержки блокировок или восстановления).

Также реализована функция main(), демонстрирующая работу модуля.
"""

import cv2
import pickle
from concurrent.futures import ThreadPoolExecutor
from detection.video_processor import VideoProcessor
from detection.vehicle_detector import VehicleDetector


class DetectionManager:
    """
    Класс для управления обнаружением транспортных средств.

    Аргументы:
        video_source (str/int): Путь к видеофайлу или индекс камеры.
        output_path (str): Путь для сохранения обработанного видео.
        skip_frames (int): Количество кадров для пропуска.
        resize_dim (tuple): Размер (ширина, высота) для обработки и отрисовки.
        device (str): Устройство для работы модели (например, 'cpu' или 'cuda').
    """

    def __init__(self, video_source, output_path=None, skip_frames=0, resize_dim=(640, 480), device='cpu'):
        self.video_processor = VideoProcessor(
            source=video_source,
            skip_frames=skip_frames,
            output_path=output_path,
            resize_dim=resize_dim
        )
        self.vehicle_detector = VehicleDetector(device=device)
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.traffic_map = {}  # Структура для хранения статистики по зонам
        # Пример зон интереса с разделением кадра по вертикали (левая и правая части)
        self.zones = [
            {'name': 'left', 'x1': 0, 'y1': 0, 'x2': resize_dim[0] // 2, 'y2': resize_dim[1]},
            {'name': 'right', 'x1': resize_dim[0] // 2, 'y1': 0, 'x2': resize_dim[0], 'y2': resize_dim[1]}
        ]
        self.latest_stats = {}

    def process_stream(self):
        """
        Метод обрабатывает видеопоток, выполняя детекцию транспортных средств на каждом кадре.
        Для ускорения используется параллельное выполнение детекции через ThreadPoolExecutor.
        Отрисовываются обнаруженные объекты и зоны интереса, а также выводится статистика.
        """
        while True:
            frame = self.video_processor.get_frame()
            if frame is None:
                break

            # Параллельный вызов детекции для текущего кадра
            future = self.executor.submit(self.vehicle_detector.detect, frame)
            tracks = future.result()

            # Отрисовываем результаты обнаружения (bounding boxes, ID, метки, скорость)
            for obj in tracks:
                bbox = obj['bbox']
                track_id = obj['track_id']
                label = obj['label']
                confidence = obj['confidence']
                speed = obj['speed']
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
                text = f"ID:{track_id} {label} {confidence:.2f} spd:{speed:.1f}"
                cv2.putText(frame, text, (int(bbox[0]), int(bbox[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Подсчёт транспортных средств по зонам интереса
            stats = {}
            for zone in self.zones:
                count = self.vehicle_detector.count_vehicles_in_zone(tracks, zone)
                stats[zone['name']] = count
                # Отрисовка зоны
                cv2.rectangle(frame, (zone['x1'], zone['y1']), (zone['x2'], zone['y2']), (255, 0, 0), 2)
                cv2.putText(frame, f"{zone['name']}: {count}", (zone['x1'] + 5, zone['y1'] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            self.latest_stats = stats

            # Отображение обработанного кадра
            cv2.imshow("Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.video_processor.release()
        self.executor.shutdown()

    def get_flow_statistics(self):
        """
        Возвращает текущую статистику по плотности транспортного потока.
        
        Возвращает:
            dict: Словарь с количеством ТС по зонам (например, {"left": 3, "right": 5}).
        """
        return self.latest_stats

    def save_state(self, filepath):
        """
        Сохраняет состояние детектора (например, треки и статистику) в файл.

        Аргументы:
            filepath (str): Путь для сохранения состояния.
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

        Аргументы:
            filepath (str): Путь к файлу со сохранённым состоянием.
        """
        with open(filepath, 'rb') as f:
            state = pickle.load(f)
        self.vehicle_detector.tracker.tracks = state.get('vehicle_detector_tracks', {})
        self.latest_stats = state.get('latest_stats', {})


def main():
    """
    Функция демонстрации работы модуля обнаружения.
    Загрузка тестового видео, настройка процессора и детектора,
    обработка видеопотока в реальном времени, отображение результатов и вывод статистики по транспортному потоку.
    """
    video_source = "test_video.mp4"  # Замените на путь к тестовому видео или 0 для камеры
    output_path = "processed_output.mp4"
    detection_manager = DetectionManager(
        video_source=video_source,
        output_path=output_path,
        skip_frames=1,
        resize_dim=(640, 480),
        device='cpu'
    )

    print("Запуск обнаружения транспортных средств. Для выхода нажмите 'q'.")
    detection_manager.process_stream()
    stats = detection_manager.get_flow_statistics()
    print("Статистика транспортного потока:", stats)


if __name__ == "__main__":
    main()
