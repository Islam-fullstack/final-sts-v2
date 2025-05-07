#!/usr/bin/env python
"""
Файл: detection/video_processor.py

Класс VideoProcessor для обработки видеопотока.
"""

import cv2
import numpy as np
import logging

class VideoProcessor:
    def __init__(self, source=0, skip_frames=0, output_path=None, resize_dim=(640, 480)):
        self.source = source
        self.skip_frames = skip_frames
        self.resize_dim = resize_dim
        self.output_path = output_path

        self.capture = cv2.VideoCapture(source)
        if not self.capture.isOpened():
            raise ValueError(f"Cannot open video source: {source}")

        self.fps = self.capture.get(cv2.CAP_PROP_FPS) or 30
        self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.out_writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out_writer = cv2.VideoWriter(output_path, fourcc, self.fps, self.resize_dim)

        self.logger = logging.getLogger(__name__)

    def preprocess_frame(self, frame):
        processed = cv2.resize(frame, self.resize_dim)
        processed = cv2.GaussianBlur(processed, (5, 5), 0)
        return processed

    def get_frame(self):
        # Пропуск заданного количества кадров
        for _ in range(self.skip_frames + 1):
            ret, frame = self.capture.read()
            if not ret:
                return None
        processed_frame = self.preprocess_frame(frame)
        if self.out_writer:
            self.out_writer.write(processed_frame)
        return processed_frame

    def release(self):
        self.capture.release()
        if self.out_writer:
            self.out_writer.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    def demo_callback(frame):
        cv2.imshow("Demo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
    processor = VideoProcessor(source=0, skip_frames=1)
    while True:
        frame = processor.get_frame()
        if frame is None:
            break
        demo_callback(frame)
    processor.release()
