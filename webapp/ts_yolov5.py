#
# TowerScout
# A tool for identifying cooling towers from satellite and aerial imagery
#
# TowerScout Team:
# Karen Wong, Gunnar Mein, Thaddeus Segura, Jia Lu
#
# Licensed under CC-BY-NC-SA-4.0
# (see LICENSE.TXT in the root of the repository for details)
#

# YOLOv5 detector class

import math
import os
import time
from importlib import metadata

import torch
from packaging.version import InvalidVersion, Version
from PIL import Image

from ts_imgutil import crop
from ts_errors import ModelLoadError, ProcessingError
from ts_logging import get_ml_logger
from ts_device import DevicePolicyError, gpu_guard, select_model_device
from ts_assets import AssetManifestError, verify_trusted_model
from ts_yolov5_local import load_local_yolov5_model as _load_local_yolov5_model

logger = get_ml_logger()

YOLOV5_RUNTIME_DEPENDENCIES = {
    'numpy': {'max_version_exclusive': '2.0.0'},
    'pillow': {'min_version': '12.3.0'},
    'requests': {'min_version': '2.33.1'},
    'packaging': {},
    'pandas': {},
    'opencv-python': {},
    'seaborn': {},
    'tqdm': {},
    'ultralytics': {},
}


def _env_int(name, default, minimum=1):
    value = os.getenv(name)
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        logger.warning("%s must be an integer; using %s", name, default)
        return default
    if parsed < minimum:
        logger.warning("%s must be >= %s; using %s", name, minimum, default)
        return default
    return parsed


def _format_dependency_mismatch(dist_name, spec, installed_version):
    requirement_parts = []
    min_version = spec.get('min_version')
    max_version_exclusive = spec.get('max_version_exclusive')
    if min_version:
        requirement_parts.append(f'>={min_version}')
    if max_version_exclusive:
        requirement_parts.append(f'<{max_version_exclusive}')
    requirement_text = ', '.join(requirement_parts)
    return (
        f'{dist_name} requires {requirement_text}, '
        f'but TowerScout found {installed_version}.'
    )


def _validate_runtime_dependencies():
    """Fail before model load if the local runtime cannot satisfy TowerScout's YOLO path."""
    mismatches = []

    for dist_name, spec in YOLOV5_RUNTIME_DEPENDENCIES.items():
        try:
            installed_version = metadata.version(dist_name)
        except metadata.PackageNotFoundError:
            mismatches.append(
                f'{dist_name} is not installed but is required by the local YOLOv5 runtime.'
            )
            continue

        try:
            installed = Version(installed_version)
        except InvalidVersion:
            mismatches.append(
                f'{dist_name} has an unreadable installed version: {installed_version}.'
            )
            continue

        min_version = spec.get('min_version')
        if min_version and installed < Version(min_version):
            mismatches.append(
                _format_dependency_mismatch(dist_name, spec, installed_version)
            )
            continue

        max_version_exclusive = spec.get('max_version_exclusive')
        if max_version_exclusive and installed >= Version(max_version_exclusive):
            mismatches.append(
                _format_dependency_mismatch(dist_name, spec, installed_version)
            )

    if mismatches:
        mismatch_text = ' '.join(mismatches)
        raise RuntimeError(
            'TowerScout runtime dependency check failed before YOLO initialization. '
            'Update the local environment with `pip install -r webapp/requirements.txt` '
            f'and rerun detection. {mismatch_text}'
        )


class YOLOv5_Detector:
    def __init__(self, filename):
        try:
            logger.info(f"Initializing YOLOv5 detector with model: {filename}")
            
            # Validate model file exists
            if not os.path.exists(filename):
                raise ModelLoadError(
                    f"YOLOv5 model file not found: {filename}",
                    model_name="YOLOv5",
                    model_path=filename
                )

            _validate_runtime_dependencies()
            try:
                verify_trusted_model(filename)
                logger.info("YOLOv5 model checksum verified")
            except AssetManifestError as e:
                raise ModelLoadError(
                    f"YOLOv5 model trust verification failed: {str(e)}",
                    model_name="YOLOv5",
                    model_path=filename,
                    cause=e,
                )
            
            # Model loading with error handling
            try:
                self.model = _load_local_yolov5_model(filename)
                logger.info("YOLOv5 model loaded successfully")
            except Exception as e:
                raise ModelLoadError(
                    f"Failed to load YOLOv5 model: {str(e)}",
                    model_name="YOLOv5",
                    model_path=filename,
                    cause=e
                )
            
            try:
                self.device_selection = select_model_device(
                    "YOLOv5",
                    move_to_cuda=lambda: self.model.cuda(),
                    move_to_cpu=lambda: self.model.cpu() if hasattr(self.model, "cpu") else None,
                )
            except DevicePolicyError as e:
                raise ModelLoadError(
                    str(e),
                    model_name="YOLOv5",
                    model_path=filename,
                    user_message="YOLOv5 device selection failed. Check GPU settings and try again.",
                    cause=e,
                )

            self.device_label = self.device_selection.selected_device
            self.cuda_available = self.device_selection.torch_cuda_available
            self.cuda_build_version = self.device_selection.torch_cuda_build
            self.cuda_device_name = self.device_selection.cuda_device_name
            self.device_fallback_reason = self.device_selection.fallback_reason

            if self.device_label == "cuda":
                try:
                    t = torch.cuda.get_device_properties(0).total_memory
                    r = torch.cuda.memory_reserved(0)
                    a = torch.cuda.memory_allocated(0)
                    f = r-a  # free inside reserved
                except Exception:
                    f = 0
                logger.info(
                    "CUDA enabled - device=%s build=%s free_gpu_memory=%s bytes",
                    self.cuda_device_name,
                    self.cuda_build_version,
                    f"{f:,}",
                )
                self.batch_size = _env_int("TOWERSCOUT_YOLO_CUDA_BATCH_SIZE", 8)
            else:
                logger.info(
                    "YOLOv5 using CPU (policy=%s, torch_cuda_build=%s, fallback=%s)",
                    self.device_selection.requested_policy,
                    self.cuda_build_version,
                    self.device_fallback_reason,
                )
                self.batch_size = _env_int(
                    "TOWERSCOUT_YOLO_CPU_BATCH_SIZE",
                    torch.get_num_threads(),
                )
            
        except Exception as e:
            if isinstance(e, ModelLoadError):
                raise
            else:
                raise ModelLoadError(
                    f"Unexpected error during YOLOv5 initialization: {str(e)}",
                    model_name="YOLOv5",
                    model_path=filename,
                    cause=e
                )

    def detect(
        self,
        tiles,
        events,
        id,
        crop_tiles=False,
        secondary=None,
        perf_metrics=None,
        progress_callback=None,
    ):
        try:
            logger.info(f"Starting YOLOv5 detection on {len(tiles)} tiles")

            def record_phase(phase_name, started_at):
                if perf_metrics and hasattr(perf_metrics, "add_phase_duration"):
                    perf_metrics.add_phase_duration(phase_name, time.time() - started_at)
            
            # Track memory before detection starts
            if perf_metrics:
                perf_metrics.update_memory_usage()
                if hasattr(perf_metrics, "set_runtime_metadata"):
                    device_selection = getattr(self, "device_selection", None)
                    perf_metrics.set_runtime_metadata(
                        model_device=self.device_label,
                        model_batch_size=self.batch_size,
                        model_tile_count=len(tiles),
                        model_torch_threads=torch.get_num_threads(),
                        model_torch_interop_threads=torch.get_num_interop_threads(),
                        model_torch_cuda_build=getattr(self, "cuda_build_version", None),
                        model_cuda_available=getattr(self, "cuda_available", False),
                        model_cuda_device_name=getattr(self, "cuda_device_name", None),
                        model_device_policy=getattr(device_selection, "requested_policy", None),
                        model_configured_device_policy=getattr(device_selection, "configured_policy", None),
                        model_device_fallback_reason=getattr(self, "device_fallback_reason", None),
                        secondary_classifier_enabled=secondary is not None,
                        secondary_classifier_device=getattr(secondary, "device_label", None),
                        secondary_classifier_batch_size=getattr(secondary, "batch_size", None),
                    )
            
            # Inference in batches
            tile_count = len(tiles)
            chunks = math.ceil(tile_count/self.batch_size)
            results = []
            count = 0
            secondary_detection_total = 0
            secondary_candidate_total = 0
            secondary_batch_total = 0
            secondary_total_seconds = 0.0

            def record_secondary_stats(stats):
                nonlocal secondary_detection_total
                nonlocal secondary_candidate_total
                nonlocal secondary_batch_total
                nonlocal secondary_total_seconds

                if not isinstance(stats, dict):
                    return

                if perf_metrics and hasattr(perf_metrics, "add_phase_duration"):
                    phase_map = {
                        'crop_seconds': 'model_secondary_crop',
                        'transform_seconds': 'model_secondary_transform',
                        'stack_seconds': 'model_secondary_stack',
                        'transfer_seconds': 'model_secondary_transfer',
                        'forward_seconds': 'model_secondary_forward',
                        'attach_seconds': 'model_secondary_attach',
                        'debug_image_seconds': 'model_secondary_debug_image_save',
                    }
                    for stat_key, phase_name in phase_map.items():
                        duration = stats.get(stat_key, 0.0)
                        if duration:
                            perf_metrics.add_phase_duration(phase_name, duration)

                secondary_detection_total += int(stats.get('detections_total') or 0)
                secondary_candidate_total += int(stats.get('candidate_count') or 0)
                secondary_batch_total += int(stats.get('batches') or 0)
                secondary_total_seconds += float(stats.get('total_seconds') or 0.0)

                if perf_metrics and hasattr(perf_metrics, "set_runtime_metadata"):
                    metadata = {
                        "secondary_classifier_detection_count": secondary_detection_total,
                        "secondary_classifier_candidate_count": secondary_candidate_total,
                        "secondary_classifier_batches": secondary_batch_total,
                        "secondary_classifier_device": stats.get('device'),
                        "secondary_classifier_batch_size": stats.get('batch_size'),
                    }
                    if secondary_candidate_total:
                        metadata["secondary_classifier_seconds_per_candidate"] = (
                            secondary_total_seconds / secondary_candidate_total
                        )
                    perf_metrics.set_runtime_metadata(**metadata)

            for i in range(0, tile_count, self.batch_size):
                try:
                    # make a batch of image urls
                    tile_batch = tiles[i:i+self.batch_size]
                    logger.debug(f"Processing batch {i//self.batch_size + 1}/{chunks}: {len(tile_batch)} tiles")
                    
                    # Load images with error handling
                    img_batch = []
                    image_loading_start = time.time()
                    for tile in tile_batch:
                        try:
                            img_batch.append(Image.open(tile['filename']))
                        except Exception as e:
                            logger.error(f"Failed to load image {tile['filename']}: {e}")
                            raise ProcessingError(
                                f"Image loading failed: {tile['filename']}",
                                operation="image_loading",
                                cause=e
                            )
                    record_phase('model_tile_image_loading', image_loading_start)

                    # crop the tiles if requested
                    if crop_tiles:
                        try:
                            crop_start = time.time()
                            img_batch = [crop(img) for img in img_batch]
                            record_phase('model_tile_cropping', crop_start)
                        except Exception as e:
                            logger.error(f"Image cropping failed: {e}")
                            raise ProcessingError(
                                "Image cropping operation failed",
                                operation="image_cropping",
                                cause=e
                            )

                    # retain a copy of the images
                    if secondary is not None:
                        image_copy_start = time.time()
                        img_batch2 = [img.copy() for img in img_batch]
                        record_phase('model_secondary_image_copy', image_copy_start)
                    else:
                        img_batch2 = [None] * len(img_batch)

                    # Shared GPU guard protects all GPU model stages in this process.
                    with gpu_guard(self.device_label == "cuda"):
                        try:
                            inference_start = time.time()
                            result_obj = self.model(img_batch)
                            record_phase('model_yolo_inference', inference_start)
                        except Exception as e:
                            logger.error(f"YOLOv5 model inference failed: {e}")
                            raise ProcessingError(
                                f"Model inference failed: {str(e)}",
                                operation="yolo_inference",
                                tile_count=len(tile_batch),
                                cause=e
                            )

                        # check for exit signal
                        if events.query(id):
                            logger.info("Detection aborted by user request")
                            return []

                        # Keep the GPU guard through extraction and CPU conversion so
                        # asynchronous CUDA work is complete before other model stages run.
                        result_extraction_start = time.time()
                        results_raw = result_obj.xyxyn
                        record_phase('model_result_extraction', result_extraction_start)

                        batch_results_cpu = []
                        for result in results_raw:
                            result_tensor_start = time.time()
                            batch_results_cpu.append(result.cpu().numpy().tolist())
                            record_phase('model_result_tensor_conversion', result_tensor_start)

                    # result is tile by tile
                    for (tile, img, results_cpu) in zip(tile_batch, img_batch2, batch_results_cpu):
                        try:
                            # secondary classifier processing
                            if secondary is not None:
                                try:
                                    # classifier will append its own prob to every detection
                                    secondary_start = time.time()
                                    secondary_stats = secondary.classify(img, results_cpu, batch_id=count)
                                    record_phase('model_secondary_classifier_inference', secondary_start)
                                    record_secondary_stats(secondary_stats)
                                    count += 1
                                except Exception as e:
                                    logger.error(f"Secondary classifier failed: {e}")
                                    # Continue without secondary classification
                                    count += 1

                            result_processing_start = time.time()
                            tile_results = [{
                                'x1': item[0],
                                'y1':item[1],
                                'x2':item[2],
                                'y2':item[3],
                                'conf':item[4],
                                'class':int(item[5]),
                                'class_name':result_obj.names[int(item[5])],
                                'secondary':item[6] if len(item) > 6 else 1
                                } for item in results_cpu]
                            results.append(tile_results)

                            # record the detections in the tile
                            boxes = []
                            for tr in tile_results:
                                box = "0 " + \
                                    str((tr['x1']+tr['x2'])/2) + \
                                    " "+str((tr['y1']+tr['y2'])/2) + \
                                    " "+str(tr['x2']-tr['x1']) +\
                                    " "+str(tr['y2']-tr['y1'])+"\n"
                                boxes.append(box)
                            tile['detections'] = boxes
                            record_phase('model_result_conversion_filtering', result_processing_start)
                            
                        except Exception as e:
                            logger.error(f"Result processing failed for tile: {e}")
                            # Continue processing other tiles
                            continue

                    logger.debug(f"Batch {i//self.batch_size + 1}/{chunks} completed")

                    if progress_callback is not None:
                        try:
                            progress_callback(
                                batches_completed=(i // self.batch_size) + 1,
                                batches_total=chunks,
                                tiles_processed=min(tile_count, i + len(tile_batch)),
                                tiles_total=tile_count
                            )
                        except Exception as callback_error:
                            logger.debug(f"Progress callback failed: {callback_error}")
                    
                    # Track memory usage after batch (helpful for monitoring memory leaks)
                    if perf_metrics:
                        perf_metrics.update_memory_usage()
                    
                except Exception as e:
                    if isinstance(e, ProcessingError):
                        raise
                    else:
                        logger.error(f"Unexpected error in batch processing: {e}")
                        raise ProcessingError(
                            f"Batch processing failed: {str(e)}",
                            operation="batch_processing",
                            cause=e
                        )

            logger.info(f"YOLOv5 detection completed: {tile_count} tiles processed")
            return results
            
        except Exception as e:
            if isinstance(e, ProcessingError):
                raise
            else:
                logger.error(f"Unexpected error in YOLOv5 detection: {str(e)}", exc_info=True)
                raise ProcessingError(
                    f"YOLOv5 detection system error: {str(e)}",
                    operation="detect",
                    tile_count=len(tiles),
                    cause=e
                )
