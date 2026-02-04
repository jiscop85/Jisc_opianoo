"""
تشخیص انگشت استفاده شده برای فشردن کلاویه
"""
from typing import List, Tuple, Optional, Dict
import numpy as np
from ..utils.constants import HAND_LANDMARKS
from ..utils.helpers import calculate_distance
from ..utils.logger import logger


