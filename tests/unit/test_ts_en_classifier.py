"""Focused EfficientNet secondary-classifier regression tests."""

import shutil
import uuid
from pathlib import Path
from unittest.mock import Mock

import torch
from PIL import Image

import ts_device
import ts_en


class _FakeCudaProbe:
    def cpu(self):
        return self


def test_classify_applies_confidence_branches_and_inference_mode(monkeypatch):
    classifier = object.__new__(ts_en.EN_Classifier)
    classifier.save_debug_images = False
    classifier.batch_size = 8
    classifier.device = torch.device("cpu")
    classifier.device_label = "cpu"

    fake_input = torch.ones(3, 2, 2)
    classifier.transform = Mock(return_value=fake_input)
    cropped_image = Mock()
    cropped_image.convert.return_value = "cropped-rgb-image"
    monkeypatch.setattr(ts_en, "cut_square_detection", Mock(return_value=cropped_image))
    monkeypatch.setattr(
        ts_en.torch.cuda,
        "is_available",
        Mock(side_effect=AssertionError("classify should use cached device state")),
    )

    inference_state = {"active": False, "entered": 0}

    class FakeInferenceMode:
        def __enter__(self):
            inference_state["active"] = True
            inference_state["entered"] += 1

        def __exit__(self, exc_type, exc_value, traceback):
            inference_state["active"] = False

    def fake_inference_mode():
        return FakeInferenceMode()

    def fake_model(input_tensor):
        assert inference_state["active"] is True
        assert input_tensor.shape == (1, 3, 2, 2)
        return torch.tensor([[0.0]])

    classifier.model = Mock(side_effect=fake_model)
    monkeypatch.setattr(ts_en.torch, "inference_mode", fake_inference_mode)

    detections = [
        [0, 0, 10, 10, 0.10],
        [1, 1, 11, 11, 0.50],
        [2, 2, 12, 12, 0.90],
    ]

    stats = classifier.classify("source-image", detections, min_conf=0.25, max_conf=0.65)

    assert detections[0][-1] == 0
    assert detections[1][-1] == 0.5
    assert detections[2][-1] == 1
    assert inference_state["entered"] == 1
    assert stats["detections_total"] == 3
    assert stats["candidate_count"] == 1
    assert stats["batches"] == 1
    assert stats["device"] == "cpu"
    cropped_image.convert.assert_called_once_with("RGB")
    classifier.transform.assert_called_once_with("cropped-rgb-image")
    classifier.model.assert_called_once()
    ts_en.cut_square_detection.assert_called_once_with("source-image", 1, 1, 11, 11)


def test_classify_batches_multiple_review_band_candidates(monkeypatch):
    classifier = object.__new__(ts_en.EN_Classifier)
    classifier.save_debug_images = False
    classifier.batch_size = 2
    classifier.device = torch.device("cpu")
    classifier.device_label = "cpu"

    classifier.transform = Mock(return_value=torch.ones(3, 2, 2))
    cropped_image = Mock()
    cropped_image.convert.return_value = "cropped-rgb-image"
    monkeypatch.setattr(ts_en, "cut_square_detection", Mock(return_value=cropped_image))

    batch_shapes = []
    stack_sizes = []
    real_stack = ts_en.torch.stack

    def fake_stack(tensors):
        stack_sizes.append(len(tensors))
        return real_stack(tensors)

    def fake_model(input_tensor):
        batch_shapes.append(tuple(input_tensor.shape))
        return torch.zeros((input_tensor.shape[0], 1))

    classifier.model = Mock(side_effect=fake_model)
    monkeypatch.setattr(ts_en.torch, "stack", fake_stack)

    detections = [
        [0, 0, 10, 10, 0.30],
        [1, 1, 11, 11, 0.40],
        [2, 2, 12, 12, 0.50],
    ]

    stats = classifier.classify("source-image", detections, min_conf=0.25, max_conf=0.65)

    assert [det[-1] for det in detections] == [0.5, 0.5, 0.5]
    assert batch_shapes == [(2, 3, 2, 2), (1, 3, 2, 2)]
    assert stack_sizes == [2, 1]
    assert stats["candidate_count"] == 3
    assert stats["batches"] == 2
    assert stats["batch_size"] == 2
    assert classifier.last_classify_stats is stats


def test_classify_converts_palette_png_crop_to_rgb_before_transform():
    classifier = object.__new__(ts_en.EN_Classifier)
    classifier.save_debug_images = False
    classifier.batch_size = 8
    classifier.device = torch.device("cpu")
    classifier.device_label = "cpu"
    observed_modes = []

    def transform(image):
        observed_modes.append(image.mode)
        return torch.ones(3, 2, 2)

    classifier.transform = transform
    classifier.model = Mock(return_value=torch.zeros((1, 1)))
    palette_image = Image.new("P", (16, 16))
    palette_image.putpalette([value for index in range(256) for value in (index, 0, 0)])
    detections = [[0.0, 0.0, 1.0, 1.0, 0.5]]

    classifier.classify(palette_image, detections)

    assert observed_modes == ["RGB"]
    assert detections[0][-1] == 0.5


def test_efficientnet_init_falls_back_to_cpu_when_cuda_setup_fails(monkeypatch):
    scratch_dir = Path(".agent_work/pytest-temp") / f"ts-en-{uuid.uuid4().hex}"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    model_path = scratch_dir / "b5_unweighted_best.pt"
    model_path.write_text("fake checkpoint", encoding="utf-8")

    class FakeModel:
        def __init__(self):
            self.devices = []
            self.loaded_checkpoint = None
            self.evaluated = False

        def to(self, device):
            self.devices.append(str(device))
            if str(device) == "cuda":
                raise RuntimeError("cuda unavailable")
            return self

        def load_state_dict(self, checkpoint):
            self.loaded_checkpoint = checkpoint

        def eval(self):
            self.evaluated = True

    fake_model = FakeModel()
    torch_load = Mock(return_value={"weights": "ok"})

    try:
        monkeypatch.setattr(ts_en, "get_en_model_dir", lambda: scratch_dir)
        from_name = Mock(return_value=fake_model)
        from_pretrained = Mock(side_effect=AssertionError("from_pretrained should not run during RC package load"))
        monkeypatch.setattr(ts_en.EfficientNet, "from_name", from_name)
        monkeypatch.setattr(ts_en.EfficientNet, "from_pretrained", from_pretrained)
        monkeypatch.setattr(ts_en, "verify_trusted_model", Mock())
        monkeypatch.setattr(ts_en.torch.cuda, "is_available", Mock(return_value=True))
        monkeypatch.setattr(ts_en.torch.cuda, "get_device_name", Mock(return_value="NVIDIA Test GPU"))
        monkeypatch.setattr(ts_en.torch, "zeros", Mock(return_value=_FakeCudaProbe()))
        # The decisive conv/GEMM kernel probe cannot run on CPU-only torch; simulate it passing.
        monkeypatch.setattr(ts_device, "_cuda_kernel_probe", lambda: None)
        monkeypatch.setattr(ts_en.torch, "load", torch_load)

        classifier = ts_en.EN_Classifier()

        assert classifier.device_label == "cpu"
        assert fake_model.devices == ["cuda", "cpu"]
        assert fake_model.loaded_checkpoint == {"weights": "ok"}
        assert fake_model.evaluated is True
        assert classifier.batch_size == 8
        from_name.assert_called_once_with("efficientnet-b5", num_classes=1000)
        from_pretrained.assert_not_called()
        torch_load.assert_called_once()
        assert torch_load.call_args.kwargs["map_location"] == torch.device("cpu")
        assert torch_load.call_args.kwargs["weights_only"] is True
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)
