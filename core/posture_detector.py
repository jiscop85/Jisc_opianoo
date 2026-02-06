"""
تشخیص وضعیت دست (posture detection)
"""
from typing import List, Dict, Optional
import numpy as np
from ..utils.constants import HAND_LANDMARKS
from ..utils.helpers import calculate_distance
from ..utils.logger import logger

