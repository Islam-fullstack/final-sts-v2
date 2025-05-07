#!/usr/bin/env python
"""
Файл: detection/vehicle_detector.py

Класс VehicleDetector выполняет обнаружение и классификацию транспортных средств на кадре.
Использует предобученную модель YOLOv8 через пакет ultralytics и реализует простой трекер (SimpleTracker).
"""

from ultralytics import YOLO  # YOLOv8
import cv2
import numpy as np

class VehicleDetector:
    def __init__(self, device='cpu'):
        self.device = device
        # Загрузка модели YOLOv8 (например, nano версия, можно поменять на другую)
        self.model = YOLO("yolov8n.pt")  # убедитесь, что модель установлена
        self.vehicle_categories = ['car', 'truck', 'bus', 'motorcycle']
        self.tracker = SimpleTracker(max_distance=50, max_missed=5)

    def detect(self, frame):
        # Модель YOLOv8 автоматически обрабатывает изображения
        results = self.model(frame, verbose=False)[0]
        detections = []
        # results.boxes.xyxy, results.boxes.conf, results.boxes.cls
        if results.boxes is not None:
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            classes = results.boxes.cls.cpu().numpy().astype(int)
            for bbox, conf, cls in zip(boxes, confidences, classes):
                # Получаем имя класса из id
                label = self.model.model.names[cls]
                if label in self.vehicle_categories:
                    detection = {
                        'bbox': bbox.tolist(),
                        'confidence': float(conf),
                        'name': label
                    }
                    detections.append(detection)
        tracks = self.tracker.update(detections)
        return tracks

    def count_vehicles_in_zone(self, tracks, zone):
        count = 0
        for track in tracks:
            cx, cy = track['centroid']
            if zone['x1'] <= cx <= zone['x2'] and zone['y1'] <= cy <= zone['y2']:
                count += 1
        return count

class SimpleTracker:
    def __init__(self, max_distance=50, max_missed=5):
        self.tracks = {}
        self.next_id = 0
        self.max_distance = max_distance
        self.max_missed = max_missed

    def update(self, detections):
        updated_tracks = {}
        results = []
        used_tracks = set()

        for det in detections:
            bbox = det['bbox']
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            centroid = [cx, cy]
            min_dist = float('inf')
            matched_id = None
            for track_id, track in self.tracks.items():
                track_centroid = track['centroid']
                dist = np.linalg.norm(np.array(centroid) - np.array(track_centroid))
                if dist < min_dist and dist < self.max_distance and track_id not in used_tracks:
                    min_dist = dist
                    matched_id = track_id
            if matched_id is not None:
                track = self.tracks[matched_id]
                speed = np.linalg.norm(np.array(centroid) - np.array(track['centroid']))
                updated_tracks[matched_id] = {'centroid': centroid, 'bbox': bbox, 'missed': 0, 'speed': speed}
                results.append({'track_id': matched_id, 'bbox': bbox, 'centroid': centroid,
                                'speed': speed, 'label': det['name'], 'confidence': det['confidence']})
                used_tracks.add(matched_id)
            else:
                new_id = self.next_id
                self.next_id += 1
                updated_tracks[new_id] = {'centroid': centroid, 'bbox': bbox, 'missed': 0, 'speed': 0.0}
                results.append({'track_id': new_id, 'bbox': bbox, 'centroid': centroid,
                                'speed': 0.0, 'label': det['name'], 'confidence': det['confidence']})
        for track_id, track in self.tracks.items():
            if track_id not in updated_tracks:
                track['missed'] += 1
                if track['missed'] < self.max_missed:
                    updated_tracks[track_id] = track
        self.tracks = updated_tracks
        return results

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = VehicleDetector()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        tracks = detector.detect(frame)
        for obj in tracks:
            bbox = obj['bbox']
            text = f"ID:{obj['track_id']} {obj['label']} {obj['confidence']:.2f}"
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])),
                          (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
            cv2.putText(frame, text, (int(bbox[0]), int(bbox[1])-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imshow("Vehicle Detection Demo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
