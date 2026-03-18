"""
Test script for performance metrics tracking

Run this after making a few detection requests to verify performance
logging is working correctly.

Usage:
    cd tests && python test_performance_metrics.py
    OR
    cd webapp && python ../tests/test_performance_metrics.py
"""

import sys
import os
from pathlib import Path

# Add webapp to path
webapp_dir = os.path.join(os.path.dirname(__file__), '..', 'webapp')
sys.path.insert(0, webapp_dir)

# Change to webapp directory so performance logger finds correct log path
original_dir = os.getcwd()
os.chdir(webapp_dir)

from ts_performance import get_performance_logger, PerformanceLogger
import json

def test_performance_logging():
    """Test that performance metrics are being logged correctly."""
    print("🧪 Testing Performance Metrics System")
    print("=" * 60)
    
    logger = get_performance_logger()
    
    # Check if log files exist
    csv_file = logger.csv_file
    json_file = logger.json_file
    
    print(f"\n📁 Log Files:")
    print(f"   CSV: {csv_file}")
    print(f"   Exists: {csv_file.exists()}")
    print(f"   JSON: {json_file}")
    print(f"   Exists: {json_file.exists()}")
    
    if not csv_file.exists():
        print("\n⚠️  No performance data yet. Make a detection request first.")
        return
    
    # Read recent metrics
    print(f"\n📊 Recent Performance Metrics:")
    recent = logger.get_recent_metrics(5)
    
    if not recent:
        print("   No metrics found")
        return
    
    for i, metrics in enumerate(recent, 1):
        print(f"\n   Entry {i}:")
        print(f"      Timestamp: {metrics['timestamp']}")
        print(f"      Tile Count: {metrics['tile_count']}")
        print(f"      Estimated Time: {metrics['estimated_time_seconds']}s")
        print(f"      Actual Model Time: {metrics['actual_model_time_seconds']}s")
        print(f"      Total Workflow Time: {metrics['total_workflow_time_seconds']}s")
        print(f"      Detection Count: {metrics['detection_count']}")
        print(f"      Selected: {metrics['detections_selected']}")
        print(f"      Avg Confidence: {metrics['avg_confidence']}")
        print(f"      Memory Usage: {metrics['memory_usage_mb']}MB")
        print(f"      GPU Memory: {metrics['gpu_memory_usage_mb']}MB")
        print(f"      Peak Memory: {metrics['peak_memory_mb']}MB")
        print(f"      Map API Calls: {metrics['map_api_calls']}")
        print(f"      Geocoding API Calls: {metrics['geocoding_api_calls']}")
        print(f"      Provider: {metrics['map_provider']}")
        print(f"      Engine: {metrics['detection_engine']}")
    
    # Get summary statistics
    print(f"\n📈 Summary Statistics (last 100 runs):")
    stats = logger.get_summary_stats(100)
    
    if stats:
        print(f"   Sample Count: {stats['sample_count']}")
        print(f"   Total Tiles Processed: {stats['total_tiles_processed']}")
        print(f"   Total Detections: {stats['total_detections']}")
        print(f"   Avg Model Time: {stats['avg_model_time_seconds']}s")
        print(f"   Avg Total Time: {stats['avg_total_time_seconds']}s")
        print(f"   Avg Tiles per Detection: {stats['avg_tiles_per_detection']}")
        print(f"   Avg Time per Tile: {stats['avg_time_per_tile']}s")
    
    print("\n" + "=" * 60)
    print("✅ Performance metrics test complete")


def check_csv_format():
    """Check that CSV format is correct."""
    logger = get_performance_logger()
    
    if not logger.csv_file.exists():
        print("⚠️  CSV file doesn't exist yet")
        return
    
    print("\n📋 CSV Format Check:")
    with open(logger.csv_file, 'r', encoding='utf-8') as f:
        header = f.readline().strip()
        print(f"   Header: {header[:80]}...")
        
        # Read first data row
        first_row = f.readline().strip()
        if first_row:
            print(f"   Sample row: {first_row[:100]}...")
            print(f"   ✅ CSV format looks good")
        else:
            print(f"   ⚠️  No data rows yet")


if __name__ == '__main__':
    try:
        test_performance_logging()
        check_csv_format()
    finally:
        # Restore original directory
        os.chdir(original_dir)


if __name__ == '__main__':
    test_performance_logging()
    check_csv_format()
