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

# تنظیم فونت فارسی (اگر نیاز باشد)
plt.rcParams['font.family'] = 'DejaVu Sans'


class ReportGenerator:
    """تولیدکننده گزارش"""
    
    def __init__(self, analysis_result: Dict, lesson_name: str = "Unknown"):
        self.analysis = analysis_result
        self.lesson_name = lesson_name
        self.figures = []
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, str]:
        """
        تولید گزارش کامل
        
        Returns:
            دیکشنری شامل مسیر فایل‌های تولید شده
        """
        if output_path:
            output_dir = Path(output_path)
        else:
            output_dir = Path("reports")
        
        output_dir.mkdir(exist_ok=True)
        
        report_files = {}
        
        try:
            # تولید چارت‌ها
            report_files['error_types_chart'] = self._create_error_types_chart(output_dir)
            report_files['timing_chart'] = self._create_timing_chart(output_dir)
            report_files['note_patterns_chart'] = self._create_note_patterns_chart(output_dir)
            report_files['common_errors_chart'] = self._create_common_errors_chart(output_dir)
            
            logger.info(f"Report generated: {output_dir}")
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
        
        return report_files
    
    def _create_error_types_chart(self, output_dir: Path) -> str:
        """چارت انواع اشتباهات"""
        error_types = self.analysis.get('error_types', {})
        
        if not error_types:
            return ""
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        labels = list(error_types.keys())
        values = list(error_types.values())
        colors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#95e1d3']
        
 
