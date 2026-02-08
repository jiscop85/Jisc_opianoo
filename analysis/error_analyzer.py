"""
تحلیل اشتباهات: دسته‌بندی، تشخیص الگوهای رایج
"""
from typing import List, Dict, Optional
from collections import defaultdict, Counter
from ..utils.helpers import midi_to_note_name, is_white_key
from ..utils.logger import logger


class ErrorAnalyzer:
    """تحلیل‌گر اشتباهات"""
    
    def __init__(self, error_logs: List[Dict]):
        self.error_logs = error_logs
        self.analysis_result = None
    
    def analyze(self) -> Dict:
        """
        تحلیل کامل اشتباهات
        
        Returns:
            دیکشنری شامل تحلیل‌های مختلف
        """
        if not self.error_logs:
            return self._empty_analysis()
        
        analysis = {
            'total_errors': len(self.error_logs),
            'error_types': self._analyze_error_types(),
            'common_errors': self._find_common_errors(),
            'timing_analysis': self._analyze_timing(),
            'note_patterns': self._analyze_note_patterns(),
            'difficulty_areas': self._identify_difficulty_areas(),
            'finger_usage_errors': self._analyze_finger_usage(),
            'recommendations': []
        }
        
        # تولید توصیه‌ها
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        self.analysis_result = analysis
        return analysis
    
    def _empty_analysis(self) -> Dict:
        """تحلیل خالی"""
        return {
            'total_errors': 0,
            'error_types': {},
            'common_errors': [],
            'timing_analysis': {},
            'note_patterns': {},
            'difficulty_areas': [],
            'recommendations': ['هیچ اشتباهی ثبت نشده است!']
        }
    
    def _analyze_error_types(self) -> Dict[str, int]:
        """تحلیل انواع اشتباهات"""
        error_type_counts = Counter()
        
        for error in self.error_logs:
            error_type = error.get('error_type', 'unknown')
            error_type_counts[error_type] += 1
        
        return dict(error_type_counts)
    
    def _find_common_errors(self, top_n: int = 10) -> List[Dict]:
        """پیدا کردن اشتباهات رایج"""
        # شمارش جفت‌های (expected, played)
        error_pairs = Counter()
        
        for error in self.error_logs:
            expected = error.get('expected_note')
            played = error.get('played_note')
            
            if expected is not None:
                if played is not None:
                    # نت اشتباه
                    pair = (expected, played)
                    error_pairs[pair] += 1
                else:
                    # نت از دست رفته
                    pair = (expected, None)
                    error_pairs[pair] += 1
        

