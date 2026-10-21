# Performance Metrics - Quick Reference

## Example CSV Output

After running a few detections, your `webapp/logs/performance.log` will look like this:

```csv
timestamp,session_id,tile_count,estimated_time_seconds,actual_model_time_seconds,total_workflow_time_seconds,detection_count,detections_selected,avg_confidence,memory_usage_mb,gpu_memory_usage_mb,peak_memory_mb,peak_gpu_memory_mb,map_api_calls,geocoding_api_calls,map_provider,detection_engine,crop_tiles,phase_timings_json
2026-03-12T10:30:45.123456,1234567890,45,13.5,14.23,22.87,12,8,0.782,1847.50,2048.00,2156.30,2304.50,45,12,google,yolo,True,"{""tile_download"": 5.2, ""model_detection"": 14.23, ""geocoding"": 3.44}"
2026-03-12T10:35:22.654321,1234567891,23,6.9,7.45,12.34,5,4,0.891,1654.25,2048.00,1892.40,2304.50,23,5,azure,yolo,True,"{""tile_download"": 2.8, ""model_detection"": 7.45, ""geocoding"": 2.09}"
```

## What the Metrics Tell You

### Example 1: Normal Performance
```
tile_count: 45
estimated_time_seconds: 13.5
actual_model_time_seconds: 14.23
```
✅ **Good** - Actual time close to estimate (~0.32s per tile)

### Example 2: Slow Processing
```
tile_count: 45
estimated_time_seconds: 13.5
actual_model_time_seconds: 45.0
```
⚠️ **Warning** - 3x slower than expected (~1s per tile)
- Possible CPU-only processing (no GPU)
- High system load
- Memory constraints

### Example 3: Memory Issue
```
peak_memory_mb: 7850
peak_gpu_memory_mb: 7680
```
⚠️ **Warning** - Approaching 8GB limit
- May cause swapping/paging
- Could trigger out-of-memory errors
- Consider reducing batch size

### Example 4: High API Usage
```
tile_count: 45
map_api_calls: 45
geocoding_api_calls: 12
```
ℹ️ **Info** - Expected ratio
- 1 map API call per tile
- Geocoding calls depend on detection count
- Track for cost estimation

## Quick Analysis Commands

### View Recent Performance (PowerShell)
```powershell
Get-Content webapp\logs\performance.log -Tail 10 | ConvertFrom-Csv | Format-Table timestamp, tile_count, actual_model_time_seconds, detection_count
```

### Calculate Average Time Per Tile (PowerShell)
```powershell
$data = Import-Csv webapp\logs\performance.log
$avgTime = ($data | Measure-Object -Property actual_model_time_seconds -Average).Average
$avgTiles = ($data | Measure-Object -Property tile_count -Average).Average
Write-Host "Average time per tile: $($avgTime / $avgTiles) seconds"
```

### Find Slowest Runs (Git Bash)
```bash
tail -n +2 webapp/logs/performance.log | sort -t, -k5 -nr | head -5
# Shows top 5 runs by actual_model_time_seconds (field 5)
```

### Check Memory Usage Trend (Git Bash)
```bash
tail -n 100 webapp/logs/performance.log | cut -d, -f1,10 | tail -20
# Shows last 20 runs with timestamp and memory usage
```

## First Use

1. **Start TowerScout**:
   ```bash
   cd webapp
   python towerscout.py dev
   ```

2. **Run a detection** through the web interface

3. **Check the log file**:
   ```bash
   cat logs/performance.log
   ```

4. **Run the test script**:
   ```bash
   cd ../tests
   python test_performance_metrics.py
   ```

You should see comprehensive metrics for each detection run!

## Tracking Your Hypothesis

You mentioned the model seems slower than before. With these metrics, you can:

1. **Establish baseline**: Run 5-10 detections now, record average times
2. **After each change**: Run same number of detections, compare
3. **Track trends**: Import CSV into Excel, create time series chart
4. **Identify bottlenecks**: Check phase_timings_json to see where time is spent

Example comparison:
```
Before optimization:
  Average model time: 14.5s for 50 tiles = 0.29s/tile

After optimization:
  Average model time: 11.2s for 50 tiles = 0.22s/tile
  
Improvement: 23% faster! ✅
```

## Additional Resources

- **Full Documentation**: See `PERFORMANCE_METRICS_GUIDE.md`
- **Test Script**: Run `tests/test_performance_metrics.py`
- **Implementation**: Check `webapp/ts_performance.py` for details
