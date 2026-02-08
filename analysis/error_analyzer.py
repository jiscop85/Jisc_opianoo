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
        

        # تبدیل به لیست
        common_errors = []
        for (expected, played), count in error_pairs.most_common(top_n):
            common_errors.append({
                'expected_note': expected,
                'expected_name': midi_to_note_name(expected) if expected else None,
                'played_note': played,
                'played_name': midi_to_note_name(played) if played else None,
                'count': count,
                'percentage': (count / len(self.error_logs)) * 100.0
            })
        
        return common_errors
    
    def _analyze_timing(self) -> Dict:
        """تحلیل زمان‌بندی اشتباهات"""
        if not self.error_logs:
            return {}
        
        timestamps = [error.get('timestamp', 0) for error in self.error_logs]
        
        if not timestamps:
            return {}
        
        # تقسیم‌بندی به بخش‌های زمانی
        max_time = max(timestamps)
        time_segments = 4  # تقسیم به 4 بخش
        
        segment_errors = defaultdict(int)
        for timestamp in timestamps:
            segment = int((timestamp / max_time) * time_segments) if max_time > 0 else 0
            segment = min(segment, time_segments - 1)
            segment_errors[segment] += 1
        
        return {
            'total_time': max_time,
            'errors_per_segment': dict(segment_errors),
            'average_error_time': sum(timestamps) / len(timestamps),
            'error_distribution': 'uniform' if len(set(segment_errors.values())) == 1 else 'variable'
        }
    
    def _analyze_note_patterns(self) -> Dict:
        """تحلیل الگوهای نت"""
        # تحلیل نت‌های مشکل‌دار
        problematic_notes = Counter()
        note_ranges = defaultdict(int)
        
        for error in self.error_logs:
            expected = error.get('expected_note')
            if expected is not None:
                problematic_notes[expected] += 1
                
                # محدوده نت
                octave = (expected // 12) - 1
                if octave < 3:
                    note_ranges['low'] += 1
                elif octave < 5:
                    note_ranges['middle'] += 1
                else:
                    note_ranges['high'] += 1
          # تحلیل کلیدهای سفید vs سیاه
        white_key_errors = 0
        black_key_errors = 0
        
        for error in self.error_logs:
            expected = error.get('expected_note')
            if expected is not None:
                if is_white_key(expected):
                    white_key_errors += 1
                else:
                    black_key_errors += 1
        
        return {
            'most_problematic_notes': [
                {
                    'note': note,
                    'name': midi_to_note_name(note),
                    'error_count': count
                }
                for note, count in problematic_notes.most_common(5)
            ],
            'note_range_errors': dict(note_ranges),
            'white_vs_black_keys': {
                'white_key_errors': white_key_errors,
                'black_key_errors': black_key_errors,
                'ratio': white_key_errors / black_key_errors if black_key_errors > 0 else float('inf')
            }
        }
    
    def _identify_difficulty_areas(self) -> List[Dict]:
        """شناسایی مناطق مشکل‌دار"""
        difficulty_areas = []
        
        # تحلیل بر اساس نوع اشتباه
        error_types = self._analyze_error_types()
        
        if error_types.get('missed_note', 0) > len(self.error_logs) * 0.3:
            difficulty_areas.append({
                'area': 'Timing',
                'description': 'مشکل در زمان‌بندی - نت‌های زیادی از دست رفته‌اند',
                'severity': 'high' if error_types['missed_note'] > len(self.error_logs) * 0.5 else 'medium'
            })
        
        if error_types.get('wrong_note', 0) > len(self.error_logs) * 0.3:
            difficulty_areas.append({
                'area': 'Note Recognition',
                'description': 'مشکل در تشخیص نت‌ها - نت‌های اشتباه زیادی نواخته شده',
                'severity': 'high' if error_types['wrong_note'] > len(self.error_logs) * 0.5 else 'medium'
            })
           if error_types.get('extra_note', 0) > len(self.error_logs) * 0.2:
            difficulty_areas.append({
                'area': 'Control',
                'description': 'مشکل در کنترل - نت‌های اضافی زیادی نواخته شده',
                'severity': 'medium'
            })
        
        # تحلیل الگوهای نت
        note_patterns = self._analyze_note_patterns()
        if note_patterns.get('white_vs_black_keys', {}).get('black_key_errors', 0) > 0:
            black_ratio = note_patterns['white_vs_black_keys'].get('ratio', 0)
            if black_ratio < 2.0:  # نسبت کمتر از 2:1
                difficulty_areas.append({
                    'area': 'Black Keys',
                    'description': 'مشکل در نواختن کلیدهای سیاه',
                    'severity': 'medium'
                })
        
        return difficulty_areas
    
    def _analyze_finger_usage(self) -> Dict:
        """تحلیل استفاده از انگشتان"""
        finger_errors = defaultdict(int)
        finger_usage = defaultdict(list)  # finger: [expected, actual]
        
        for error in self.error_logs:
            finger_used = error.get('finger_used')
            if finger_used:
                finger_errors[finger_used] += 1
                
                # اگر اطلاعات انگشت مورد انتظار موجود باشد
                expected_finger = error.get('expected_finger')
                if expected_finger and expected_finger != finger_used:
                    finger_usage[finger_used].append(expected_finger)
        
        # پیدا کردن الگوهای استفاده اشتباه انگشت
        finger_patterns = {}
        for finger, expected_list in finger_usage.items():
            if expected_list:
                most_common_expected = Counter(expected_list).most_common(1)[0][0]
                finger_patterns[finger] = {
                    'used': finger,
                    'should_use': most_common_expected,
                    'count': len(expected_list)
                }
        
        return {
            'finger_errors': dict(finger_errors),
            'finger_patterns': finger_patterns,
            'total_finger_errors': sum(finger_errors.values())
        }
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """تولید توصیه‌های هوشمند"""
        recommendations = []
        
        # توصیه‌های بر اساس نوع اشتباه
        error_types = analysis.get('error_types', {})
        total_errors = analysis.get('total_errors', 0)
        
        if total_errors == 0:
            recommendations.append("عالی! هیچ اشتباهی نداشتید. به تمرین ادامه دهید!")
            return recommendations
        
        # توصیه برای missed notes
        missed_count = error_types.get('missed_note', 0)
        if missed_count > total_errors * 0.3:
            recommendations.append(
                f"شما {missed_count} نت را از دست داده‌اید. "
                "سعی کنید با سرعت کمتری تمرین کنید و روی زمان‌بندی تمرکز کنید."
            )
        
        # توصیه برای wrong notes
        wrong_count = error_types.get('wrong_note', 0)
        if wrong_count > total_errors * 0.3:
            recommendations.append(
                f"شما {wrong_count} نت اشتباه نواخته‌اید. "
                "قبل از نواختن، موقعیت دست خود را بررسی کنید و مطمئن شوید که روی کلاویه صحیح قرار دارد."
            )
        
        # توصیه برای extra notes
        extra_count = error_types.get('extra_note', 0)
        if extra_count > total_errors * 0.2:
            recommendations.append(
                f"شما {extra_count} نت اضافی نواخته‌اید. "
                "سعی کنید کنترل بیشتری روی دست خود داشته باشید و فقط نت‌های لازم را بنوازید."
            )
        
        # توصیه بر اساس مناطق مشکل‌دار
        difficulty_areas = analysis.get('difficulty_areas', [])
        for area in difficulty_areas:
            if area['severity'] == 'high':
                recommendations.append(
                    f"⚠️ مشکل جدی در {area['area']}: {area['description']}"
                )
        
        # توصیه برای finger usage
        finger_usage = analysis.get('finger_usage_errors', {})
        finger_patterns = finger_usage.get('finger_patterns', {})
        if finger_patterns:
            for finger, pattern in finger_patterns.items():
                recommendations.append(
                    f"⚠️ شما اغلب از انگشت {pattern['used']} استفاده می‌کنید "
                    f"در حالی که باید از انگشت {pattern['should_use']} استفاده کنید. "
                    f"این مشکل {pattern['count']} بار رخ داده است."
                )
        
        # توصیه‌های کلی
        accuracy_estimate = 100 - (total_errors / max(1, total_errors + 50) * 100)
        if accuracy_estimate < 50:
            recommendations.append(
                "دقت شما کمتر از 50% است. پیشنهاد می‌شود این درس را دوباره تمرین کنید."
            )
        elif accuracy_estimate < 70:
            recommendations.append(
                "دقت شما قابل قبول است اما می‌تواند بهتر شود. چند بار دیگر این درس را تمرین کنید."
            )
        else:
            recommendations.append(
                "دقت خوبی دارید! برای بهبود بیشتر، سعی کنید سرعت را افزایش دهید."
            )
        
        return recommendations
     

      




