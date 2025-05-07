"""
Модуль vehicle_detector.py
--------------------------
Класс VehicleDetector выполняет обнаружение и классификацию транспортных средств на кадре,
использует предобученную модель YOLOv5 (через torch.hub) и реализует базовый трекинг
на основе центроидов (SimpleTracker). Кроме того, класс предоставляет функцию подсчёта ТС в заданной зоне.
"""

import torch
import cv2
import numpy as np
from scipy.spatial.distance import euclidean


class VehicleDetector:
    """
    Класс для обнаружения и классификации транспортных средств с использованием предобученной модели YOLOv5,
    а также базового трекинга для отслеживания объектов.

    Методы:
        detect(frame): Выполняет детекцию транспортных средств на кадре и обновляет треки.
        count_vehicles_in_zone(tracks, zone): Подсчитывает количество ТС, центры которых попадают в указанную зону.
    """

    def __init__(self, device='cpu'):
        self.device = device
        # Загрузка предобученной модели YOLOv5 из репозитория ultralytics
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True).to(self.device)
        self.model.eval()
        # Определяем категории транспортных средств, которые нас интересуют
        self.vehicle_categories = ['car', 'truck', 'bus', 'motorcycle']
        self.tracker = SimpleTracker(max_distance=50, max_missed=5)

    def detect(self, frame):
        """
        Детектирует транспортные средства на кадре.

        Аргументы:
            frame (numpy.ndarray): Изображение в формате BGR.

        Возвращает:
            List[dict]: Список обнаруженных транспортных средств с информацией о треке,
                        например, {'track_id', 'bbox', 'centroid', 'speed', 'label', 'confidence'}.
        """
        # Переход из BGR в RGB, так как модель ожидает RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(img)
        # Получаем результаты в виде pandas DataFrame
        df = results.pandas().xyxy[0]
        detections = []
        for index, row in df.iterrows():
            if row['name'] in self.vehicle_categories:
                bbox = [row['xmin'], row['ymin'], row['xmax'], row['ymax']]
                detection = {
                    'bbox': bbox,
                    'confidence': row['confidence'],
                    'name': row['name']
                }
                detections.append(detection)
        # Обновляем трекер, сопоставляя детекции с существующими треками
        tracks = self.tracker.update(detections)
        return tracks

    def count_vehicles_in_zone(self, tracks, zone):
        """
        Подсчитывает количество транспортных средств в заданной зоне.

        Аргументы:
            tracks (List[dict]): Список треков, полученных из метода detect().
            zone (dict): Определение зоны интереса, например, {'name': 'zone1',
                         'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100}.

        Возвращает:
            int: Количество транспортных средств в зоне.
        """
        count = 0
        for track in tracks:
            cx, cy = track['centroid']
            if zone['x1'] <= cx <= zone['x2'] and zone['y1'] <= cy <= zone['y2']:
                count += 1
        return count


class SimpleTracker:
    """
    Простой трекер на основе сопоставления центроидов обнаруженных объектов.
    Для каждого нового обнаружения ищется ближайший существующий трек, если расстояние меньше max_distance.
    Если сопоставление найдено, трек обновляется, иначе создаётся новый.
    Также ведётся учёт пропущенных кадров, чтобы удалять неактуальные треки.
    """

    def __init__(self, max_distance=50, max_missed=5):
        self.tracks = {}  # track_id -> {'centroid': [x, y], 'bbox': [xmin, ymin, xmax, ymax], 'missed': int}
        self.next_id = 0
        self.max_distance = max_distance
        self.max_missed = max_missed

    def update(self, detections):
        """
        Обновляет данные треков на основе текущих детекций.

        Аргументы:
            detections (List[dict]): Список детекций с ключом 'bbox'.

        Возвращает:
            List[dict]: Список треков с дополнительной информацией (track_id, centroid, скорость, label, confidence).
        """
        updated_tracks = {}
        results = []
        used_tracks = set()

        for det in detections:
            bbox = det['bbox']
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            centroid = np.array([cx, cy])

            # Поиск ближайшего существующего трека
            min_dist = float('inf')
            matched_id = None
            for track_id, track in self.tracks.items():
                track_centroid = np.array(track['centroid'])
                dist = np.linalg.norm(centroid - track_centroid)
                if dist < min_dist and dist < self.max_distance and track_id not in used_tracks:
                    min_dist = dist
                    matched_id = track_id

            if matched_id is not None:
                track = self.tracks[matched_id]
                # Вычисляем условную скорость как разность центроидов (без калибровки)
                speed = np.linalg.norm(centroid - np.array(track['centroid']))
                updated_tracks[matched_id] = {
                    'centroid': centroid.tolist(),
                    'bbox': bbox,
                    'missed': 0,
                    'speed': speed
                }
                results.append({
                    'track_id': matched_id,
                    'bbox': bbox,
                    'centroid': centroid.tolist(),
                    'speed': speed,
                    'label': det['name'],
                    'confidence': det['confidence']
                })
                used_tracks.add(matched_id)
            else:
                # Создаём новый трек, если сопоставление не найдено
                new_id = self.next_id
                self.next_id += 1
                updated_tracks[new_id] = {
                    'centroid': centroid.tolist(),
                    'bbox': bbox,
                    'missed': 0,
                    'speed': 0.0
                }
                results.append({
                    'track_id': new_id,
                    'bbox': bbox,
                    'centroid': centroid.tolist(),
                    'speed': 0.0,
                    'label': det['name'],
                    'confidence': det['confidence']
                })

        # Увеличиваем счётчик пропущенных кадров для треков, не обновлённых в этом кадре
        for track_id, track in self.tracks.items():
            if track_id not in updated_tracks:
                track['missed'] += 1
                if track['missed'] < self.max_missed:
                    updated_tracks[track_id] = track

        self.tracks = updated_tracks
        return results
