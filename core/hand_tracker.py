"""
ردیابی دست با MediaPipe و OpenCV
"""
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtCore import QThread, Signal
from typing import List, Tuple, Optional, Dict
import config
from ..utils.helpers import map_coordinates, calculate_distance
from ..utils.logger import logger
from .finger_detector import FingerDetector

