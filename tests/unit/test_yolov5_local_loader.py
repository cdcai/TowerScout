import os
import sys
import types
from contextlib import nullcontext
from importlib import metadata
from unittest.mock import Mock, patch

import pytest

from ts_errors import ModelLoadError
from ts_yolov5 import YOLOv5_Detector, _validate_runtime_dependencies
from ts_yolov5_local import (
    YOLOV5_AUTOINSTALL_ENV_VAR,
    YOLOV5_LOCAL_PACKAGE,
    YOLO_AUTOINSTALL_ENV_VAR,
    disable_yolo_autoinstall,
    load_local_yolov5_model,
)


def test_yolov5_detector_uses_local_loader_not_torch_hub():
    recovered_model = Mock()

    with patch("ts_yolov5.os.path.exists", return_value=True), \
         patch("ts_yolov5._load_local_yolov5_model", return_value=recovered_model) as mock_local_load, \
         patch("ts_yolov5.torch.hub.load") as mock_hub_load, \
         patch("ts_yolov5.torch.cuda.is_available", return_value=False), \
         patch("ts_yolov5.torch.get_num_threads", return_value=4):
        detector = YOLOv5_Detector("newest.pt")

    assert detector.model is recovered_model
    mock_local_load.assert_called_once_with("newest.pt")
    mock_hub_load.assert_not_called()


def test_yolov5_detector_reports_missing_local_snapshot():
    error_message = "TowerScout local YOLOv5 source snapshot is missing."

    with patch("ts_yolov5.os.path.exists", return_value=True), \
         patch("ts_yolov5._load_local_yolov5_model", side_effect=RuntimeError(error_message)), \
         patch("ts_yolov5.torch.cuda.is_available", return_value=False), \
         patch("ts_yolov5.torch.get_num_threads", return_value=4):
        with pytest.raises(ModelLoadError) as exc_info:
            YOLOv5_Detector("newest.pt")

    assert error_message in str(exc_info.value)


def test_yolov5_detector_reports_dependency_mismatch_before_local_load():
    with patch("ts_yolov5.os.path.exists", return_value=True), \
         patch(
             "ts_yolov5._validate_runtime_dependencies",
             side_effect=RuntimeError(
                 "TowerScout runtime dependency check failed before YOLO initialization."
             ),
         ), \
         patch("ts_yolov5._load_local_yolov5_model") as mock_local_load, \
         patch("ts_yolov5.torch.cuda.is_available", return_value=False), \
         patch("ts_yolov5.torch.get_num_threads", return_value=4):
        with pytest.raises(ModelLoadError) as exc_info:
            YOLOv5_Detector("newest.pt")

    assert "runtime dependency check failed before YOLO initialization" in str(exc_info.value)
    mock_local_load.assert_not_called()


def test_validate_runtime_dependencies_reports_missing_required_local_loader_imports():
    def fake_version(dist_name):
        if dist_name == "seaborn":
            raise metadata.PackageNotFoundError

        versions = {
            "numpy": "1.26.4",
            "pillow": "10.3.0",
            "requests": "2.32.2",
            "packaging": "25.0",
            "pandas": "2.3.3",
            "opencv-python": "4.9.0.80",
            "tqdm": "4.67.1",
            "ultralytics": "8.3.249",
        }
        return versions[dist_name]

    with patch("ts_yolov5.metadata.version", side_effect=fake_version):
        with pytest.raises(RuntimeError) as exc_info:
            _validate_runtime_dependencies()

    message = str(exc_info.value)
    assert "seaborn is not installed" in message
    assert "local YOLOv5 runtime" in message
    assert "pip install -r webapp/requirements.txt" in message


def test_disable_yolo_autoinstall_sets_both_env_guards():
    with patch.dict(
        os.environ,
        {
            YOLO_AUTOINSTALL_ENV_VAR: "true",
            YOLOV5_AUTOINSTALL_ENV_VAR: "true",
        },
        clear=False,
    ):
        with disable_yolo_autoinstall():
            assert os.environ[YOLO_AUTOINSTALL_ENV_VAR] == "false"
            assert os.environ[YOLOV5_AUTOINSTALL_ENV_VAR] == "false"

        assert os.environ[YOLO_AUTOINSTALL_ENV_VAR] == "true"
        assert os.environ[YOLOV5_AUTOINSTALL_ENV_VAR] == "true"


def test_local_loader_wraps_attempt_load_fallback_in_autoshape_without_sys_path_mutation(monkeypatch):
    fake_device = object()
    raw_model = Mock()
    select_device = Mock(return_value=fake_device)
    attempt_load = Mock(return_value=raw_model)

    class FakeLogger:
        def __init__(self):
            self.level = 20
            self.messages = []

        def setLevel(self, level):
            self.level = level

        def warning(self, message, *args):
            if args:
                message = message % args
            self.messages.append(message)

    class FakeAutoShape:
        def __init__(self, model, verbose=True):
            self.model = model
            self.verbose = verbose
            self.device = None

        def to(self, device):
            self.device = device
            return self

    class FakeDetectMultiBackend:
        def __init__(self, *args, **kwargs):
            raise ModuleNotFoundError("export")

    class FakeClassificationModel:
        pass

    class FakeSegmentationModel:
        pass

    def package_module(name):
        module = types.ModuleType(name)
        module.__path__ = []
        return module

    fake_logger = FakeLogger()
    vendor_package = package_module("vendor")
    yolov5_package = package_module("vendor.yolov5_local")
    models_package = package_module("vendor.yolov5_local.models")
    utils_package = package_module("vendor.yolov5_local.utils")
    common_module = types.ModuleType("vendor.yolov5_local.models.common")
    common_module.AutoShape = FakeAutoShape
    common_module.DetectMultiBackend = FakeDetectMultiBackend
    experimental_module = types.ModuleType("vendor.yolov5_local.models.experimental")
    experimental_module.attempt_load = attempt_load
    yolo_module = types.ModuleType("vendor.yolov5_local.models.yolo")
    yolo_module.ClassificationModel = FakeClassificationModel
    yolo_module.SegmentationModel = FakeSegmentationModel
    general_module = types.ModuleType("vendor.yolov5_local.utils.general")
    general_module.LOGGER = fake_logger
    torch_utils_module = types.ModuleType("vendor.yolov5_local.utils.torch_utils")
    torch_utils_module.select_device = select_device

    vendor_package.yolov5_local = yolov5_package
    yolov5_package.models = models_package
    yolov5_package.utils = utils_package
    models_package.common = common_module
    models_package.experimental = experimental_module
    models_package.yolo = yolo_module
    utils_package.general = general_module
    utils_package.torch_utils = torch_utils_module

    monkeypatch.setattr("ts_yolov5_local.disable_yolo_autoinstall", lambda: nullcontext())
    monkeypatch.setattr("ts_yolov5_local.ensure_local_yolov5_source_available", lambda: None)

    original_sys_path = list(sys.path)

    with patch.dict(
        sys.modules,
        {
            "vendor": vendor_package,
            "vendor.yolov5_local": yolov5_package,
            "vendor.yolov5_local.models": models_package,
            "vendor.yolov5_local.models.common": common_module,
            "vendor.yolov5_local.models.experimental": experimental_module,
            "vendor.yolov5_local.models.yolo": yolo_module,
            "vendor.yolov5_local.utils": utils_package,
            "vendor.yolov5_local.utils.general": general_module,
            "vendor.yolov5_local.utils.torch_utils": torch_utils_module,
        },
        clear=False,
    ):
        wrapped_model = load_local_yolov5_model("newest.pt", autoshape=True, verbose=False)

    assert YOLOV5_LOCAL_PACKAGE == "vendor.yolov5_local"
    assert sys.path == original_sys_path
    assert isinstance(wrapped_model, FakeAutoShape)
    assert wrapped_model.model is raw_model
    assert wrapped_model.device is fake_device
    select_device.assert_called_once_with(None)
    attempt_load.assert_called_once()
    assert any("DetectMultiBackend load failed" in message for message in fake_logger.messages)
