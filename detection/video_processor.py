"""
Модуль video_processor.py
-------------------------
Класс VideoProcessor отвечает за получение кадров из видеопотока (камера или видеофайл),
предобработку кадра (изменение размера, фильтрация шумов),
пропуск кадров для ускорения обработки и сохранение обработанного видео в файл.
"""

import cv2
import numpy as np
import logging


class VideoProcessor:
    """
    Класс для обработки видеопотока.

    Аргументы:
        source (str/int): Путь к видеофайлу или индекс камеры.
        skip_frames (int): Количество кадров для пропуска между обработанными кадрами.
        output_path (str): Если указан, сохранение обработанного видео по данному пути.
        resize_dim (tuple): Размер (ширина, высота) для изменения размера каждого кадра.
    """

    def __init__(self, source=0, skip_frames=0, output_path=None, resize_dim=(640, 480)):
        self.source = source
        self.skip_frames = skip_frames
        self.resize_dim = resize_dim
        self.output_path = output_path

        self.capture = cv2.VideoCapture(source)
        if not self.capture.isOpened():
            raise ValueError(f"Не удалось открыть видеоисточник: {source}")

        # Получаем параметры видео
        self.fps = self.capture.get(cv2.CAP_PROP_FPS) or 30
        self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Если указан путь для сохранения, настраиваем VideoWriter
        self.out_writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.out_writer = cv2.VideoWriter(output_path, fourcc, self.fps, self.resize_dim)

        self.logger = logging.getLogger(__name__)

    def preprocess_frame(self, frame):
        """
        Предобработка кадра: изменение размера и сглаживание для фильтрации шумов.

        Аргументы:
            frame (numpy.ndarray): Исходный кадр.

        Возвращает:
            numpy.ndarray: Обработанный кадр.
        """
        processed = cv2.resize(frame, self.resize_dim)
        processed = cv2.GaussianBlur(processed, (5, 5), 0)
        return processed

    def get_frame(self):
        """
        Получает следующий кадр с учётом режима пропуска кадров.

        Возвращает:
            numpy.ndarray или None: Обработанный кадр или None, если кадры закончились.
        """
        # Пропускаем заданное количество кадров
        for _ in range(self.skip_frames + 1):
            ret, frame = self.capture.read()
            if not ret:
                return None
        processed_frame = self.preprocess_frame(frame)

        # Если видео записывается, сохраняем обработанный кадр
        if self.out_writer:
            self.out_writer.write(processed_frame)

        return processed_frame

    def release(self):
        """
        Освобождает ресурсы видеопотока и закрывает окна OpenCV.
        """
        self.capture.release()
        if self.out_writer:
            self.out_writer.release()
        cv2.destroyAllWindows()

    def process_stream(self, frame_callback):
        """
        Обрабатывает видеопоток. Для каждого обработанного кадра вызывается функция обратного вызова.

        Аргументы:
            frame_callback (callable): Функция с сигнатурой callback(frame), которая обрабатывает каждый кадр.
        """
        while True:
            frame = self.get_frame()
            if frame is None:
                self.logger.info("Конец видеопотока или ошибка получения кадра.")
                break
            frame_callback(frame)
