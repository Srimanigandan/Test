#!/usr/bin/env python3
"""
Build System Learning Engine
Learns patterns from build processes to provide intelligent assistance
"""

import json
import logging
import pickle
import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class BuildPatternLearner:
    """
    Learns patterns from build processes to provide intelligent recommendations
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.model_dir = self.project_root / "mcp" / "models"
        self.model_dir.mkdir(exist_ok=True, parents=True)
        
        # Pattern storage
        self.error_patterns = defaultdict(list)
        self.success_patterns = defaultdict(list)
        self.performance_patterns = []
        self.resolution_patterns = {}
        
        # ML models
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.error_clusterer = None
        self.error_vectors = None
        
        # Load existing patterns
        self._load_patterns()
    
    def _load_patterns(self):
        """Load previously learned patterns"""
        try:
            patterns_file = self.model_dir / "build_patterns.pkl"
            if patterns_file.exists():
                with open(patterns_file, 'rb') as f:
                    data = pickle.load(f)
                    self.error_patterns = data.get('error_patterns', defaultdict(list))
                    self.success_patterns = data.get('success_patterns', defaultdict(list))
                    self.performance_patterns = data.get('performance_patterns', [])
                    self.resolution_patterns = data.get('resolution_patterns', {})
                    
                logger.info("Loaded existing build patterns")
        except Exception as e:
            logger.warning(f"Could not load existing patterns: {e}")
    
    def _save_patterns(self):
        """Save learned patterns to disk"""
        try:
            patterns_file = self.model_dir / "build_patterns.pkl"
            with open(patterns_file, 'wb') as f:
                pickle.dump({
                    'error_patterns': dict(self.error_patterns),
                    'success_patterns': dict(self.success_patterns),
                    'performance_patterns': self.performance_patterns,
                    'resolution_patterns': self.resolution_patterns
                }, f)
            logger.info("Saved build patterns")
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")
    
    def learn_from_build_event(self, build_event: Dict[str, Any]):
        """Learn from a single build event"""
        try:
            task = build_event.get('task', 'unknown')
            status = build_event.get('status', 'unknown')
            timestamp = build_event.get('timestamp')
            
            if status == 'SUCCESS':
                self._learn_success_pattern(build_event)
            elif status in ['FAILED', 'WARNINGS']:
                self._learn_error_pattern(build_event)
            
            # Always learn performance patterns
            self._learn_performance_pattern(build_event)
            
            # Save patterns periodically
            if len(self.error_patterns) % 10 == 0:
                self._save_patterns()
                
        except Exception as e:
            logger.error(f"Error learning from build event: {e}")
    
    def _learn_success_pattern(self, build_event: Dict[str, Any]):
        """Learn patterns from successful builds"""
        task = build_event.get('task')
        duration = build_event.get('duration', 0)
        
        pattern = {
            'timestamp': build_event.get('timestamp'),
            'duration': duration,
            'inputs': build_event.get('inputs', []),
            'outputs': build_event.get('outputs', [])
        }
        
        self.success_patterns[task].append(pattern)
        
        # Keep only recent patterns (last 100)
        if len(self.success_patterns[task]) > 100:
            self.success_patterns[task] = self.success_patterns[task][-100:]
    
    def _learn_error_pattern(self, build_event: Dict[str, Any]):
        """Learn patterns from failed builds"""
        task = build_event.get('task')
        errors = build_event.get('errors', [])
        
        for error in errors:
            error_text = str(error)
            error_type = self._classify_error_type(error_text)
            
            pattern = {
                'timestamp': build_event.get('timestamp'),
                'error_text': error_text,
                'error_type': error_type,
                'task': task,
                'context': self._extract_error_context(build_event)
            }
            
            self.error_patterns[error_type].append(pattern)
            
            # Keep only recent error patterns
            if len(self.error_patterns[error_type]) > 50:
                self.error_patterns[error_type] = self.error_patterns[error_type][-50:]
    
    def _learn_performance_pattern(self, build_event: Dict[str, Any]):
        """Learn performance patterns"""
        duration = build_event.get('duration', 0)
        if duration > 0:
            pattern = {
                'timestamp': build_event.get('timestamp'),
                'task': build_event.get('task'),
                'duration': duration,
                'status': build_event.get('status'),
                'file_count': len(build_event.get('sourceFiles', [])),
                'hour_of_day': datetime.now().hour
            }
            
            self.performance_patterns.append(pattern)
            
            # Keep only recent performance data
            if len(self.performance_patterns) > 200:
                self.performance_patterns = self.performance_patterns[-200:]
    
    def _classify_error_type(self, error_text: str) -> str:
        """Classify error type based on text content"""
        error_lower = error_text.lower()
        
        if 'compilation' in error_lower or 'compile' in error_lower:
            return 'compilation_error'
        elif 'link' in error_lower or 'ld:' in error_lower:
            return 'linking_error'
        elif 'include' in error_lower or 'header' in error_lower:
            return 'header_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        elif 'misra' in error_lower or 'violation' in error_lower:
            return 'static_analysis_error'
        elif 'timeout' in error_lower or 'slow' in error_lower:
            return 'performance_error'
        else:
            return 'other_error'
    
    def _extract_error_context(self, build_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contextual information from build event"""
        return {
            'task': build_event.get('task'),
            'file_count': len(build_event.get('sourceFiles', [])),
            'time_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
    
    def predict_build_issues(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict potential build issues based on learned patterns"""
        predictions = []
        
        task = current_context.get('task', 'unknown')
        current_time = datetime.now()
        
        # Analyze error frequency patterns
        for error_type, patterns in self.error_patterns.items():
            if len(patterns) < 3:  # Need sufficient data
                continue
            
            # Calculate error frequency for this task
            task_errors = [p for p in patterns if p.get('task') == task]
            if len(task_errors) >= 2:
                # Recent error trend
                recent_errors = [
                    p for p in task_errors 
                    if self._is_recent(p.get('timestamp'), hours=24)
                ]
                
                if len(recent_errors) > 0:
                    probability = min(len(recent_errors) / len(task_errors), 1.0)
                    
                    predictions.append({
                        'error_type': error_type,
                        'probability': probability,
                        'recent_occurrences': len(recent_errors),
                        'common_causes': self._get_common_causes(error_type),
                        'prevention_tips': self._get_prevention_tips(error_type)
                    })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions[:5]  # Top 5 predictions
    
    def get_build_recommendations(self, issue_description: str) -> Dict[str, Any]:
        """Get recommendations based on issue description and learned patterns"""
        # Find similar historical issues
        similar_issues = self._find_similar_issues(issue_description)
        
        # Get error type specific recommendations
        error_type = self._classify_error_type(issue_description)
        type_recommendations = self._get_type_specific_recommendations(error_type)
        
        # Performance recommendations
        performance_tips = self._get_performance_recommendations()
        
        return {
            'similar_historical_issues': similar_issues,
            'error_type': error_type,
            'specific_recommendations': type_recommendations,
            'performance_tips': performance_tips,
            'success_rate_improvement': self._calculate_success_rate_improvement(error_type)
        }
    
    def _find_similar_issues(self, issue_description: str) -> List[Dict[str, Any]]:
        """Find similar issues from historical data using text similarity"""
        if not self.error_patterns:
            return []
        
        # Collect all error texts
        all_errors = []
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                all_errors.append({
                    'text': pattern.get('error_text', ''),
                    'type': error_type,
                    'timestamp': pattern.get('timestamp'),
                    'resolution': self.resolution_patterns.get(
                        pattern.get('error_text', ''), None
                    )
                })
        
        if not all_errors:
            return []
        
        try:
            # Vectorize error texts
            error_texts = [issue_description] + [error['text'] for error in all_errors]
            vectors = self.vectorizer.fit_transform(error_texts)
            
            # Calculate similarity
            similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
            
            # Get top similar issues
            similar_indices = np.argsort(similarities)[::-1][:5]
            
            similar_issues = []
            for idx in similar_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    similar_issues.append({
                        'issue': all_errors[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return similar_issues
            
        except Exception as e:
            logger.error(f"Error finding similar issues: {e}")
            return []
    
    def _get_type_specific_recommendations(self, error_type: str) -> List[str]:
        """Get recommendations specific to error type"""
        recommendations = {
            'compilation_error': [
                "Check syntax and semicolons in C files",
                "Verify all functions are properly declared",
                "Ensure all included headers exist",
                "Check for missing braces or parentheses"
            ],
            'header_error': [
                "Run 'gradle generateHeaders' to regenerate header files",
                "Check if template files exist in src/main/templates/",
                "Verify header include paths",
                "Ensure config.h is included first"
            ],
            'static_analysis_error': [
                "Review MISRA-C compliance rules",
                "Remove any goto statements",
                "Add proper error handling to functions",
                "Check automotive coding standards"
            ],
            'linking_error': [
                "Check for duplicate function definitions",
                "Verify all required object files are generated",
                "Review linker script for automotive requirements"
            ],
            'permission_error': [
                "Check file and directory permissions",
                "Ensure build directory is writable",
                "Run build with appropriate user privileges"
            ],
            'performance_error': [
                "Use parallel build: gradle --parallel",
                "Clean build directory: gradle clean",
                "Check available system memory and disk space"
            ]
        }
        
        return recommendations.get(error_type, [
            "Check build logs for detailed error messages",
            "Try running a clean build",
            "Verify all dependencies are available"
        ])
    
    def _get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """Get performance recommendations based on learned patterns"""
        if not self.performance_patterns:
            return []
        
        recommendations = []
        
        # Analyze build duration trends
        recent_patterns = [
            p for p in self.performance_patterns 
            if self._is_recent(p.get('timestamp'), hours=24)
        ]
        
        if len(recent_patterns) >= 3:
            avg_duration = sum(p['duration'] for p in recent_patterns) / len(recent_patterns)
            
            if avg_duration > 30000:  # More than 30 seconds
                recommendations.append({
                    'type': 'performance',
                    'issue': 'Build duration is above average',
                    'suggestion': 'Consider using parallel builds or cleaning build cache',
                    'avg_duration_ms': avg_duration
                })
        
        # Analyze peak hours
        hour_performance = defaultdict(list)
        for pattern in self.performance_patterns:
            hour = pattern.get('hour_of_day', 0)
            hour_performance[hour].append(pattern['duration'])
        
        if hour_performance:
            current_hour = datetime.now().hour
            if current_hour in hour_performance:
                avg_current_hour = sum(hour_performance[current_hour]) / len(hour_performance[current_hour])
                overall_avg = sum(
                    sum(durations) / len(durations) 
                    for durations in hour_performance.values()
                ) / len(hour_performance)
                
                if avg_current_hour > overall_avg * 1.2:
                    recommendations.append({
                        'type': 'timing',
                        'issue': 'Current time shows slower build performance',
                        'suggestion': 'Consider running builds during off-peak hours',
                        'current_hour_avg': avg_current_hour,
                        'overall_avg': overall_avg
                    })
        
        return recommendations
    
    def _get_common_causes(self, error_type: str) -> List[str]:
        """Get common causes for specific error type"""
        causes = {
            'compilation_error': [
                "Syntax errors in C code",
                "Missing function declarations",
                "Incorrect header inclusions"
            ],
            'header_error': [
                "Template files not found",
                "Header generation failed",
                "Include path issues"
            ],
            'static_analysis_error': [
                "MISRA-C violations",
                "Automotive coding standard violations",
                "Missing error handling"
            ]
        }
        return causes.get(error_type, ["Unknown causes"])
    
    def _get_prevention_tips(self, error_type: str) -> List[str]:
        """Get prevention tips for specific error type"""
        tips = {
            'compilation_error': [
                "Use consistent coding style",
                "Test compile frequently during development",
                "Use static analysis tools"
            ],
            'header_error': [
                "Verify template files before build",
                "Keep header templates up to date",
                "Check permissions on template directory"
            ],
            'static_analysis_error': [
                "Follow automotive coding standards",
                "Use MISRA-C compliant code patterns",
                "Implement proper error handling"
            ]
        }
        return tips.get(error_type, ["Follow general best practices"])
    
    def _calculate_success_rate_improvement(self, error_type: str) -> Dict[str, float]:
        """Calculate success rate improvement for error type"""
        if error_type not in self.error_patterns:
            return {"current_success_rate": 1.0, "potential_improvement": 0.0}
        
        total_patterns = len(self.error_patterns[error_type])
        if total_patterns == 0:
            return {"current_success_rate": 1.0, "potential_improvement": 0.0}
        
        # Simple calculation based on error frequency
        success_rate = max(0.0, 1.0 - (total_patterns / 100.0))
        potential_improvement = min(0.3, total_patterns / 100.0)  # Max 30% improvement
        
        return {
            "current_success_rate": success_rate,
            "potential_improvement": potential_improvement
        }
    
    def _is_recent(self, timestamp_str: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            cutoff = datetime.now() - timedelta(hours=hours)
            return timestamp > cutoff
        except:
            return False
    
    def add_resolution(self, error_text: str, resolution: str):
        """Add a resolution for a specific error"""
        self.resolution_patterns[error_text] = {
            'resolution': resolution,
            'timestamp': datetime.now().isoformat(),
            'success_count': self.resolution_patterns.get(error_text, {}).get('success_count', 0) + 1
        }
        self._save_patterns()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            'total_error_patterns': sum(len(patterns) for patterns in self.error_patterns.values()),
            'total_success_patterns': sum(len(patterns) for patterns in self.success_patterns.values()),
            'total_performance_patterns': len(self.performance_patterns),
            'total_resolutions': len(self.resolution_patterns),
            'error_types': list(self.error_patterns.keys()),
            'most_common_errors': self._get_most_common_errors(),
            'success_tasks': list(self.success_patterns.keys())
        }
    
    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common error types"""
        error_counts = {
            error_type: len(patterns) 
            for error_type, patterns in self.error_patterns.items()
        }
        
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"error_type": error_type, "count": count} 
            for error_type, count in sorted_errors[:5]
        ]