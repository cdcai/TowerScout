#
# TowerScout
# A tool for identifying cooling towers from satellite and aerial imagery
#

import logging
import os
import sys
from contextlib import contextmanager
from pathlib import Path

YOLOV5_SOURCE_REPO = "ultralytics/yolov5"
YOLOV5_SOURCE_REF = "1d62daa3c6b8ec15fdb319c0a2e341d8b56ec86c"
YOLOV5_LOCAL_SOURCE_DIR = Path(__file__).resolve().parent / "vendor" / "yolov5_local"
YOLOV5_LOCAL_PACKAGE = "vendor.yolov5_local"
YOLO_AUTOINSTALL_ENV_VAR = "YOLO_AUTOINSTALL"
YOLOV5_AUTOINSTALL_ENV_VAR = "YOLOv5_AUTOINSTALL"
YOLO_AUTOINSTALL_ENV_VARS = (
    YOLO_AUTOINSTALL_ENV_VAR,
    YOLOV5_AUTOINSTALL_ENV_VAR,
)

YOLOV5_LEGACY_MODULE_ALIASES = (
    ("models", "vendor.yolov5_local.models"),
    ("models.common", "vendor.yolov5_local.models.common"),
    ("models.experimental", "vendor.yolov5_local.models.experimental"),
    ("models.yolo", "vendor.yolov5_local.models.yolo"),
    ("utils", "vendor.yolov5_local.utils"),
    ("utils.augmentations", "vendor.yolov5_local.utils.augmentations"),
    ("utils.autoanchor", "vendor.yolov5_local.utils.autoanchor"),
    ("utils.dataloaders", "vendor.yolov5_local.utils.dataloaders"),
    ("utils.downloads", "vendor.yolov5_local.utils.downloads"),
    ("utils.general", "vendor.yolov5_local.utils.general"),
    ("utils.metrics", "vendor.yolov5_local.utils.metrics"),
    ("utils.plots", "vendor.yolov5_local.utils.plots"),
    ("utils.torch_utils", "vendor.yolov5_local.utils.torch_utils"),
    ("utils.triton", "vendor.yolov5_local.utils.triton"),
)


def ensure_local_yolov5_source_available():
    """Fail fast if the vendored YOLO snapshot is missing from the workspace."""
    if YOLOV5_LOCAL_SOURCE_DIR.is_dir():
        return

    raise RuntimeError(
        "TowerScout local YOLOv5 source snapshot is missing. "
        f"Expected vendored runtime under {YOLOV5_LOCAL_SOURCE_DIR} "
        f"from {YOLOV5_SOURCE_REPO}@{YOLOV5_SOURCE_REF}."
    )


@contextmanager
def disable_yolo_autoinstall():
    """Prevent vendored YOLO code from attempting runtime package mutation."""
    previous_values = {
        env_var: os.environ.get(env_var)
        for env_var in YOLO_AUTOINSTALL_ENV_VARS
    }

    for env_var in YOLO_AUTOINSTALL_ENV_VARS:
        os.environ[env_var] = "false"

    try:
        yield
    finally:
        for env_var, previous_value in previous_values.items():
            if previous_value is None:
                os.environ.pop(env_var, None)
            else:
                os.environ[env_var] = previous_value


@contextmanager
def alias_legacy_yolov5_modules():
    """Expose vendored modules under legacy upstream names while loading pickled weights."""
    previous_modules = {
        legacy_name: sys.modules.get(legacy_name)
        for legacy_name, _ in YOLOV5_LEGACY_MODULE_ALIASES
    }

    try:
        for legacy_name, packaged_name in YOLOV5_LEGACY_MODULE_ALIASES:
            try:
                sys.modules[legacy_name] = __import__(packaged_name, fromlist=["*"])
            except ModuleNotFoundError:
                continue
        yield
    finally:
        for legacy_name, previous_module in previous_modules.items():
            if previous_module is None:
                sys.modules.pop(legacy_name, None)
            else:
                sys.modules[legacy_name] = previous_module


def load_local_yolov5_model(filename, autoshape=True, verbose=False, device=None):
    """Load TowerScout's vendored YOLOv5 runtime from local source."""
    ensure_local_yolov5_source_available()
    with disable_yolo_autoinstall():
        from vendor.yolov5_local.models.common import AutoShape, DetectMultiBackend
        from vendor.yolov5_local.models.experimental import attempt_load
        from vendor.yolov5_local.models.yolo import (
            ClassificationModel,
            SegmentationModel,
        )
        from vendor.yolov5_local.utils.general import LOGGER
        from vendor.yolov5_local.utils.torch_utils import select_device

        previous_level = LOGGER.level
        if not verbose:
            LOGGER.setLevel(logging.WARNING)

        path = Path(filename)
        try:
            with alias_legacy_yolov5_modules():
                resolved_device = select_device(device)

                def _apply_autoshape_if_supported(model):
                    if not autoshape:
                        return model

                    wrapped_model = model.model if isinstance(model, DetectMultiBackend) else model
                    if isinstance(wrapped_model, ClassificationModel):
                        LOGGER.warning(
                            "WARNING: YOLOv5 ClassificationModel is not AutoShape compatible. "
                            "Inference must pass BCHW torch tensors to this model."
                        )
                        return model
                    if isinstance(wrapped_model, SegmentationModel):
                        LOGGER.warning(
                            "WARNING: YOLOv5 SegmentationModel is not AutoShape compatible."
                        )
                        return model

                    return AutoShape(model, verbose=verbose)

                try:
                    model = DetectMultiBackend(path, device=resolved_device, fuse=autoshape)
                except Exception as detect_multi_backend_error:
                    LOGGER.warning(
                        f"DetectMultiBackend load failed for {path}; "
                        f"falling back to direct PyTorch weight load: {detect_multi_backend_error}"
                    )
                    model = attempt_load(path, device=resolved_device, fuse=False)

                model = _apply_autoshape_if_supported(model)
                return model.to(resolved_device)
        finally:
            LOGGER.setLevel(previous_level)
