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
        
        # Pie chart
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(labels)], startangle=90)
        ax.set_title(f'Error Types Distribution - {self.lesson_name}', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        file_path = output_dir / 'error_types.png'
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(file_path)
    
    def _create_timing_chart(self, output_dir: Path) -> str:
        """چارت تحلیل زمان‌بندی"""
        timing_analysis = self.analysis.get('timing_analysis', {})
        
        if not timing_analysis:
            return ""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # چارت توزیع اشتباهات در زمان
        errors_per_segment = timing_analysis.get('errors_per_segment', {})
        if errors_per_segment:
            segments = sorted(errors_per_segment.keys())
            error_counts = [errors_per_segment[s] for s in segments]
            
            ax1.bar(segments, error_counts, color='#ff6b6b', alpha=0.7)
            ax1.set_xlabel('Time Segment')
            ax1.set_ylabel('Number of Errors')
            ax1.set_title('Errors Over Time')
            ax1.grid(axis='y', alpha=0.3)
        
        # چارت توزیع زمانی (histogram)
        # این نیاز به داده‌های خام دارد که در اینجا نداریم
        # می‌توان از timing_analysis استفاده کرد
        
        plt.tight_layout()
        
        file_path = output_dir / 'timing_analysis.png'
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(file_path)
    
    def _create_note_patterns_chart(self, output_dir: Path) -> str:
        """چارت الگوهای نت"""
        note_patterns = self.analysis.get('note_patterns', {})
        
        if not note_patterns:
            return ""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # چارت نت‌های مشکل‌دار
        problematic_notes = note_patterns.get('most_problematic_notes', [])
        if problematic_notes:
            note_names = [n['name'] for n in problematic_notes]
            error_counts = [n['error_count'] for n in problematic_notes]
            
            ax1.barh(note_names, error_counts, color='#4ecdc4')
            ax1.set_xlabel('Error Count')
            ax1.set_title('Most Problematic Notes')
            ax1.grid(axis='x', alpha=0.3)
        
        # چارت کلیدهای سفید vs سیاه
        white_vs_black = note_patterns.get('white_vs_black_keys', {})
        if white_vs_black:
            keys = ['White Keys', 'Black Keys']
            errors = [
                white_vs_black.get('white_key_errors', 0),
                white_vs_black.get('black_key_errors', 0)
            ]
            
            ax2.bar(keys, errors, color=['#ffe66d', '#95e1d3'])
            ax2.set_ylabel('Error Count')
            ax2.set_title('White vs Black Keys Errors')
            ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        file_path = output_dir / 'note_patterns.png'
        plt.savefig(file_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(file_path)
    
    def _create_common_errors_chart(self, output_dir: Path) -> str:
        """چارت اشتباهات رایج"""
        common_errors = self.analysis.get('common_errors', [])
        
        if not common_errors:
            return ""
        
     


