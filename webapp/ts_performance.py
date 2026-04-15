"""
TowerScout Performance Metrics Tracking

This module provides comprehensive performance monitoring for detection workflows.
Tracks timing, memory usage, API calls, and detection metrics.

Author: TowerScout Development Team
Date: March 2026
"""

import time
import csv
import json
import os
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import contextmanager
import psutil
from ts_paths import get_base_dir, get_log_dir

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from ts_logging import get_main_logger

logger = get_main_logger()


class PerformanceMetrics:
    """
    Track performance metrics for a detection workflow.
    
    Captures:
    - Timing: Start, end, duration for each phase
    - Tiles: Count and estimation
    - Detections: Count and confidence distribution
    - Memory: CPU RAM and GPU VRAM usage
    - API Calls: Map provider and geocoding calls
    """
    
    def __init__(self, session_id: str):
        """Initialize performance metrics tracking for a session."""
        self.session_id = session_id
        self.start_time = time.time()
        self.start_datetime = datetime.now()
        
        # Workflow metrics
        self.tile_count = 0
        self.estimated_time_seconds = 0.0
        self.actual_model_time_seconds = 0.0
        self.total_workflow_time_seconds = 0.0
        
        # Detection metrics
        self.detection_count = 0
        self.detections_selected = 0
        self.avg_confidence = 0.0
        
        # Memory metrics
        self.memory_usage_mb = 0.0
        self.gpu_memory_usage_mb = 0.0
        self.peak_memory_mb = 0.0
        self.peak_gpu_memory_mb = 0.0
        
        # API call tracking
        self.map_api_calls = 0
        self.geocoding_api_calls = 0
        
        # Workflow details
        self.map_provider = ""
        self.detection_engine = ""
        self.crop_tiles = False
        
        # Phase timing
        self.phase_timings = {}
        self._phase_start_times = {}
        
        # Process tracking for memory
        self.process = psutil.Process()
        self._initial_memory = self.process.memory_info().rss / (1024 * 1024)
        
    def start_phase(self, phase_name: str):
        """Start timing a workflow phase."""
        self._phase_start_times[phase_name] = time.time()
        logger.debug(f"Performance tracking: Started phase '{phase_name}'")
    
    def end_phase(self, phase_name: str):
        """End timing a workflow phase."""
        if phase_name in self._phase_start_times:
            duration = time.time() - self._phase_start_times[phase_name]
            self.phase_timings[phase_name] = duration
            logger.debug(f"Performance tracking: Phase '{phase_name}' completed in {duration:.2f}s")
            del self._phase_start_times[phase_name]
    
    def update_memory_usage(self):
        """Update memory usage metrics."""
        try:
            # CPU memory
            mem_info = self.process.memory_info()
            current_memory = mem_info.rss / (1024 * 1024)  # Convert to MB
            self.memory_usage_mb = current_memory
            self.peak_memory_mb = max(self.peak_memory_mb, current_memory)
            
            # GPU memory (if available)
            if TORCH_AVAILABLE and torch.cuda.is_available():
                gpu_memory = torch.cuda.memory_allocated() / (1024 * 1024)  # Convert to MB
                self.gpu_memory_usage_mb = gpu_memory
                self.peak_gpu_memory_mb = max(self.peak_gpu_memory_mb, gpu_memory)
        except Exception as e:
            logger.warning(f"Failed to update memory usage: {e}")
    
    def estimate_processing_time(self, tile_count: int, base_time_per_tile: float = 0.3) -> float:
        """
        Estimate processing time based on tile count.
        
        Args:
            tile_count: Number of tiles to process
            base_time_per_tile: Average seconds per tile (default: 0.3s)
            
        Returns:
            Estimated time in seconds
        """
        self.estimated_time_seconds = tile_count * base_time_per_tile
        return self.estimated_time_seconds
    
    def finalize(self):
        """Finalize metrics at end of workflow."""
        self.total_workflow_time_seconds = time.time() - self.start_time
        self.update_memory_usage()
        logger.info(f"Performance metrics finalized for session {self.session_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for logging."""
        return {
            'timestamp': self.start_datetime.isoformat(),
            'session_id': self.session_id,
            'tile_count': self.tile_count,
            'estimated_time_seconds': round(self.estimated_time_seconds, 2),
            'actual_model_time_seconds': round(self.actual_model_time_seconds, 2),
            'total_workflow_time_seconds': round(self.total_workflow_time_seconds, 2),
            'detection_count': self.detection_count,
            'detections_selected': self.detections_selected,
            'avg_confidence': round(self.avg_confidence, 3),
            'memory_usage_mb': round(self.memory_usage_mb, 2),
            'gpu_memory_usage_mb': round(self.gpu_memory_usage_mb, 2),
            'peak_memory_mb': round(self.peak_memory_mb, 2),
            'peak_gpu_memory_mb': round(self.peak_gpu_memory_mb, 2),
            'map_api_calls': self.map_api_calls,
            'geocoding_api_calls': self.geocoding_api_calls,
            'map_provider': self.map_provider,
            'detection_engine': self.detection_engine,
            'crop_tiles': self.crop_tiles,
            'phase_timings': {k: round(v, 2) for k, v in self.phase_timings.items()}
        }
    
    def to_csv_row(self) -> List[Any]:
        """Convert metrics to CSV row."""
        return [
            self.start_datetime.isoformat(),
            self.session_id,
            self.tile_count,
            round(self.estimated_time_seconds, 2),
            round(self.actual_model_time_seconds, 2),
            round(self.total_workflow_time_seconds, 2),
            self.detection_count,
            self.detections_selected,
            round(self.avg_confidence, 3),
            round(self.memory_usage_mb, 2),
            round(self.gpu_memory_usage_mb, 2),
            round(self.peak_memory_mb, 2),
            round(self.peak_gpu_memory_mb, 2),
            self.map_api_calls,
            self.geocoding_api_calls,
            self.map_provider,
            self.detection_engine,
            self.crop_tiles,
            json.dumps({k: round(v, 2) for k, v in self.phase_timings.items()})
        ]


class PerformanceLogger:
    """
    Thread-safe performance metrics logger.
    
    Writes metrics to CSV file with automatic header management.
    """
    
    CSV_HEADERS = [
        'timestamp',
        'session_id',
        'tile_count',
        'estimated_time_seconds',
        'actual_model_time_seconds',
        'total_workflow_time_seconds',
        'detection_count',
        'detections_selected',
        'avg_confidence',
        'memory_usage_mb',
        'gpu_memory_usage_mb',
        'peak_memory_mb',
        'peak_gpu_memory_mb',
        'map_api_calls',
        'geocoding_api_calls',
        'map_provider',
        'detection_engine',
        'crop_tiles',
        'phase_timings_json'
    ]
    
    def __init__(self, log_dir: Optional[str] = None):
        """Initialize performance logger with CSV output."""
        if log_dir is None:
            self.log_dir = get_log_dir()
        else:
            candidate = Path(log_dir)
            if not candidate.is_absolute():
                candidate = get_base_dir() / candidate
            self.log_dir = candidate
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.log_dir / "performance.log"
        self.json_file = self.log_dir / "performance.jsonl"  # JSON Lines format
        
        self._lock = threading.Lock()
        
        # Initialize CSV file with headers if it doesn't exist
        if not self.csv_file.exists():
            self._write_csv_header()
            logger.info(f"Created performance log: {self.csv_file}")
    
    def _write_csv_header(self):
        """Write CSV header to file."""
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.CSV_HEADERS)
        except Exception as e:
            logger.error(f"Failed to write CSV header: {e}")
    
    def log_metrics(self, metrics: PerformanceMetrics):
        """
        Log performance metrics to CSV and JSON files.
        
        Args:
            metrics: PerformanceMetrics object with finalized data
        """
        with self._lock:
            try:
                # Write to CSV
                with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(metrics.to_csv_row())
                
                # Write to JSON Lines (easier for programmatic analysis)
                with open(self.json_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(metrics.to_dict()) + '\n')
                
                logger.info(f"Performance metrics logged for session {metrics.session_id}")
                logger.info(f"  Tiles: {metrics.tile_count} | "
                          f"Model time: {metrics.actual_model_time_seconds:.2f}s | "
                          f"Total time: {metrics.total_workflow_time_seconds:.2f}s | "
                          f"Detections: {metrics.detection_count}")
                
            except Exception as e:
                logger.error(f"Failed to log performance metrics: {e}", exc_info=True)
    
    def get_recent_metrics(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent performance metrics.
        
        Args:
            count: Number of recent entries to retrieve
            
        Returns:
            List of metrics dictionaries
        """
        metrics = []
        try:
            if self.json_file.exists():
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Get last N lines
                    for line in lines[-count:]:
                        metrics.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read performance metrics: {e}")
        
        return metrics
    
    def get_summary_stats(self, last_n: int = 100) -> Dict[str, Any]:
        """
        Calculate summary statistics from recent metrics.
        
        Args:
            last_n: Number of recent entries to analyze
            
        Returns:
            Dictionary with summary statistics
        """
        metrics = self.get_recent_metrics(last_n)
        if not metrics:
            return {}
        
        try:
            total_tiles = sum(m['tile_count'] for m in metrics)
            total_detections = sum(m['detection_count'] for m in metrics)
            avg_model_time = sum(m['actual_model_time_seconds'] for m in metrics) / len(metrics)
            avg_total_time = sum(m['total_workflow_time_seconds'] for m in metrics) / len(metrics)
            
            return {
                'sample_count': len(metrics),
                'total_tiles_processed': total_tiles,
                'total_detections': total_detections,
                'avg_model_time_seconds': round(avg_model_time, 2),
                'avg_total_time_seconds': round(avg_total_time, 2),
                'avg_tiles_per_detection': round(total_tiles / total_detections, 2) if total_detections > 0 else 0,
                'avg_time_per_tile': round(avg_model_time * len(metrics) / total_tiles, 3) if total_tiles > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to calculate summary stats: {e}")
            return {}


# Global performance logger instance
_performance_logger = None
_logger_lock = threading.Lock()


def get_performance_logger() -> PerformanceLogger:
    """Get or create the global performance logger instance."""
    global _performance_logger
    if _performance_logger is None:
        with _logger_lock:
            if _performance_logger is None:
                _performance_logger = PerformanceLogger()
    return _performance_logger


@contextmanager
def track_performance(session_id: str):
    """
    Context manager for tracking performance of a detection workflow.
    
    Usage:
        with track_performance(stable_session_id) as metrics:
            metrics.tile_count = len(tiles)
            metrics.map_provider = "google"
            # ... do work ...
            metrics.detection_count = len(results)
    
    Automatically finalizes and logs metrics on exit.
    """
    metrics = PerformanceMetrics(session_id)
    try:
        yield metrics
    finally:
        metrics.finalize()
        get_performance_logger().log_metrics(metrics)


def log_api_call(metrics: Optional[PerformanceMetrics], call_type: str):
    """
    Log an API call to the metrics tracker.
    
    Args:
        metrics: PerformanceMetrics object or None
        call_type: Type of API call ('map' or 'geocoding')
    """
    if metrics is not None:
        if call_type == 'map':
            metrics.map_api_calls += 1
        elif call_type == 'geocoding':
            metrics.geocoding_api_calls += 1
