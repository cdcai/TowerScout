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

#
# EfficientNet B5 secondary classifier
# Looks at detections between x% and y% confidence, rechecks
#

import torch
import torch.nn as nn
import os
import time

from efficientnet_pytorch import EfficientNet
from torchvision import transforms

import PIL
from ts_imgutil import cut_square_detection
from ts_errors import ModelLoadError, ProcessingError
from ts_logging import get_ml_logger
from ts_device import DevicePolicyError, gpu_guard, select_model_device
from ts_paths import get_en_model_dir, get_upload_dir

logger = get_ml_logger()


def _env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


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


class EN_Classifier:

    def __init__(self):
        try:
            logger.info("Initializing EfficientNet classifier")
            
            # Validate model file exists
            path_best = get_en_model_dir() / 'b5_unweighted_best.pt'
            if not path_best.exists():
                raise ModelLoadError(
                    f"EfficientNet model file not found: {path_best}",
                    model_name="EfficientNet-B5",
                    model_path=str(path_best)
                )
            
            try:
                # Build the B5 architecture locally. The packaged TowerScout
                # checkpoint below contains the trained weights, so using
                # from_pretrained() would only add a hidden first-run download.
                self.model = EfficientNet.from_name('efficientnet-b5', num_classes=1000)
                logger.info("EfficientNet base architecture initialized")
            except Exception as e:
                raise ModelLoadError(
                    f"Failed to load EfficientNet base model: {str(e)}",
                    model_name="EfficientNet-B5", 
                    cause=e
                )

            try:
                # replace classification head
                self.model._fc = nn.Sequential(
                    nn.Linear(2048, 512), #b5
                    nn.Linear(512, 1))
                logger.debug("EfficientNet classification head replaced")
            except Exception as e:
                raise ModelLoadError(
                    f"Failed to modify EfficientNet architecture: {str(e)}",
                    model_name="EfficientNet-B5",
                    cause=e
                )

            try:
                load_kwargs = {"map_location": torch.device('cpu')}
                try:
                    checkpoint = torch.load(
                        str(path_best),
                        weights_only=True,
                        **load_kwargs
                    )
                except TypeError:
                    checkpoint = torch.load(str(path_best), **load_kwargs)
                self.model.load_state_dict(checkpoint)
                logger.info("EfficientNet weights loaded on CPU")
            except Exception as e:
                raise ModelLoadError(
                    f"Failed to load EfficientNet weights: {str(e)}",
                    model_name="EfficientNet-B5",
                    model_path=str(path_best),
                    cause=e
                )

            try:
                self.device_selection = select_model_device(
                    "EfficientNet",
                    move_to_cuda=lambda: self.model.to(torch.device('cuda')),
                    move_to_cpu=lambda: self.model.to(torch.device('cpu')),
                )
                self.device = torch.device(self.device_selection.selected_device)
                self.device_label = self.device_selection.selected_device
                self.device_fallback_reason = self.device_selection.fallback_reason
                self.model.eval()
                logger.info(
                    "EfficientNet loaded on %s (policy=%s, fallback=%s)",
                    self.device_label,
                    self.device_selection.requested_policy,
                    self.device_fallback_reason,
                )
            except DevicePolicyError as e:
                raise ModelLoadError(
                    str(e),
                    model_name="EfficientNet-B5",
                    model_path=str(path_best),
                    user_message="EfficientNet device selection failed. Check GPU settings and try again.",
                    cause=e,
                )
            except Exception as e:
                raise ModelLoadError(
                    f"Failed to configure EfficientNet device: {str(e)}",
                    model_name="EfficientNet-B5",
                    model_path=str(path_best),
                    cause=e
                )
                
        except Exception as e:
            if isinstance(e, ModelLoadError):
                raise
            else:
                raise ModelLoadError(
                    f"Unexpected error during EfficientNet initialization: {str(e)}",
                    model_name="EfficientNet-B5",
                    cause=e
                )

        # prepare the image transform
        self.transform = transforms.Compose([
            transforms.Resize([456, 456]),
            transforms.ToTensor(),
            transforms.Normalize(mean=(0.5553, 0.5080, 0.4960), std=(0.1844, 0.1982, 0.2017))
            ])
        self.save_debug_images = _env_flag('TOWERSCOUT_SAVE_EN_DEBUG_IMAGES', False)
        self.batch_size = _env_int('TOWERSCOUT_EN_BATCH_SIZE', 8, minimum=1)
        self.last_classify_stats = {}
        if self.save_debug_images:
            logger.info("EfficientNet debug image capture enabled")
    
    #
    # classify:
    #
    # take batch of one img and multiple detections
    # returns filtered detections (class 0 only)
    #
    # IMPORTANT: Confidence range for running EN.
    def classify(self, img, detections, min_conf=0.25, max_conf=0.65, batch_id=0):
        total_start = time.time()
        stats = {
            'detections_total': len(detections),
            'candidate_count': 0,
            'batch_size': self.batch_size,
            'device': self.device_label,
            'batches': 0,
            'crop_seconds': 0.0,
            'transform_seconds': 0.0,
            'stack_seconds': 0.0,
            'transfer_seconds': 0.0,
            'forward_seconds': 0.0,
            'attach_seconds': 0.0,
            'debug_image_seconds': 0.0,
            'total_seconds': 0.0,
            'device_policy': getattr(getattr(self, 'device_selection', None), 'requested_policy', None),
            'device_fallback_reason': getattr(self, 'device_fallback_reason', None),
        }
        if self.save_debug_images:
            upload_dir = get_upload_dir()

        candidate_tensors = []
        candidate_refs = []
        debug_candidates = []

        for count, det in enumerate(detections):
            x1,y1,x2,y2,conf = det[0:5]

            # only for certain confidence range
            if conf >= min_conf and conf <= max_conf:
                stats['candidate_count'] += 1
                crop_start = time.time()
                det_img = cut_square_detection(img, x1, y1, x2, y2)
                stats['crop_seconds'] += time.time() - crop_start

                # now apply transformations
                transform_start = time.time()
                candidate_tensors.append(self.transform(det_img))
                stats['transform_seconds'] += time.time() - transform_start
                candidate_refs.append((count, det))
                if self.save_debug_images:
                    debug_candidates.append((count, conf, det_img))
                continue

            elif conf < min_conf:
                # print(" No chance: YOLOv5 conf:", round(conf,2))
                # garbage gets thrown out right here
                p2 = 0

            else:
                # >= max_conf does not need review, gets added to results
                # print(" kept: YOLOv5 conf:", round(conf,2))
                p2 = 1

            det.append(p2)

        if candidate_tensors:
            outputs = []
            for offset in range(0, len(candidate_tensors), self.batch_size):
                tensor_batch = candidate_tensors[offset:offset + self.batch_size]
                stack_start = time.time()
                chunk = torch.stack(tensor_batch)
                stats['stack_seconds'] += time.time() - stack_start

                with gpu_guard(self.device_label == 'cuda'):
                    if self.device_label == 'cuda':
                        transfer_start = time.time()
                        chunk = chunk.to(self.device)
                        stats['transfer_seconds'] += time.time() - transfer_start

                    stats['batches'] += 1
                    forward_start = time.time()
                    # This is 1-... because the secondary has class 0 as tower.
                    with torch.inference_mode():
                        batch_outputs = 1 - torch.sigmoid(self.model(chunk).cpu()).view(-1)
                    stats['forward_seconds'] += time.time() - forward_start
                outputs.extend(float(value) for value in batch_outputs.tolist())

            attach_start = time.time()
            output_by_index = {}
            for (count, det), output in zip(candidate_refs, outputs):
                det.append(output)
                output_by_index[count] = output
            stats['attach_seconds'] += time.time() - attach_start

            if self.save_debug_images:
                debug_start = time.time()
                for count, conf, det_img in debug_candidates:
                    output = output_by_index[count]
                    debug_suffix = f"{batch_id+count:02}_conf_{round(conf, 2)}_p2_{round(output, 2)}"
                    img.save(upload_dir / f"img_for_id_{debug_suffix}.jpg")
                    det_img.save(upload_dir / f"id_{debug_suffix}.jpg")
                stats['debug_image_seconds'] += time.time() - debug_start

        stats['total_seconds'] = time.time() - total_start
        self.last_classify_stats = stats
        return stats
