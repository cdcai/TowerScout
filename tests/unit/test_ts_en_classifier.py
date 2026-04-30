"""Focused EfficientNet secondary-classifier regression tests."""

from unittest.mock import Mock

import torch

import ts_en


class _FakeInput:
    def unsqueeze(self, dim):
        self.unsqueeze_dim = dim
        return self

    def cuda(self):
        self.moved_to_cuda = True
        return self


def test_classify_applies_confidence_branches_and_inference_mode(monkeypatch):
    classifier = object.__new__(ts_en.EN_Classifier)
    classifier.save_debug_images = False

    fake_input = _FakeInput()
    classifier.transform = Mock(return_value=fake_input)
    monkeypatch.setattr(ts_en, "cut_square_detection", Mock(return_value="cropped-image"))
    monkeypatch.setattr(ts_en.torch.cuda, "is_available", lambda: False)

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
        assert input_tensor is fake_input
        return torch.tensor([[0.0]])

    classifier.model = Mock(side_effect=fake_model)
    monkeypatch.setattr(ts_en.torch, "inference_mode", fake_inference_mode)

    detections = [
        [0, 0, 10, 10, 0.10],
        [1, 1, 11, 11, 0.50],
        [2, 2, 12, 12, 0.90],
    ]

    classifier.classify("source-image", detections, min_conf=0.25, max_conf=0.65)

    assert detections[0][-1] == 0
    assert detections[1][-1] == 0.5
    assert detections[2][-1] == 1
    assert inference_state["entered"] == 1
    classifier.transform.assert_called_once_with("cropped-image")
    classifier.model.assert_called_once_with(fake_input)
    ts_en.cut_square_detection.assert_called_once_with("source-image", 1, 1, 11, 11)
    assert fake_input.unsqueeze_dim == 0
