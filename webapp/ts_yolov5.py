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
import threading
from importlib import metadata

import torch
from packaging.version import InvalidVersion, Version
from PIL import Image

from ts_imgutil import crop
from ts_errors import ModelLoadError, ProcessingError
from ts_logging import get_ml_logger
from ts_yolov5_local import load_local_yolov5_model as _load_local_yolov5_model

logger = get_ml_logger()

YOLOV5_RUNTIME_DEPENDENCIES = {
    'numpy': {'max_version_exclusive': '2.0.0'},
    'pillow': {'min_version': '10.3.0'},
    'requests': {'min_version': '2.32.2'},
    'packaging': {},
    'pandas': {},
    'opencv-python': {},
    'seaborn': {},
    'tqdm': {},
    'ultralytics': {},
}


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
            
            # GPU/CPU configuration with error handling
            if torch.cuda.is_available():
                try:
                    self.model.cuda()
                    t = torch.cuda.get_device_properties(0).total_memory
                    r = torch.cuda.memory_reserved(0)
                    a = torch.cuda.memory_allocated(0)
                    f = r-a  # free inside reserved
                    logger.info(f"CUDA enabled - Free GPU memory: {f:,} bytes")
                    self.batch_size = 8  # For our Tesla K8, this means 8 batches can run in parallel
                except Exception as e:
                    logger.warning(f"CUDA setup failed, falling back to CPU: {e}")
                    self.batch_size = torch.get_num_threads()  # tuned to threads
            else:
                logger.info("CUDA not available, using CPU")
                self.batch_size = torch.get_num_threads()  # tuned to threads
            
            # add a semaphore so we don't run out of GPU memory between multiple clients
            self.semaphore = threading.Semaphore(8)
            
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
            
            # Track memory before detection starts
            if perf_metrics:
                perf_metrics.update_memory_usage()
            
            # Inference in batches
            tile_count = len(tiles)
            chunks = math.ceil(tile_count/self.batch_size)
            results = []
            count = 0

            for i in range(0, tile_count, self.batch_size):
                try:
                    # make a batch of image urls
                    tile_batch = tiles[i:i+self.batch_size]
                    logger.debug(f"Processing batch {i//self.batch_size + 1}/{chunks}: {len(tile_batch)} tiles")
                    
                    # Load images with error handling
                    img_batch = []
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

                    # crop the tiles if requested
                    if crop_tiles:
                        try:
                            img_batch = [crop(img) for img in img_batch]
                        except Exception as e:
                            logger.error(f"Image cropping failed: {e}")
                            raise ProcessingError(
                                "Image cropping operation failed",
                                operation="image_cropping",
                                cause=e
                            )

                    # retain a copy of the images
                    if secondary is not None:
                        img_batch2 = [img.copy() for img in img_batch]
                    else:
                        img_batch2 = [None] * len(img_batch)

                    # detect with semaphore protection
                    with self.semaphore:  # limit the number of jobs going on in parallel, because of GPU mem
                        try:
                            result_obj = self.model(img_batch)
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

                    # get the important part
                    results_raw = result_obj.xyxyn

                    # result is tile by tile
                    for (tile, img, result) in zip(tile_batch, img_batch2, results_raw):
                        try:
                            results_cpu = result.cpu().numpy().tolist()

                            # secondary classifier processing
                            if secondary is not None:
                                try:
                                    # classifier will append its own prob to every detection
                                    secondary.classify(img, results_cpu, batch_id=count)
                                    count += 1
                                except Exception as e:
                                    logger.error(f"Secondary classifier failed: {e}")
                                    # Continue without secondary classification
                                    count += 1

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
