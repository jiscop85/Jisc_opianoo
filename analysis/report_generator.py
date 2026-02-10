"""
تولید گزارش با چارت‌ها و توصیه‌ها
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # برای استفاده بدون GUI
import seaborn as sns
from typing import Dict, List, Optional
from pathlib import Path
import numpy as np
from ..utils.logger import logger


