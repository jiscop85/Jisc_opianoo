"""
موتور صوتی با FluidSynth برای پخش نت‌های پیانو
"""
import fluidsynth
import threading
import time
from typing import Dict, Optional
import config
from ..utils.logger import logger


