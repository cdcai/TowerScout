"""
Diagnostic helper for TowerScout performance metrics tracking.

Run this after making a few detection requests to verify performance logging
is working correctly without depending on the current working directory.
"""

from pathlib import Path
import sys


WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"
sys.path.insert(0, str(WEBAPP_DIR))

from ts_paths import get_log_dir
from ts_performance import get_performance_logger


def test_performance_logging():
    """Print recent performance metrics from the normalized log location."""
    print("Testing Performance Metrics System")
    print("=" * 60)

    logger = get_performance_logger()
    expected_log_dir = get_log_dir()

    csv_file = logger.csv_file
    json_file = logger.json_file

    print("\nLog Files:")
    print(f"   Expected log dir: {expected_log_dir}")
    print(f"   Logger log dir: {logger.log_dir}")
    print(f"   CSV: {csv_file}")
    print(f"   Exists: {csv_file.exists()}")
    print(f"   JSON: {json_file}")
    print(f"   Exists: {json_file.exists()}")

    if logger.log_dir.resolve() != expected_log_dir.resolve():
        print("\nWARNING: Performance logger is not using the normalized app-anchored log directory.")
        return

    if not csv_file.exists():
        print("\nWARNING: No performance data yet. Make a detection request first.")
        return

    print("\nRecent Performance Metrics:")
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

    print("\nSummary Statistics (last 100 runs):")
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
    print("Performance metrics test complete")


def check_csv_format():
    """Print a compact CSV format check from the normalized log location."""
    logger = get_performance_logger()
    expected_log_dir = get_log_dir()

    if logger.log_dir.resolve() != expected_log_dir.resolve():
        print("WARNING: CSV format check skipped because logger path is not normalized.")
        return

    if not logger.csv_file.exists():
        print("WARNING: CSV file does not exist yet")
        print(f"   Expected log dir: {expected_log_dir}")
        return

    print("\nCSV Format Check:")
    with open(logger.csv_file, "r", encoding="utf-8") as file_handle:
        header = file_handle.readline().strip()
        print(f"   Header: {header[:80]}...")

        first_row = file_handle.readline().strip()
        if first_row:
            print(f"   Sample row: {first_row[:100]}...")
            print("   CSV format looks good")
        else:
            print("   No data rows yet")


if __name__ == "__main__":
    test_performance_logging()
    check_csv_format()
