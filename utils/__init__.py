# Добавляем dummy-класс TryExcept для совместимости с YOLOv5, который ищет его в utils.
class TryExcept:
    """Stub-класс для обеспечения импорта в YOLOv5."""
    pass

from .config_loader import *
from .logger import *
