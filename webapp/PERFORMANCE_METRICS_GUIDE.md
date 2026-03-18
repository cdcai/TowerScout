# TowerScout Performance Metrics System

## Overview

The performance metrics system provides comprehensive tracking of detection workflow performance, including timing, memory usage, API calls, and detection statistics.

## Features

### Captured Metrics

For each detection workflow, the system captures:

1. **Timing Metrics**
   - Timestamp (ISO 8601 format)
   - Session ID
   - Estimated processing time (based on tile count)
   - Actual model processing time (YOLOv5 + EfficientNet)
   - Total workflow time (end-to-end)
   - Phase-specific timings (tile download, model detection, geocoding)

2. **Tile & Detection Metrics**
   - Number of tiles processed
   - Number of detections found
   - Number of detections selected (after filtering)
   - Average confidence score

3. **Memory Usage**
   - CPU RAM usage (MB)
   - GPU VRAM usage (MB) - when available
   - Peak memory usage during workflow

4. **API Call Tracking**
   - Map provider API calls (tile downloads)
   - Geocoding API calls (address lookups)

5. **Configuration**
   - Map provider used (google/azure)
   - Detection engine (yolo/yolo+en)
   - Tile cropping enabled/disabled

## Output Files

Performance metrics are logged to two files in `webapp/logs/`:

1. **performance.log** - CSV format for spreadsheet analysis
   - Easy to import into Excel, Google Sheets
   - Calculate trends, averages, performance over time
   - Compare different configurations

2. **performance.jsonl** - JSON Lines format for programmatic analysis
   - One JSON object per line
   - Easy to parse with Python/JavaScript
   - Queryable with jq or other tools

## Usage

### Automatic Logging

Performance metrics are **automatically captured** for every detection request. No manual intervention required.

When you run a detection through the web interface:
1. User submits detection request
2. System tracks all metrics throughout workflow
3. Metrics are automatically logged on completion

### Viewing Metrics

#### Option 1: Excel/Google Sheets

1. Open `webapp/logs/performance.log` in Excel or Google Sheets
2. CSV format with headers makes it easy to:
   - Sort by timestamp, tile count, detection time
   - Create charts showing performance trends
   - Calculate averages and statistics
   - Filter by map provider or detection engine

#### Option 2: Python Script

Run the test script to view recent metrics:

```bash
cd tests
python test_performance_metrics.py
```

This displays:
- Recent detection runs (last 5)
- Summary statistics (last 100)
- CSV format validation

#### Option 3: Programmatic Access

```python
from ts_performance import get_performance_logger

logger = get_performance_logger()

# Get recent metrics
recent = logger.get_recent_metrics(count=10)
for metrics in recent:
    print(f"Run at {metrics['timestamp']}: "
          f"{metrics['tile_count']} tiles, "
          f"{metrics['detection_count']} detections, "
          f"{metrics['actual_model_time_seconds']}s")

# Get summary statistics
stats = logger.get_summary_stats(last_n=100)
print(f"Average model time: {stats['avg_model_time_seconds']}s")
print(f"Average time per tile: {stats['avg_time_per_tile']}s")
```

## Performance Analysis Examples

### Compare Detection Speed Over Time

1. Open `performance.log` in Excel
2. Create a scatter plot with:
   - X-axis: timestamp
   - Y-axis: actual_model_time_seconds
3. Add trend line to see if performance is degrading

### Analyze Memory Usage

```python
import json

with open('webapp/logs/performance.jsonl', 'r') as f:
    metrics = [json.loads(line) for line in f]

# Find runs with high memory usage
high_memory = [m for m in metrics if m['peak_memory_mb'] > 2000]
print(f"Runs with >2GB memory: {len(high_memory)}")

# Check correlation between tiles and memory
for m in metrics:
    print(f"{m['tile_count']} tiles → {m['peak_memory_mb']:.0f}MB")
```

### Compare Map Providers

```bash
# Using jq to query JSON Lines
cat webapp/logs/performance.jsonl | jq -r 'select(.map_provider == "google") | .actual_model_time_seconds' | awk '{s+=$1} END {print "Google avg:", s/NR}'
cat webapp/logs/performance.jsonl | jq -r 'select(.map_provider == "azure") | .actual_model_time_seconds' | awk '{s+=$1} END {print "Azure avg:", s/NR}'
```

### Estimate API Costs

```python
# Calculate total API calls
with open('webapp/logs/performance.jsonl', 'r') as f:
    total_map_calls = 0
    total_geocoding_calls = 0
    
    for line in f:
        m = json.loads(line)
        total_map_calls += m['map_api_calls']
        total_geocoding_calls += m['geocoding_api_calls']

# Google Maps pricing (example rates)
map_cost = total_map_calls * 0.002  # $2 per 1000 requests
geocoding_cost = total_geocoding_calls * 0.005  # $5 per 1000 requests

print(f"Estimated costs:")
print(f"  Map API: ${map_cost:.2f}")
print(f"  Geocoding API: ${geocoding_cost:.2f}")
print(f"  Total: ${map_cost + geocoding_cost:.2f}")
```

## Identifying Performance Issues

### Slow Detection Times

If `actual_model_time_seconds` is higher than expected:

1. **Check tile count** - More tiles = more time
   - Expected: ~0.3 seconds per tile
   - If much higher: Model may be running on CPU instead of GPU

2. **Check memory usage** - High memory can slow processing
   - `peak_memory_mb` approaching system limits
   - May trigger swapping/paging

3. **Compare with estimated time** - Large deviation indicates issue
   - `estimated_time_seconds` is baseline
   - If actual is 2-3x higher, investigate

### Memory Leaks

If `peak_memory_mb` increases over time:

1. Sort metrics by timestamp
2. Check if memory increases with consecutive runs
3. Look for patterns (specific tile counts, providers)

### API Rate Limiting

If detection time includes long tile download phase:

1. Check `phase_timings_json` field
2. Compare `tile_download` vs `model_detection` times
3. High download time may indicate rate limiting

## CSV Fields Reference

| Field | Description | Example |
|-------|-------------|---------|
| `timestamp` | ISO 8601 timestamp | 2026-03-12T10:30:45.123456 |
| `session_id` | Unique session identifier | 4567890123 |
| `tile_count` | Number of tiles processed | 45 |
| `estimated_time_seconds` | Estimated processing time | 13.5 |
| `actual_model_time_seconds` | Actual model processing time | 14.2 |
| `total_workflow_time_seconds` | End-to-end workflow time | 22.8 |
| `detection_count` | Total detections found | 12 |
| `detections_selected` | Detections meeting threshold | 8 |
| `avg_confidence` | Average confidence score | 0.78 |
| `memory_usage_mb` | CPU RAM usage | 1847.5 |
| `gpu_memory_usage_mb` | GPU VRAM usage | 2048.0 |
| `peak_memory_mb` | Peak CPU RAM | 2156.3 |
| `peak_gpu_memory_mb` | Peak GPU VRAM | 2304.5 |
| `map_api_calls` | Map tile downloads | 45 |
| `geocoding_api_calls` | Geocoding requests | 12 |
| `map_provider` | Provider used | google |
| `detection_engine` | Engine used | yolo |
| `crop_tiles` | Tiles cropped | True |
| `phase_timings_json` | Phase timing breakdown | {"tile_download": 5.2, "model_detection": 14.2, "geocoding": 3.4} |

## Development Tips

### Adding Custom Metrics

To track additional metrics, modify `ts_performance.py`:

```python
class PerformanceMetrics:
    def __init__(self, session_id: str):
        # ... existing code ...
        
        # Add your custom metric
        self.custom_metric = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            # ... existing fields ...
            'custom_metric': self.custom_metric
        }
        return result
```

Update `PerformanceLogger.CSV_HEADERS` to include the new field.

### Phase Timing

To track timing for a specific phase:

```python
perf_metrics.start_phase('my_custom_phase')
# ... do work ...
perf_metrics.end_phase('my_custom_phase')
```

This will be included in the `phase_timings_json` field.

## Troubleshooting

### No performance.log file

If the log file doesn't exist:
- Run at least one detection request
- Check `webapp/logs/` directory exists
- Verify write permissions

### Empty or incomplete metrics

If metrics are missing fields:
- Check for exceptions during workflow
- Review logs for error messages
- Verify all phases complete successfully

### High memory usage reported

If memory values seem incorrect:
- Verify `psutil` is installed: `pip install psutil`
- Check if GPU memory tracking requires PyTorch with CUDA
- Memory values are in MB, not GB

## Best Practices

1. **Regular Monitoring** - Review metrics weekly to catch performance regressions early

2. **Baseline Establishment** - After each major change, record baseline metrics for comparison

3. **A/B Testing** - When testing optimizations, run multiple workflows and compare metrics

4. **Archival** - Periodically back up `performance.log` before it gets too large

5. **Correlation Analysis** - Look for patterns between provider choice, tile count, and performance

## Future Enhancements

Planned improvements:
- Web dashboard for real-time metric visualization
- Automated alerting for performance degradation
- Historical comparison reports
- Export to external monitoring systems (Prometheus, etc.)
