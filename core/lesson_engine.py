"""
موتور مدیریت درس‌ها: مقایسه نت‌ها، تشخیص اشتباهات
"""
import mido
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import config
from ..utils.helpers import midi_to_note_name
from ..utils.logger import logger

