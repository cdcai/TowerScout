"""Tests for the TASK-103 pilot comparator (scripts/task103_compare.py).

Every test builds synthetic probe run directories in ``tmp_path`` and judges
them against the real declared gates file, so thresholds are never duplicated
here. Pure stdlib + pytest; the comparator itself must stay torch-free.
"""

import ast
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
COMPARE_PATH = REPO_ROOT / "scripts" / "task103_compare.py"
GATES_V1_PATH = REPO_ROOT / "scripts" / "task103_gates.v1.json"
# v2 amends only the fixture (RGB-derived tiles + palette originals); it is the
# operative gates file, so it is the default for these tests.
GATES_PATH = REPO_ROOT / "scripts" / "task103_gates.v2.json"
GATES = json.loads(GATES_PATH.read_text(encoding="utf-8"))
HISTORICAL = GATES["fixture"]["historical_count_vector"]
PHASES = GATES["required_phases"]
GIB = 1024**3

ARCH_LISTS = {
    "cuda128": ["sm_75", "sm_80", "sm_86", "sm_90", "sm_100", "sm_120"],
    "cuda126": ["sm_50", "sm_60", "sm_70", "sm_75", "sm_80", "sm_86", "sm_90"],
    "cpu": [],
}
WHEEL_TAGS = {"cuda128": "cu128", "cuda126": "cu126", "cpu": "cpu"}


def _load_compare_module():
    spec = importlib.util.spec_from_file_location("task103_compare_under_test", COMPARE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # dataclasses resolve annotations through sys.modules, so register first.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


compare = _load_compare_module()


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def _detection(tile, k, **overrides):
    """Deterministic, non-overlapping detections laid out along a row."""

    x1 = 0.02 + 0.07 * k
    y1 = 0.10 + 0.02 * tile
    detection = {
        "x1": round(x1, 6),
        "y1": round(y1, 6),
        "x2": round(x1 + 0.05, 6),
        "y2": round(y1 + 0.05, 6),
        "conf": round(0.95 - 0.03 * k, 6),
        "class": 0,
        "class_name": "ct",
        "secondary": round(0.40 + 0.04 * k, 6),
    }
    detection.update(overrides)
    return detection


def _results(counts=HISTORICAL):
    return [[_detection(tile, k) for k in range(count)] for tile, count in enumerate(counts)]


def _phase(name, profile, **body):
    return {
        "schema_version": 1,
        "phase": name,
        "ok": True,
        "error": None,
        "profile": profile,
        **body,
    }


def run_docs(
    run_id,
    *,
    stage="C",
    profile="cuda",
    flavor=None,
    host="H-T1",
    image_id=None,
    measured=3,
    startup=1.0,
    yolo=0.10,
    en=0.05,
    combined=2.0,
    results=None,
):
    """Build every JSON document of one passing probe run directory."""

    if flavor is None:
        flavor = "cpu" if profile == "cpu" else ("cuda128" if stage == "C" else "cuda126")
    tag = WHEEL_TAGS[flavor]
    build = GATES["identity"]["cuda_build_by_wheel_tag"][tag]
    torch_version, torchvision_version = (
        ("2.10.0", "0.25.0") if stage == "C" else ("2.6.0", "0.21.0")
    )
    cuda = profile == "cuda"
    device = "cuda:0" if cuda else "cpu"
    results = _results() if results is None else results
    total = sum(len(tile) for tile in results)

    def combined_run(index, warmup):
        return {
            "index": index,
            "warmup": warmup,
            "seconds": combined * (1.5 if warmup else 1.0),
            "results": copy.deepcopy(results),
            "en": {"calls": len(results), "candidates": total, "batches": 2, "errors": []},
        }

    return {
        "run": {
            "schema_version": 1,
            "run_id": run_id,
            "stage": stage,
            "host": host,
            "engine": "docker",
            "profile": profile,
            "flavor": flavor,
            "expected": {
                "torch": torch_version,
                "torchvision": torchvision_version,
                "cuda_build": build,
                "wheel_tag": tag,
            },
            "image": {
                "ref": f"towerscout-pilot:{stage.lower()}-{flavor}",
                "id": image_id or f"sha256:{stage.lower()}-{flavor}",
                "size_bytes": 8_000_000_000,
                "labels": {},
            },
            "source": {
                "worktree_head": "c796792",
                "probe_sha256": "a" * 64,
                "contract_sha256": "b" * 64,
            },
            "fixture_manifest_sha256": None,
            "phases": {name: {"exit_code": 0, "file": f"{name}.json"} for name in PHASES},
            "started_utc": "2026-09-23T10:00:00Z",
            "finished_utc": "2026-09-23T10:20:00Z",
        },
        "identity": _phase(
            "identity",
            profile,
            versions={
                "python": "3.11.13",
                "torch": f"{torch_version}+{tag}",
                "torchvision": f"{torchvision_version}+{tag}",
                "torch_local_tag": tag,
                "torch_cuda_build": build,
                "cudnn_version": 91002 if build else None,
            },
            cuda={
                "available": cuda,
                "device_name": "NVIDIA T1000" if cuda else None,
                "capability": "sm_75" if cuda else None,
                "arch_list": list(ARCH_LISTS[flavor]),
                "arch_supported": True if cuda else None,
                "kernel_probe_ok": True if cuda else None,
            },
            precision={
                "api": "fp32_precision",
                "conv": "ieee",
                "matmul": "ieee",
                "override_env": None,
            },
            model_sha256={
                # Upper case on purpose: G4 must compare case-insensitively.
                "yolo": GATES["models"]["yolo_sha256"].upper(),
                "efficientnet": GATES["models"]["efficientnet_sha256"].upper(),
            },
            pip_check={"ok": True, "output": "No broken requirements found."},
            checks={
                "versions_match": True,
                "cuda_build_matches": True,
                "wheel_tag_matches": True,
                "pip_check_ok": True,
            },
        ),
        "startup": _phase(
            "startup",
            profile,
            cold_start_seconds=startup * 2,
            warmup_seconds=[startup * 1.2],
            measured_seconds=[startup] * measured,
            median_seconds=startup,
        ),
        "synthetic": _phase(
            "synthetic",
            profile,
            yolo={
                "inference_seconds": [yolo] * measured,
                "inference_median_seconds": yolo,
                "detection_counts": [0] * measured,
            },
            efficientnet={
                "inference_seconds": [en] * measured,
                "inference_median_seconds": en,
                "scores": [GATES["tolerances"]["en_synthetic_expected"]] * measured,
            },
            selected_devices={"yolo": profile, "efficientnet": profile},
            nms_probe={"keep": [0, 2], "ok": True},
            checks={"yolo_counts_zero": True, "en_scores_within_tolerance": True},
        ),
        "combined": _phase(
            "combined",
            profile,
            mode="compare",
            tiles=copy.deepcopy(GATES["fixture"]["tiles"]),
            tile_hashes_verified=True,
            runs=[combined_run(0, True)]
            + [combined_run(index, False) for index in range(1, measured + 1)],
            measured_median_seconds=combined,
            observed_devices={"yolo": [device], "efficientnet": [device]},
            log_findings={"secondary_classifier_failed": 0, "nms_time_limit": 0},
            selected_devices={"yolo": profile, "efficientnet": profile},
            contract=None,
        ),
        "memory": _phase(
            "memory",
            profile,
            job_seconds=[combined] * measured,
            host={"vmhwm_bytes": 3 * GIB, "final_rss_bytes": 2 * GIB},
            cuda=(
                {
                    "min_free_bytes": 2 * GIB,
                    "total_bytes": 4 * GIB,
                    "max_allocated_bytes": GIB,
                    "max_reserved_bytes": GIB + GIB // 4,
                    "samples": 20,
                }
                if cuda
                else None
            ),
            en={"candidates": total, "batches": 2, "errors": []},
        ),
        "inject": _phase(
            "inject",
            profile,
            checks={"injected_failure_detected": True, "followup_clean": True},
            injected={"error_type": "RuntimeError", "surfaced": True},
            followup={"ok": True},
        ),
    }


def set_results(docs, results):
    """Give every combined run (warm-up included) the same per-tile results."""

    for run in docs["combined"]["runs"]:
        run["results"] = copy.deepcopy(results)
        run["en"]["candidates"] = sum(len(tile) for tile in results)
    docs["memory"]["en"]["candidates"] = sum(len(tile) for tile in results)


def write_run(root, docs):
    run_dir = root / docs["run"]["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    for name, doc in docs.items():
        if doc is None:
            continue
        (run_dir / f"{name}.json").write_text(json.dumps(doc), encoding="utf-8")
    return run_dir


def _trivy(*vulnerabilities):
    return {
        "SchemaVersion": 2,
        "ArtifactName": "towerscout-pilot:test",
        "Results": [
            {
                "Target": "python-pkg",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": vuln_id,
                        "PkgName": package,
                        "InstalledVersion": "1.0.0",
                        "Severity": severity,
                    }
                    for vuln_id, package, severity in vulnerabilities
                ],
            },
            {"Target": "os", "Vulnerabilities": None},
        ],
    }


class Scenario:
    """Default: all-pass stage-C CUDA candidate with baseline and CPU counterpart."""

    def __init__(self, root):
        self.root = root
        self.reference = run_docs("ref-a-cpu", stage="A", profile="cpu")
        self.candidate = run_docs("cand-c-cuda", stage="C", profile="cuda")
        self.extra_candidates = []
        self.baseline = run_docs("base-a-cuda", stage="A", profile="cuda")
        self.counterpart = run_docs("cpu-c", stage="C", profile="cpu")
        self.gates_path = GATES_PATH
        self.out = root / "out"

    def all_docs(self):
        runs = [self.reference, self.candidate, self.baseline, self.counterpart]
        return [docs for docs in runs + self.extra_candidates if docs is not None]

    def write_json(self, name, doc):
        path = self.root / name
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    def argv(self, *extra):
        runs = self.root / "runs"
        argv = [
            "--gates",
            str(self.gates_path),
            "--reference-outputs",
            str(write_run(runs, self.reference)),
            "--candidate",
            str(write_run(runs, self.candidate)),
        ]
        for docs in self.extra_candidates:
            argv += ["--candidate", str(write_run(runs, docs))]
        if self.baseline is not None:
            argv += ["--baseline", str(write_run(runs, self.baseline))]
        if self.counterpart is not None:
            argv += ["--cpu-counterpart", str(write_run(runs, self.counterpart))]
        return argv + [str(value) for value in extra] + ["--out", str(self.out)]

    def run(self, *extra):
        code = compare.main(self.argv(*extra))
        verdict = json.loads((self.out / "verdict.json").read_text(encoding="utf-8"))
        return code, verdict


@pytest.fixture
def scenario(tmp_path):
    return Scenario(tmp_path)


def _statuses(verdict):
    return {gate_id: gate["status"] for gate_id, gate in verdict["gates"].items()}


def _failed_checks(verdict, gate_id):
    return verdict["gates"][gate_id]["details"].get("failed_checks", [])


# ---------------------------------------------------------------------------
# Happy path and applicability
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("gates_path", [GATES_PATH, GATES_V1_PATH], ids=["v2", "v1"])
def test_all_gates_pass_for_cuda_stage_c_with_baseline(scenario, gates_path):
    gates = json.loads(gates_path.read_text(encoding="utf-8"))
    scenario.gates_path = gates_path
    for docs in scenario.all_docs():
        docs["combined"]["tiles"] = copy.deepcopy(gates["fixture"]["tiles"])
    shared = [("CVE-2025-0001", "openssl", "HIGH"), ("CVE-2025-0002", "zlib", "MEDIUM")]
    reference_scan = scenario.write_json("trivy-ref.json", _trivy(*shared))
    candidate_scan = scenario.write_json("trivy-cand.json", _trivy(*shared))

    code, verdict = scenario.run(
        "--scan-reference", reference_scan, "--scan-candidate", candidate_scan
    )

    assert code == 0
    assert verdict["overall"] == "pass"
    assert set(_statuses(verdict).values()) == {"pass"}, _statuses(verdict)
    assert verdict["reference_outputs"] == "ref-a-cpu"
    assert verdict["candidates"] == ["cand-c-cuda"]
    assert verdict["baselines"] == ["base-a-cuda"]
    assert verdict["cpu_counterpart"] == "cpu-c"
    assert (verdict["stage"], verdict["profile"]) == ("C", "cuda")
    assert verdict["gates_file_sha256"] == hashlib.sha256(gates_path.read_bytes()).hexdigest()
    assert verdict["gates"]["G2"]["details"]["missing_arch"] == []
    assert verdict["gates"]["G7"]["details"]["tile_set"] == "fixture.tiles"
    assert verdict["findings"] == []
    g7 = verdict["gates"]["G7"]["details"]
    assert g7["count_vectors"]["candidate"] == HISTORICAL
    assert len(g7["tiles"]) == len(HISTORICAL)
    assert g7["max_deltas"]["box"] == 0.0
    assert set(verdict["gates"]["G9"]["details"]["ratios"]) == {
        "startup_seconds",
        "synthetic_yolo_inference_seconds",
        "synthetic_en_inference_seconds",
        "combined_run_seconds",
    }
    markdown = (scenario.out / "verdict.md").read_text(encoding="utf-8")
    assert "| G7 Combined outputs | pass |" in markdown
    assert "| Gate | Status | Key details |" in markdown


def test_cpu_profile_marks_arch_and_precision_not_applicable(scenario):
    scenario.candidate = run_docs("cand-c-cpu", stage="C", profile="cpu")
    scenario.baseline = run_docs("base-a-cpu", stage="A", profile="cpu")
    scenario.counterpart = None

    code, verdict = scenario.run()

    statuses = _statuses(verdict)
    assert statuses["G2"] == "not_applicable"
    assert statuses["G5"] == "not_applicable"
    assert statuses["G10"] == "not_applicable"
    assert verdict["overall"] == "pass"
    assert code == 0


def test_stage_a_skips_precision_and_null_kernel_probe_uses_execution_evidence(scenario):
    scenario.candidate = run_docs("cand-a-cuda", stage="A", profile="cuda")
    identity = scenario.candidate["identity"]
    identity["cuda"]["kernel_probe_ok"] = None
    identity["cuda"]["arch_supported"] = None
    identity["precision"] = {"api": "legacy", "conv": None, "matmul": None, "override_env": None}
    scenario.counterpart = run_docs("cpu-a", stage="A", profile="cpu")

    code, verdict = scenario.run()

    assert verdict["gates"]["G5"]["status"] == "not_applicable"
    g2 = verdict["gates"]["G2"]
    assert g2["status"] == "pass"
    assert g2["details"]["kernel_probe"] == "unknown_fallback_to_execution_evidence"
    assert "missing_arch" not in g2["details"]  # cuda126 is not the target flavor
    assert any(f["id"] == "kernel_probe_unknown" for f in verdict["findings"])
    assert code == 0


def test_null_kernel_probe_without_cuda_execution_fails_arch_gate(scenario):
    scenario.candidate = run_docs("cand-a-cuda", stage="A", profile="cuda")
    scenario.candidate["identity"]["cuda"]["kernel_probe_ok"] = None
    scenario.candidate["combined"]["observed_devices"]["efficientnet"] = ["cpu"]
    scenario.counterpart = None

    code, verdict = scenario.run()

    assert verdict["gates"]["G2"]["status"] == "fail"
    assert "kernel_execution_evidence" in _failed_checks(verdict, "G2")
    assert code == 1


def test_target_flavor_requires_every_declared_arch(scenario):
    scenario.candidate["identity"]["cuda"]["arch_list"].remove("sm_120")

    _, verdict = scenario.run()

    assert verdict["gates"]["G2"]["status"] == "fail"
    assert verdict["gates"]["G2"]["details"]["missing_arch"] == ["sm_120"]


# ---------------------------------------------------------------------------
# G7 combined outputs
# ---------------------------------------------------------------------------


def test_iou_matching_tolerates_reordered_detections(scenario):
    reordered = [list(reversed(tile)) for tile in _results()]
    set_results(scenario.candidate, reordered)

    code, verdict = scenario.run()

    assert verdict["gates"]["G7"]["status"] == "pass"
    assert code == 0


def test_iou_matching_tolerates_nms_tie_reordering(scenario):
    # Two overlapping same-class boxes with near-equal confidences: the other
    # runtime's NMS emits them in the opposite order with conf nudged (within
    # tolerance) across each other. Positional comparison would fail here.
    first = {"x1": 0.10, "y1": 0.10, "x2": 0.30, "y2": 0.30, "conf": 0.80000}
    second = {"x1": 0.12, "y1": 0.10, "x2": 0.32, "y2": 0.30, "conf": 0.79995}
    common = {"class": 0, "class_name": "ct"}
    reference = [[] for _ in HISTORICAL]
    reference[2] = [
        {**first, **common, "secondary": 0.7},
        {**second, **common, "secondary": 0.6},
    ]
    candidate = [[] for _ in HISTORICAL]
    candidate[2] = [
        {**second, **common, "conf": 0.80001, "secondary": 0.6},
        {**first, **common, "conf": 0.79996, "secondary": 0.7},
    ]
    set_results(scenario.reference, reference)
    set_results(scenario.candidate, candidate)

    _, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "pass", g7["summary"]
    assert g7["details"]["tiles"][2]["matched"] == 2
    assert g7["details"]["tiles"][2]["min_iou"] == pytest.approx(1.0)


def test_detection_shift_within_tolerance_passes(scenario):
    results = _results()
    results[2][0]["x1"] += 0.00005
    results[2][0]["x2"] += 0.00005
    results[2][0]["conf"] -= 0.00005
    set_results(scenario.candidate, results)

    _, verdict = scenario.run()

    assert verdict["gates"]["G7"]["status"] == "pass"
    assert verdict["gates"]["G7"]["details"]["tiles"][2]["max_box_delta"] == pytest.approx(
        0.00005
    )


def test_detection_shift_beyond_box_tolerance_fails(scenario):
    results = _results()
    results[2][0]["x1"] += 0.001
    results[2][0]["x2"] += 0.001
    set_results(scenario.candidate, results)

    code, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "fail"
    assert "detections_match_reference" in g7["details"]["failed_checks"]
    assert "count_vector_matches_reference" not in g7["details"]["failed_checks"]
    tile = g7["details"]["tiles"][2]
    assert tile["max_box_delta"] == pytest.approx(0.001)
    assert len(tile["violations"]) == 1
    assert tile["violations"][0]["box_delta"] == pytest.approx(0.001)
    assert g7["details"]["tolerance_violations"] == 1
    assert verdict["overall"] == "fail"
    assert code == 1


def test_missing_detection_fails_combined_gate(scenario):
    results = _results()
    dropped = results[2].pop()
    set_results(scenario.candidate, results)

    _, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "fail"
    assert "detections_match_reference" in g7["details"]["failed_checks"]
    unmatched = g7["details"]["tiles"][2]["unmatched_reference"]
    assert [entry["detection"]["x1"] for entry in unmatched] == [dropped["x1"]]
    assert g7["details"]["unmatched"] == {"reference": 1, "candidate": 0}


def test_count_vector_mismatch_fails(scenario):
    results = _results()
    results[0].append(_detection(0, 0))
    set_results(scenario.candidate, results)

    _, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "fail"
    assert "count_vector_matches_reference" in g7["details"]["failed_checks"]
    assert g7["details"]["count_vectors"]["candidate"][0] == 1
    assert g7["details"]["unmatched"] == {"reference": 0, "candidate": 1}


def test_en_error_in_any_run_fails_combined_gate(scenario):
    warmup = scenario.candidate["combined"]["runs"][0]
    assert warmup["warmup"] is True
    warmup["en"]["errors"] = ["RuntimeError: secondary classifier exploded"]

    _, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "fail"
    assert "en_errors_absent" in g7["details"]["failed_checks"]
    assert g7["details"]["en_errors"][0]["run_index"] == 0


def test_repeat_determinism_violation_fails(scenario):
    runs = scenario.candidate["combined"]["runs"]
    runs[2]["results"][2][0]["conf"] += 0.001  # a middle measured run drifts

    _, verdict = scenario.run()

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "fail"
    assert g7["details"]["failed_checks"] == ["repeat_determinism"]
    failing = [entry for entry in g7["details"]["determinism"] if not entry["passed"]]
    assert [entry["run_index"] for entry in failing] == [2]


def test_log_findings_fail_combined_gate(scenario):
    scenario.candidate["combined"]["log_findings"]["nms_time_limit"] = 1

    _, verdict = scenario.run()

    assert "log_findings_clean" in _failed_checks(verdict, "G7")


def test_historical_vector_finding_is_informational(scenario):
    counts = list(HISTORICAL)
    counts[0] = 1
    set_results(scenario.reference, _results(counts))
    set_results(scenario.candidate, _results(counts))

    code, verdict = scenario.run("--check-historical-vector")

    finding = next(f for f in verdict["findings"] if f["id"] == "historical_count_vector")
    assert finding["severity"] == "info"
    assert finding["matches"] is False
    assert finding["differing_tiles"] == ["tile_000.png"]
    assert verdict["gates"]["G7"]["status"] == "pass"
    assert verdict["overall"] == "pass"
    assert code == 0


def test_historical_vector_finding_reports_match(scenario):
    _, verdict = scenario.run("--check-historical-vector")

    finding = next(f for f in verdict["findings"] if f["id"] == "historical_count_vector")
    assert finding["matches"] is True
    assert finding["observed"] == HISTORICAL


def _make_yolo_only(docs):
    """Shape a run like the probe's --no-secondary palette continuity run."""

    combined = docs["combined"]
    combined["secondary_enabled"] = False
    combined["tiles"] = copy.deepcopy(GATES["fixture"]["palette_originals"])
    combined["observed_devices"]["efficientnet"] = []
    for run in combined["runs"]:
        run["en"] = {"calls": 0, "candidates": 0, "batches": 0, "errors": []}
        for tile in run["results"]:
            for detection in tile:
                detection["secondary"] = 1.0


def test_yolo_only_palette_run_skips_en_requirements(scenario):
    _make_yolo_only(scenario.reference)
    _make_yolo_only(scenario.candidate)

    code, verdict = scenario.run("--check-historical-vector")

    g7 = verdict["gates"]["G7"]
    assert g7["status"] == "pass", g7["summary"]
    assert g7["details"]["tile_set"] == "fixture.palette_originals"
    assert g7["details"]["en_requirements"].startswith("not_applicable")
    assert "en_candidates_positive" not in g7["details"]["checks"]
    assert verdict["gates"]["G3"]["status"] == "pass"
    finding_ids = {finding["id"] for finding in verdict["findings"]}
    assert {"secondary_disabled", "historical_count_vector"} <= finding_ids
    historical = next(f for f in verdict["findings"] if f["id"] == "historical_count_vector")
    assert historical["matches"] is True
    assert code == 0


def test_secondary_mode_mismatch_with_reference_fails(scenario):
    _make_yolo_only(scenario.candidate)

    _, verdict = scenario.run()

    assert "secondary_enabled_matches_reference" in _failed_checks(verdict, "G7")


def test_empty_efficientnet_devices_fail_when_secondary_enabled(scenario):
    scenario.candidate["combined"]["observed_devices"]["efficientnet"] = []

    _, verdict = scenario.run()

    assert _failed_checks(verdict, "G3") == ["observed_efficientnet_on_cuda"]


def test_match_tile_prefers_highest_iou_same_class():
    reference = [{"x1": 0.1, "y1": 0.1, "x2": 0.3, "y2": 0.3, "conf": 0.9,
                  "class": 0, "class_name": "ct", "secondary": 0.5}]
    other_class = {**reference[0], "class": 1, "class_name": "other"}
    near = {**reference[0], "x1": 0.10002}
    far = {**reference[0], "x1": 0.12}
    result = compare.match_tile(
        reference, [other_class, far, near], iou_match=0.9, box=1e-4, conf=1e-4, secondary=1e-4
    )
    assert result["matched"] == 1
    assert [entry["index"] for entry in result["unmatched_candidate"]] == [0, 1]
    assert result["max_box_delta"] == pytest.approx(0.00002)


# ---------------------------------------------------------------------------
# Other gates
# ---------------------------------------------------------------------------


def test_observed_cpu_device_in_cuda_run_fails_devices_gate(scenario):
    scenario.candidate["combined"]["observed_devices"]["yolo"] = ["cuda:0", "cpu"]

    _, verdict = scenario.run()

    assert verdict["gates"]["G3"]["status"] == "fail"
    assert _failed_checks(verdict, "G3") == ["observed_yolo_on_cuda"]


def test_model_hash_mismatch_fails_trust_gate(scenario):
    scenario.candidate["identity"]["model_sha256"]["efficientnet"] = "0" * 64

    _, verdict = scenario.run()

    assert verdict["gates"]["G4"]["status"] == "fail"
    assert _failed_checks(verdict, "G4") == ["efficientnet_sha256_matches"]


def test_precision_override_fails_precision_gate(scenario):
    scenario.candidate["identity"]["precision"]["override_env"] = "tf32"

    _, verdict = scenario.run()

    assert _failed_checks(verdict, "G5") == ["override_env_unset"]


def test_identity_cross_check_catches_wrong_cuda_build(scenario):
    scenario.candidate["identity"]["versions"]["torch_cuda_build"] = "12.6"

    _, verdict = scenario.run()

    assert verdict["gates"]["G1"]["status"] == "fail"
    assert _failed_checks(verdict, "G1") == ["torch_cuda_build_matches_gates"]


def test_cross_profile_en_delta_beyond_limit_fails_synthetic_gate(scenario):
    expected = GATES["tolerances"]["en_synthetic_expected"]
    # Within the absolute EN tolerance, but beyond the CPU/CUDA delta limit.
    scenario.counterpart["synthetic"]["efficientnet"]["scores"] = [expected + 0.00002] * 3

    _, verdict = scenario.run()

    g6 = verdict["gates"]["G6"]
    assert g6["status"] == "fail"
    assert g6["details"]["failed_checks"] == ["cross_profile_en_delta_within_limit"]
    assert g6["details"]["cross_profile"]["delta"] == pytest.approx(0.00002)


def test_injected_failure_not_detected_fails_failure_gate(scenario):
    scenario.candidate["inject"]["checks"]["injected_failure_detected"] = False

    _, verdict = scenario.run()

    assert _failed_checks(verdict, "G11") == ["injected_failure_detected"]


# ---------------------------------------------------------------------------
# Completeness and missing inputs
# ---------------------------------------------------------------------------


def test_missing_phase_file_fails_completeness_and_marks_dependent_gate_missing(scenario):
    scenario.candidate["memory"] = None

    code, verdict = scenario.run()

    assert verdict["gates"]["G12"]["status"] == "fail"
    assert verdict["gates"]["G12"]["details"]["missing"] == ["cand-c-cuda:memory"]
    assert verdict["gates"]["G8"]["status"] == "missing"
    assert verdict["gates"]["G8"]["details"]["missing"]["item"] == "memory.json"
    assert verdict["gates"]["G7"]["status"] == "pass"
    assert verdict["overall"] == "fail"
    assert code == 1


def test_nonzero_phase_exit_code_fails_completeness(scenario):
    scenario.candidate["run"]["phases"]["inject"]["exit_code"] = 3

    _, verdict = scenario.run()

    problems = verdict["gates"]["G12"]["details"]["runs"][0]["problems"]
    assert problems == [{"item": "inject", "reason": "exit_code 3"}]


def test_missing_run_json_marks_run_level_gates_missing(scenario):
    argv = scenario.argv()
    (scenario.root / "runs" / "cand-c-cuda" / "run.json").unlink()

    code = compare.main(argv)

    verdict = json.loads((scenario.out / "verdict.json").read_text(encoding="utf-8"))
    assert verdict["gates"]["G12"]["status"] == "fail"
    assert verdict["gates"]["G12"]["details"]["runs"][0]["problems"][0]["item"] == "run.json"
    assert verdict["gates"]["G1"]["status"] == "missing"
    assert verdict["gates"]["G1"]["details"]["missing"]["item"] == "run.json"
    assert code == 1


# ---------------------------------------------------------------------------
# G8 memory and G9 performance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("min_free", "expected_status"),
    [(2 * GIB, "pass"), (GIB // 2, "fail")],
)
def test_without_baseline_relative_checks_skip_but_headroom_is_enforced(
    scenario, min_free, expected_status
):
    scenario.baseline = None
    scenario.candidate["memory"]["cuda"]["min_free_bytes"] = min_free

    _, verdict = scenario.run()

    g8 = verdict["gates"]["G8"]
    assert g8["status"] == expected_status
    assert g8["details"]["relative"]["status"] == "not_applicable"
    assert verdict["gates"]["G9"]["status"] == "not_applicable"
    if expected_status == "fail":
        assert g8["details"]["failed_checks"] == ["device_headroom"]


def test_failed_device_sampler_fails_headroom_without_malformed_input(scenario):
    scenario.candidate["memory"]["cuda"].update(
        min_free_bytes=None, samples=0, sampler_error="RuntimeError: sampler died"
    )

    _, verdict = scenario.run()

    g8 = verdict["gates"]["G8"]
    assert g8["status"] == "fail"
    assert g8["details"]["failed_checks"] == ["device_headroom"]
    assert g8["details"]["absolute"]["runs"][0]["sampler_error"] == "RuntimeError: sampler died"


def test_host_memory_growth_beyond_relative_max_fails(scenario):
    scenario.candidate["memory"]["host"]["vmhwm_bytes"] = int(3 * GIB * 1.25)

    _, verdict = scenario.run()

    g8 = verdict["gates"]["G8"]
    assert g8["details"]["failed_checks"] == ["vmhwm_bytes_within_relative_max"]
    assert g8["details"]["relative"]["metrics"]["vmhwm_bytes"]["ratio"] == pytest.approx(1.25)


def test_performance_regression_beyond_relative_max_fails(scenario):
    scenario.candidate = run_docs("cand-c-cuda", combined=2.4)

    code, verdict = scenario.run()

    g9 = verdict["gates"]["G9"]
    assert g9["status"] == "fail"
    assert g9["details"]["reason"] == "regression"
    assert g9["details"]["ratios"]["combined_run_seconds"] == pytest.approx(1.2)
    assert g9["details"]["metrics"]["combined_run_seconds"]["status"] == "regression"
    assert code == 1


def test_borderline_performance_requires_rerun_then_passes_when_pooled(scenario):
    scenario.candidate = run_docs("cand-c-cuda", startup=1.08)

    code, verdict = scenario.run()

    g9 = verdict["gates"]["G9"]
    assert g9["status"] == "fail"
    assert g9["details"]["reason"] == "borderline_rerun_required"
    assert g9["details"]["metrics"]["startup_seconds"]["status"] == "borderline_rerun_required"
    assert g9["details"]["ratios"]["startup_seconds"] == pytest.approx(1.08)
    assert code == 1

    # Pool a rerun of the same image so the candidate has 3 + 5 measured values.
    scenario.extra_candidates = [run_docs("cand-c-cuda-rerun", startup=1.08, measured=5)]
    code, verdict = scenario.run()

    g9 = verdict["gates"]["G9"]
    assert g9["status"] == "pass", g9["summary"]
    assert g9["details"]["metrics"]["startup_seconds"]["candidate_count"] == 8
    assert verdict["candidates"] == ["cand-c-cuda", "cand-c-cuda-rerun"]
    assert code == 0


def test_borderline_above_limit_still_fails_after_pooling(scenario):
    scenario.candidate = run_docs("cand-c-cuda", startup=1.12)
    scenario.extra_candidates = [run_docs("cand-c-cuda-rerun", startup=1.12, measured=5)]

    _, verdict = scenario.run()

    g9 = verdict["gates"]["G9"]
    assert g9["status"] == "fail"
    assert g9["details"]["reason"] == "regression"


def test_pooled_candidate_from_another_image_is_rejected(scenario):
    scenario.extra_candidates = [
        run_docs("cand-other-image", image_id="sha256:different", measured=5)
    ]

    _, verdict = scenario.run()

    g9 = verdict["gates"]["G9"]
    assert g9["status"] == "fail"
    assert "candidate_pool_consistent" in g9["details"]["failed_checks"]
    assert g9["details"]["reason"] == "invalid_pool"


# ---------------------------------------------------------------------------
# G10 security
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("dispositions", "expected_status"),
    [(None, "fail"), ({"CVE-2026-9999": "Not reachable; upstream fix pending."}, "pass")],
)
def test_new_high_vulnerability_requires_disposition(scenario, dispositions, expected_status):
    reference_scan = scenario.write_json(
        "trivy-ref.json", _trivy(("CVE-2025-0001", "openssl", "HIGH"))
    )
    candidate_scan = scenario.write_json(
        "trivy-cand.json",
        _trivy(
            ("CVE-2025-0001", "openssl", "HIGH"),
            ("CVE-2026-9999", "libcudnn9", "HIGH"),
            ("CVE-2026-1111", "bash", "LOW"),
        ),
    )
    extra = ["--scan-reference", reference_scan, "--scan-candidate", candidate_scan]
    if dispositions is not None:
        extra += ["--scan-dispositions", scenario.write_json("dispositions.json", dispositions)]

    _, verdict = scenario.run(*extra)

    g10 = verdict["gates"]["G10"]
    assert g10["status"] == expected_status
    new = g10["details"]["new_findings"]
    assert [(f["vulnerability_id"], f["pkg_name"]) for f in new] == [
        ("CVE-2026-9999", "libcudnn9")
    ]
    assert g10["details"]["undisposed"] == ([] if dispositions else ["CVE-2026-9999"])


def test_bom_prefixed_run_json_and_non_ascii_scans_are_read(scenario):
    # Windows PowerShell 5.1 Set-Content -Encoding UTF8 writes a BOM, and Trivy
    # output contains non-ASCII text that the cp1252 default cannot decode.
    scan = _trivy(("CVE-2025-0001", "openssl", "HIGH"))
    # U+00DC, U+201E, U+201C, U+2013, U+2713 (kept out of the source as literals).
    title = "{}berlauf in {}ssl{} {} {}".format(*map(chr, (0xDC, 0x201E, 0x201C, 0x2013, 0x2713)))
    scan["Results"][0]["Vulnerabilities"][0]["Title"] = title
    scan_paths = []
    for name in ("trivy-ref.json", "trivy-cand.json"):
        path = scenario.root / name
        path.write_text(json.dumps(scan, ensure_ascii=False), encoding="utf-8-sig")
        scan_paths.append(path)
    argv = scenario.argv("--scan-reference", scan_paths[0], "--scan-candidate", scan_paths[1])
    run_json = scenario.root / "runs" / "cand-c-cuda" / "run.json"
    run_json.write_text(json.dumps(scenario.candidate["run"]), encoding="utf-8-sig")
    assert run_json.read_bytes().startswith(b"\xef\xbb\xbf")

    assert compare.main(argv) == 0
    verdict = json.loads((scenario.out / "verdict.json").read_text(encoding="utf-8"))
    assert verdict["gates"]["G10"]["status"] == "pass"
    assert verdict["gates"]["G12"]["status"] == "pass"


# ---------------------------------------------------------------------------
# CLI contract
# ---------------------------------------------------------------------------


def _cli(argv):
    return subprocess.run(
        [sys.executable, str(COMPARE_PATH), *argv],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_cli_exit_codes(scenario, tmp_path):
    assert _cli(scenario.argv()).returncode == 0

    scenario.candidate["inject"]["checks"]["followup_clean"] = False
    assert _cli(scenario.argv()).returncode == 1

    bad_gates = scenario.argv()
    bad_gates[bad_gates.index("--gates") + 1] = str(tmp_path / "missing-gates.json")
    result = _cli(bad_gates)
    assert result.returncode == 2
    assert "cannot read gates file" in result.stderr

    not_a_dir = scenario.argv()
    not_a_dir[not_a_dir.index("--candidate") + 1] = str(tmp_path / "no-such-run")
    assert _cli(not_a_dir).returncode == 2

    without_out = scenario.argv()[:-2]
    assert _cli(without_out).returncode == 2


def test_main_returns_usage_error_for_invalid_gates(scenario, tmp_path):
    invalid = tmp_path / "gates.json"
    invalid.write_text(json.dumps({**GATES, "tolerances": {"iou_match": 0.9}}), encoding="utf-8")
    argv = scenario.argv()
    argv[argv.index("--gates") + 1] = str(invalid)

    assert compare.main(argv) == 2
    with pytest.raises(SystemExit) as raised:
        compare.main(argv + ["--scan-reference", str(invalid)])
    assert raised.value.code == 2


def test_comparator_imports_stdlib_only():
    tree = ast.parse(COMPARE_PATH.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported, "expected at least one import"
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)
    assert not imported & {"torch", "torchvision", "numpy", "towerscout"}
