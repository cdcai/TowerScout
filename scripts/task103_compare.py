"""Fail-closed TASK-103 pilot comparator for probe run directories.

Reads run directories written by the TASK-103 probe harness together with a
declared gates file (``task103_gates.v1.json`` or its fixture amendment
``task103_gates.v2.json``) and writes ``verdict.json`` and ``verdict.md``.
Every threshold is read from the gates file; nothing is hardcoded here. The
comparator is stdlib-only on purpose: it must never import torch or any webapp
module so it can judge evidence on any host.

Gate statuses are ``pass``, ``fail``, ``not_applicable`` and ``missing``
(a needed input file is absent or unparseable). ``missing`` counts as a
failure; the overall verdict passes only when every gate is ``pass`` or
``not_applicable``.

Exit codes: 0 overall pass, 1 overall fail, 2 usage or IO error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Callable, Iterable, Sequence


PASS = "pass"
FAIL = "fail"
NOT_APPLICABLE = "not_applicable"
MISSING = "missing"
_ACCEPTED_STATUSES = frozenset({PASS, NOT_APPLICABLE})

GATE_TITLES: dict[str, str] = {
    "G1": "Identity",
    "G2": "Arch coverage",
    "G3": "Observed devices",
    "G4": "Model trust",
    "G5": "Precision",
    "G6": "Synthetic",
    "G7": "Combined outputs",
    "G8": "Memory",
    "G9": "Performance",
    "G10": "Security",
    "G11": "Failure behavior",
    "G12": "Completeness",
}

_SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
_BOX_FIELDS = ("x1", "y1", "x2", "y2")
_FLOAT_FIELDS = (*_BOX_FIELDS, "conf", "secondary")
_IDENTITY_CHECKS = (
    "versions_match",
    "cuda_build_matches",
    "wheel_tag_matches",
    "pip_check_ok",
)
_INJECT_CHECKS = ("injected_failure_detected", "followup_clean")
_LOG_FINDING_KEYS = ("secondary_classifier_failed", "nms_time_limit")
_MODELS = ("yolo", "efficientnet")
_PROFILES = ("cpu", "cuda")
_PRECISION_OVERRIDE_OFF = (None, "", "0")
_BLOCKING_SEVERITIES = frozenset({"CRITICAL", "HIGH"})
_MAX_JSON_BYTES = 256 * 1024 * 1024


class UsageError(Exception):
    """Invalid invocation or unreadable/unwritable top-level input (exit 2)."""


class ContentError(ValueError):
    """A readable input lacks a required field or has the wrong shape (gate fails)."""


class Unavailable(Exception):
    """An input a gate needs is missing or unparseable (gate status: missing)."""

    def __init__(self, item: str, reason: str, run_id: str | None = None) -> None:
        super().__init__(f"{item}: {reason}")
        self.item = item
        self.reason = reason
        self.run_id = run_id

    def as_details(self) -> dict[str, Any]:
        return {"run_id": self.run_id, "item": self.item, "reason": self.reason}


# ---------------------------------------------------------------------------
# Shape helpers. They raise ContentError so a malformed field fails its gate.
# ---------------------------------------------------------------------------


def _at(value: Any, path: str, where: str) -> Any:
    current = value
    for key in path.split("."):
        if not isinstance(current, dict) or key not in current:
            raise ContentError(f"{where}: missing {path}")
        current = current[key]
    return current


def _obj(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContentError(f"{where} must be an object")
    return value


def _list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContentError(f"{where} must be an array")
    return value


def _bool(value: Any, where: str) -> bool:
    if not isinstance(value, bool):
        raise ContentError(f"{where} must be a boolean")
    return value


def _int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContentError(f"{where} must be an integer")
    return value


def _num(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContentError(f"{where} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise ContentError(f"{where} must be a finite number")
    return number


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _str(value: Any, where: str) -> str:
    if not isinstance(value, str):
        raise ContentError(f"{where} must be a string")
    return value


def _num_list(value: Any, where: str, *, allow_empty: bool = False) -> list[float]:
    values = [_num(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where))]
    if not values and not allow_empty:
        raise ContentError(f"{where} must not be empty")
    return values


def _int_list(value: Any, where: str) -> list[int]:
    values = [_int(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where))]
    if not values:
        raise ContentError(f"{where} must not be empty")
    return values


def _str_list(value: Any, where: str) -> list[str]:
    return [_str(item, f"{where}[{i}]") for i, item in enumerate(_list(value, where))]


def _median(values: Sequence[float]) -> float:
    return float(statistics.median(values))


def _max_or_none(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return max(present) if present else None


def _is_plain_filename(name: str) -> bool:
    """True when ``name`` is a bare file name that cannot escape the run dir."""

    return (
        bool(name)
        and name not in (".", "..")
        and Path(name).name == name
        and PureWindowsPath(name).name == name
    )


def _load_json(path: Path) -> Any:
    """Parse a JSON file, tolerating the UTF-8 BOM Windows PowerShell writes."""

    if path.stat().st_size > _MAX_JSON_BYTES:
        raise ValueError(f"{path.name} exceeds {_MAX_JSON_BYTES} bytes")
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Gates file
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Tolerances:
    iou_match: float
    box: float
    conf: float
    secondary: float
    repeat_determinism: float
    en_synthetic_expected: float
    en_synthetic_tolerance: float
    cross_profile_en_synthetic_max_delta: float


@dataclass(frozen=True)
class Gates:
    sha256: str
    target_flavor: str
    reference_stage: str
    reference_profile: str
    historical_count_vector: tuple[int, ...]
    tiles: tuple[tuple[str, str], ...]
    # v2+: palette-mode originals, used only by YOLO-only (secondary disabled) runs.
    palette_tiles: tuple[tuple[str, str], ...] | None
    model_sha256: dict[str, str]
    tolerances: Tolerances
    memory_relative_max: float
    min_device_free_bytes: int
    perf_relative_max: float
    warmup_discard: int
    measured_runs: int
    borderline_band: float
    borderline_extra_runs: int
    precision_conv: str
    precision_matmul: str
    precision_stages: frozenset[str]
    cuda_build_by_wheel_tag: dict[str, str | None]
    target_arch_required: tuple[str, ...]
    required_phases: tuple[str, ...]

    @property
    def tile_names(self) -> list[str]:
        return [name for name, _ in self.tiles]


def _positive(value: Any, where: str) -> float:
    number = _num(value, where)
    if number <= 0:
        raise ContentError(f"{where} must be greater than 0")
    return number


def _non_negative_int(value: Any, where: str) -> int:
    number = _int(value, where)
    if number < 0:
        raise ContentError(f"{where} must not be negative")
    return number


def _sha(value: Any, where: str) -> str:
    text = _str(value, where)
    if not _SHA256_PATTERN.fullmatch(text):
        raise ContentError(f"{where} must be 64 hexadecimal characters")
    return text.lower()


def _parse_tile_set(value: Any, where: str) -> tuple[tuple[str, str], ...]:
    """Parse [{name, sha256, ...}]; extra per-tile keys (e.g. source_sha256) are ignored."""

    tiles_raw = _list(value, where)
    if not tiles_raw:
        raise ContentError(f"{where} must not be empty")
    tiles = []
    for index, tile in enumerate(tiles_raw):
        label = f"{where}[{index}]"
        tile = _obj(tile, label)
        name = _str(tile.get("name"), f"{label}.name")
        if not _is_plain_filename(name):
            raise ContentError(f"{label}.name must be a plain file name")
        tiles.append((name, _sha(tile.get("sha256"), f"{label}.sha256")))
    return tuple(tiles)


def _parse_gates(doc: Any, sha256: str) -> Gates:
    # Unknown keys (v2 adds "amends", fixture.set/derivation, ...) are ignored.
    doc = _obj(doc, "gates")
    if doc.get("schema_version") != 1:
        raise ContentError("gates schema_version must be 1")

    tiles = _parse_tile_set(_at(doc, "fixture.tiles", "gates"), "gates.fixture.tiles")
    fixture = _obj(doc["fixture"], "gates.fixture")
    palette_tiles = None
    if fixture.get("palette_originals") is not None:
        palette_tiles = _parse_tile_set(
            fixture["palette_originals"], "gates.fixture.palette_originals"
        )
        if len(palette_tiles) != len(tiles):
            raise ContentError("palette_originals length must equal the tile count")

    historical = tuple(
        _int_list(
            _at(doc, "fixture.historical_count_vector", "gates"),
            "gates.fixture.historical_count_vector",
        )
    )
    if len(historical) != len(tiles):
        raise ContentError("historical_count_vector length must equal the tile count")

    tol = _obj(_at(doc, "tolerances", "gates"), "gates.tolerances")
    tolerances = Tolerances(
        **{
            name: _positive(tol.get(name), f"gates.tolerances.{name}")
            for name in Tolerances.__dataclass_fields__
        }
    )
    if tolerances.iou_match > 1:
        raise ContentError("gates.tolerances.iou_match must be at most 1")

    memory = _obj(_at(doc, "memory", "gates"), "gates.memory")
    performance = _obj(_at(doc, "performance", "gates"), "gates.performance")
    precision = _obj(_at(doc, "precision", "gates"), "gates.precision")
    identity = _obj(_at(doc, "identity", "gates"), "gates.identity")

    build_map_raw = _obj(
        identity.get("cuda_build_by_wheel_tag"),
        "gates.identity.cuda_build_by_wheel_tag",
    )
    build_map: dict[str, str | None] = {}
    for tag, build in build_map_raw.items():
        if build is not None:
            build = _str(build, f"gates.identity.cuda_build_by_wheel_tag.{tag}")
        build_map[tag] = build

    required_phases = tuple(
        _str_list(doc.get("required_phases"), "gates.required_phases")
    )
    if not required_phases:
        raise ContentError("gates.required_phases must not be empty")
    for phase in required_phases:
        if not _is_plain_filename(f"{phase}.json"):
            raise ContentError(f"gates.required_phases entry {phase!r} is invalid")

    measured_runs = _int(performance.get("measured_runs"), "gates.performance.measured_runs")
    if measured_runs < 1:
        raise ContentError("gates.performance.measured_runs must be at least 1")

    return Gates(
        sha256=sha256,
        target_flavor=_str(doc.get("target_flavor"), "gates.target_flavor"),
        reference_stage=_str(_at(doc, "reference.outputs_stage", "gates"), "stage"),
        reference_profile=_str(_at(doc, "reference.outputs_profile", "gates"), "profile"),
        historical_count_vector=historical,
        tiles=tiles,
        palette_tiles=palette_tiles,
        model_sha256={
            "yolo": _sha(_at(doc, "models.yolo_sha256", "gates"), "yolo_sha256"),
            "efficientnet": _sha(
                _at(doc, "models.efficientnet_sha256", "gates"),
                "efficientnet_sha256",
            ),
        },
        tolerances=tolerances,
        memory_relative_max=_positive(
            memory.get("relative_max"), "gates.memory.relative_max"
        ),
        min_device_free_bytes=_non_negative_int(
            memory.get("min_device_free_bytes"), "gates.memory.min_device_free_bytes"
        ),
        perf_relative_max=_positive(
            performance.get("relative_max"), "gates.performance.relative_max"
        ),
        warmup_discard=_non_negative_int(
            performance.get("warmup_discard"), "gates.performance.warmup_discard"
        ),
        measured_runs=measured_runs,
        borderline_band=_positive(
            performance.get("borderline_band"), "gates.performance.borderline_band"
        ),
        borderline_extra_runs=_non_negative_int(
            performance.get("borderline_extra_runs"),
            "gates.performance.borderline_extra_runs",
        ),
        precision_conv=_str(precision.get("conv"), "gates.precision.conv"),
        precision_matmul=_str(precision.get("matmul"), "gates.precision.matmul"),
        precision_stages=frozenset(
            _str_list(precision.get("applies_to_stages"), "applies_to_stages")
        ),
        cuda_build_by_wheel_tag=build_map,
        target_arch_required=tuple(
            _str_list(identity.get("target_arch_required"), "target_arch_required")
        ),
        required_phases=required_phases,
    )


def load_gates(path: Path) -> Gates:
    """Load and validate the gates file; any problem is a usage error."""

    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise UsageError(f"cannot read gates file {path}: {exc}") from exc
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UsageError(f"gates file {path} is not valid JSON: {exc}") from exc
    try:
        return _parse_gates(doc, _sha256_bytes(raw))
    except ContentError as exc:
        raise UsageError(f"invalid gates file {path}: {exc}") from exc


# ---------------------------------------------------------------------------
# Run directories
# ---------------------------------------------------------------------------


class RunDir:
    """One probe run directory: ``run.json`` plus lazily loaded phase files."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.run: dict[str, Any] | None = None
        self.run_error: str | None = None
        self._phases: dict[str, dict[str, Any] | Unavailable] = {}
        try:
            doc = _load_json(path / "run.json")
        except FileNotFoundError:
            self.run_error = "run.json not found"
        except (OSError, ValueError) as exc:
            self.run_error = f"run.json unreadable: {exc}"
        else:
            if not isinstance(doc, dict):
                self.run_error = "run.json must be an object"
            elif doc.get("schema_version") != 1:
                self.run_error = "run.json schema_version must be 1"
            else:
                self.run = doc

    @property
    def run_id(self) -> str:
        run_id = self.run.get("run_id") if self.run else None
        return run_id if isinstance(run_id, str) and run_id else self.path.name

    def value(self, dotted: str) -> Any:
        """Return a run.json value by dotted path, or None when absent."""

        current: Any = self.run
        for key in dotted.split("."):
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current

    def require_run(self) -> dict[str, Any]:
        if self.run is None:
            raise Unavailable("run.json", self.run_error or "unavailable", self.run_id)
        return self.run

    def phase_file_name(self, phase: str) -> str:
        entry = self.value(f"phases.{phase}")
        if isinstance(entry, dict) and "file" in entry:
            declared = entry["file"]
            if not isinstance(declared, str) or not _is_plain_filename(declared):
                raise Unavailable(
                    f"{phase} phase",
                    f"run.json declares an unsafe phase file {declared!r}",
                    self.run_id,
                )
            return declared
        return f"{phase}.json"

    def phase(self, phase: str) -> dict[str, Any]:
        """Return a parsed phase document or raise Unavailable."""

        cached = self._phases.get(phase)
        if isinstance(cached, Unavailable):
            raise cached
        if cached is not None:
            return cached
        try:
            doc = self._load_phase(phase)
        except Unavailable as exc:
            self._phases[phase] = exc
            raise
        self._phases[phase] = doc
        return doc

    def try_phase(self, phase: str) -> dict[str, Any] | None:
        try:
            return self.phase(phase)
        except Unavailable:
            return None

    def _load_phase(self, phase: str) -> dict[str, Any]:
        name = self.phase_file_name(phase)
        try:
            doc = _load_json(self.path / name)
        except FileNotFoundError:
            raise Unavailable(name, "file not found", self.run_id) from None
        except (OSError, ValueError) as exc:
            raise Unavailable(name, f"unparseable: {exc}", self.run_id) from None
        if not isinstance(doc, dict):
            raise Unavailable(name, "phase document must be an object", self.run_id)
        if doc.get("schema_version") != 1:
            raise Unavailable(name, "schema_version must be 1", self.run_id)
        if doc.get("phase") != phase:
            raise Unavailable(
                name, f"phase field {doc.get('phase')!r} != {phase!r}", self.run_id
            )
        return doc


@dataclass(frozen=True)
class CombinedRun:
    index: int
    warmup: bool
    seconds: float
    raw: dict[str, Any]


def _combined_runs(combined: dict[str, Any], where: str) -> list[CombinedRun]:
    runs = []
    for position, run in enumerate(_list(_at(combined, "runs", where), f"{where}.runs")):
        label = f"{where}.runs[{position}]"
        run = _obj(run, label)
        runs.append(
            CombinedRun(
                index=_int(run.get("index"), f"{label}.index"),
                warmup=_bool(run.get("warmup"), f"{label}.warmup"),
                seconds=_num(run.get("seconds"), f"{label}.seconds"),
                raw=run,
            )
        )
    if len({run.index for run in runs}) != len(runs):
        raise ContentError(f"{where}.runs has duplicate index values")
    return sorted(runs, key=lambda run: run.index)


def _normalize_detection(value: Any, where: str) -> dict[str, Any]:
    detection = _obj(value, where)
    normalized: dict[str, Any] = {
        name: _num(detection.get(name), f"{where}.{name}") for name in _FLOAT_FIELDS
    }
    class_id = detection.get("class")
    if isinstance(class_id, float) and class_id.is_integer():
        class_id = int(class_id)
    normalized["class"] = _int(class_id, f"{where}.class")
    normalized["class_name"] = _str(detection.get("class_name"), f"{where}.class_name")
    return normalized


def _run_results(run: CombinedRun, tile_count: int, where: str) -> list[list[dict]]:
    label = f"{where}.runs[index={run.index}].results"
    results = _list(run.raw.get("results"), label)
    if len(results) != tile_count:
        raise ContentError(f"{label} has {len(results)} tiles, expected {tile_count}")
    return [
        [
            _normalize_detection(detection, f"{label}[{tile}][{position}]")
            for position, detection in enumerate(_list(tile_results, f"{label}[{tile}]"))
        ]
        for tile, tile_results in enumerate(results)
    ]


def _run_en(run: CombinedRun, where: str) -> dict[str, Any]:
    label = f"{where}.runs[index={run.index}].en"
    en = _obj(run.raw.get("en"), label)
    errors = _list(en.get("errors"), f"{label}.errors")
    return {
        "calls": _int(en.get("calls"), f"{label}.calls"),
        "candidates": _int(en.get("candidates"), f"{label}.candidates"),
        "batches": _int(en.get("batches"), f"{label}.batches"),
        # Any entry counts as an error, whatever its type.
        "errors": [error if isinstance(error, str) else json.dumps(error) for error in errors],
    }


def _tile_manifest(combined: dict[str, Any], where: str) -> list[dict[str, str]]:
    tiles = []
    for index, tile in enumerate(_list(_at(combined, "tiles", where), f"{where}.tiles")):
        tile = _obj(tile, f"{where}.tiles[{index}]")
        tiles.append(
            {
                "name": _str(tile.get("name"), f"{where}.tiles[{index}].name"),
                "sha256": _str(tile.get("sha256"), f"{where}.tiles[{index}].sha256").lower(),
            }
        )
    return tiles


# ---------------------------------------------------------------------------
# Detection matching
# ---------------------------------------------------------------------------


def iou(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Intersection over union of two x1/y1/x2/y2 boxes."""

    width = min(first["x2"], second["x2"]) - max(first["x1"], second["x1"])
    height = min(first["y2"], second["y2"]) - max(first["y1"], second["y1"])
    intersection = max(0.0, width) * max(0.0, height)
    area_first = max(0.0, first["x2"] - first["x1"]) * max(0.0, first["y2"] - first["y1"])
    area_second = max(0.0, second["x2"] - second["x1"]) * max(
        0.0, second["y2"] - second["y1"]
    )
    union = area_first + area_second - intersection
    if union <= 0:
        # Degenerate (zero-area) boxes only overlap when they are identical.
        identical = all(first[name] == second[name] for name in _BOX_FIELDS)
        return 1.0 if identical else 0.0
    return intersection / union


def match_tile(
    reference: Sequence[dict[str, Any]],
    candidate: Sequence[dict[str, Any]],
    *,
    iou_match: float,
    box: float,
    conf: float,
    secondary: float,
) -> dict[str, Any]:
    """Greedily match one tile's detections by IoU and apply value tolerances.

    Reference detections are visited in descending confidence (ties keep list
    order); each takes the unmatched same-class candidate with the highest IoU,
    which must reach ``iou_match``. List order on either side is irrelevant, so
    NMS tie reordering between runtimes does not cause false mismatches.
    """

    order = sorted(range(len(reference)), key=lambda i: (-reference[i]["conf"], i))
    available = list(range(len(candidate)))
    pairs: list[tuple[int, int, float]] = []
    unmatched_reference = []
    for ref_index in order:
        ref = reference[ref_index]
        best_index: int | None = None
        best_iou = 0.0
        for cand_index in available:
            if candidate[cand_index]["class"] != ref["class"]:
                continue
            overlap = iou(ref, candidate[cand_index])
            if best_index is None or overlap > best_iou:
                best_index, best_iou = cand_index, overlap
        if best_index is None or best_iou < iou_match:
            unmatched_reference.append(
                {
                    "index": ref_index,
                    "best_iou": None if best_index is None else best_iou,
                    "detection": ref,
                }
            )
            continue
        available.remove(best_index)
        pairs.append((ref_index, best_index, best_iou))

    unmatched_candidate = [{"index": i, "detection": candidate[i]} for i in available]
    matches = []
    violations = []
    for ref_index, cand_index, overlap in pairs:
        ref = reference[ref_index]
        cand = candidate[cand_index]
        record: dict[str, Any] = {
            "reference_index": ref_index,
            "candidate_index": cand_index,
            "iou": overlap,
            "box_delta": max(abs(ref[name] - cand[name]) for name in _BOX_FIELDS),
            "conf_delta": abs(ref["conf"] - cand["conf"]),
            "secondary_delta": abs(ref["secondary"] - cand["secondary"]),
        }
        within = (
            record["box_delta"] <= box
            and record["conf_delta"] <= conf
            and record["secondary_delta"] <= secondary
        )
        if ref["class_name"] != cand["class_name"]:
            record["class_name"] = [ref["class_name"], cand["class_name"]]
            within = False
        matches.append(record)
        if not within:
            violations.append(record)

    return {
        "reference_count": len(reference),
        "candidate_count": len(candidate),
        "matched": len(pairs),
        "min_iou": min((pair[2] for pair in pairs), default=None),
        "max_box_delta": _max_or_none(m["box_delta"] for m in matches),
        "max_conf_delta": _max_or_none(m["conf_delta"] for m in matches),
        "max_secondary_delta": _max_or_none(m["secondary_delta"] for m in matches),
        "unmatched_reference": unmatched_reference,
        "unmatched_candidate": unmatched_candidate,
        "violations": violations,
        "passed": not unmatched_reference and not unmatched_candidate and not violations,
    }


def compare_detection_sets(
    reference_tiles: Sequence[Sequence[dict[str, Any]]],
    candidate_tiles: Sequence[Sequence[dict[str, Any]]],
    tile_names: Sequence[str],
    *,
    iou_match: float,
    box: float,
    conf: float,
    secondary: float,
) -> dict[str, Any]:
    """Match every tile and summarize the worst deltas across the fixture."""

    tiles = []
    for name, reference, candidate in zip(tile_names, reference_tiles, candidate_tiles):
        result = match_tile(
            reference, candidate, iou_match=iou_match, box=box, conf=conf, secondary=secondary
        )
        tiles.append({"tile": name, **result})
    return {
        "passed": all(tile["passed"] for tile in tiles),
        "max_box_delta": _max_or_none(tile["max_box_delta"] for tile in tiles),
        "max_conf_delta": _max_or_none(tile["max_conf_delta"] for tile in tiles),
        "max_secondary_delta": _max_or_none(tile["max_secondary_delta"] for tile in tiles),
        "min_iou": min(
            (tile["min_iou"] for tile in tiles if tile["min_iou"] is not None), default=None
        ),
        "unmatched_reference": sum(len(tile["unmatched_reference"]) for tile in tiles),
        "unmatched_candidate": sum(len(tile["unmatched_candidate"]) for tile in tiles),
        "violations": sum(len(tile["violations"]) for tile in tiles),
        "tiles": tiles,
    }


# ---------------------------------------------------------------------------
# Evaluation context and gate plumbing
# ---------------------------------------------------------------------------


@dataclass
class Context:
    gates: Gates
    reference: RunDir
    candidates: list[RunDir]
    baselines: list[RunDir] = field(default_factory=list)
    cpu_counterpart: RunDir | None = None
    scan_reference: Path | None = None
    scan_candidate: Path | None = None
    scan_dispositions: Path | None = None
    check_historical_vector: bool = False
    findings: list[dict[str, Any]] = field(default_factory=list)

    @property
    def primary(self) -> RunDir:
        return self.candidates[0]

    def require_profile(self) -> str:
        profile = self.primary.require_run().get("profile")
        if profile not in _PROFILES:
            raise ContentError(f"run.json profile must be cpu or cuda, got {profile!r}")
        return profile

    def require_stage(self) -> str:
        return _str(self.primary.require_run().get("stage"), "run.json stage")

    def add_finding(self, finding_id: str, severity: str, message: str, **data: Any) -> None:
        self.findings.append(
            {"id": finding_id, "severity": severity, "message": message, **data}
        )


def _pairing_problems(
    anchor: RunDir, others: Sequence[RunDir], role: str, keys: Sequence[str]
) -> list[str]:
    """Describe run.json fields that differ between ``anchor`` and ``others``."""

    anchor.require_run()
    problems = []
    for other in others:
        other.require_run()
        for key in keys:
            expected, actual = anchor.value(key), other.value(key)
            if expected is None or actual != expected:
                problems.append(
                    f"{role} {other.run_id}: {key} {actual!r} != {anchor.run_id} {expected!r}"
                )
    return problems


def _candidate_pool_problems(ctx: Context) -> list[str]:
    return _pairing_problems(
        ctx.primary, ctx.candidates[1:], "candidate", ("host", "profile", "stage", "image.id")
    )


def _baseline_pool_problems(ctx: Context) -> list[str]:
    problems = _pairing_problems(ctx.primary, ctx.baselines, "baseline", ("host", "profile"))
    if ctx.baselines:
        problems += _pairing_problems(
            ctx.baselines[0], ctx.baselines[1:], "baseline", ("stage", "image.id")
        )
    return problems


def _checked(
    checks: dict[str, bool], details: dict[str, Any], summary: str
) -> dict[str, Any]:
    failed = [name for name, ok in checks.items() if not ok]
    body: dict[str, Any] = {"checks": checks, **details}
    if failed:
        body["failed_checks"] = failed
        summary = f"failed: {', '.join(failed)}" + (f"; {summary}" if summary else "")
    return {"status": FAIL if failed else PASS, "summary": summary, "details": body}


def _not_applicable(reason: str, **details: Any) -> dict[str, Any]:
    return {
        "status": NOT_APPLICABLE,
        "summary": f"not applicable: {reason}",
        "details": {"reason": reason, **details},
    }


def _fmt(value: float | None, digits: int = 3) -> str:
    return "n/a" if value is None else f"{value:.{digits}g}"


# ---------------------------------------------------------------------------
# Gates
# ---------------------------------------------------------------------------


def _base_version(version: str) -> str:
    return version.split("+", 1)[0]


def gate_g1(ctx: Context) -> dict[str, Any]:
    """G1 identity: the probe's four identity checks plus cross-checks."""

    identity = ctx.primary.phase("identity")
    run = ctx.primary.require_run()
    probe_checks = _obj(_at(identity, "checks", "identity"), "identity.checks")
    versions = _obj(_at(identity, "versions", "identity"), "identity.versions")
    expected = _obj(run.get("expected"), "run.json expected")

    checks = {name: probe_checks.get(name) is True for name in _IDENTITY_CHECKS}
    # Recompute the version and CUDA-build facts from the gates map so a probe
    # bug cannot silently report a match.
    build_map = ctx.gates.cuda_build_by_wheel_tag
    wheel_tag = expected.get("wheel_tag")
    tag_known = isinstance(wheel_tag, str) and wheel_tag in build_map
    declared_build = build_map[wheel_tag] if tag_known else None
    torch_version = _str(versions.get("torch"), "identity.versions.torch")
    torchvision_version = _str(versions.get("torchvision"), "identity.versions.torchvision")
    checks["torch_matches_expected"] = _base_version(torch_version) == expected.get("torch")
    checks["torchvision_matches_expected"] = (
        _base_version(torchvision_version) == expected.get("torchvision")
    )
    checks["wheel_tag_declared_in_gates"] = tag_known
    checks["expected_cuda_build_matches_gates"] = (
        tag_known and expected.get("cuda_build") == declared_build
    )
    checks["torch_cuda_build_matches_gates"] = (
        tag_known and versions.get("torch_cuda_build") == declared_build
    )

    return _checked(
        checks,
        {
            "versions": versions,
            "expected": expected,
            "declared_cuda_build": declared_build,
            "pip_check": identity.get("pip_check"),
        },
        f"torch {torch_version}, torchvision {torchvision_version}, "
        f"CUDA build {versions.get('torch_cuda_build')}",
    )


def _cuda_execution_evidence(rd: RunDir) -> dict[str, Any]:
    """Proof that real CUDA work succeeded, used when kernel_probe_ok is null."""

    synthetic = rd.phase("synthetic")
    combined = rd.phase("combined")
    checks = {
        "synthetic_ok": synthetic.get("ok") is True,
        "combined_ok": combined.get("ok") is True,
        "synthetic_selected_cuda": _selected_devices_match(synthetic, "cuda"),
        "combined_selected_cuda": _selected_devices_match(combined, "cuda"),
        "combined_observed_cuda": all(_observed_device_checks(combined, "cuda").values()),
    }
    return {"checks": checks, "passed": all(checks.values())}


def gate_g2(ctx: Context) -> dict[str, Any]:
    """G2 arch coverage: CUDA usable, kernels run, target arches compiled in."""

    profile = ctx.require_profile()
    if profile == "cpu":
        return _not_applicable("profile is cpu")
    identity = ctx.primary.phase("identity")
    cuda = _obj(_at(identity, "cuda", "identity"), "identity.cuda")
    arch_list = _str_list(cuda.get("arch_list"), "identity.cuda.arch_list")
    kernel_probe = cuda.get("kernel_probe_ok")
    details: dict[str, Any] = {
        "device_name": cuda.get("device_name"),
        "capability": cuda.get("capability"),
        "arch_list": arch_list,
        "arch_supported": cuda.get("arch_supported"),
        "kernel_probe_ok": kernel_probe,
    }
    checks = {
        "cuda_available": cuda.get("available") is True,
        # The probe reports None when coverage is unknown; only False is gating.
        "device_arch_not_unsupported": cuda.get("arch_supported") is not False,
    }
    if kernel_probe is None:
        # Stage-A images predate the kernel probe: accept only real CUDA work.
        evidence = _cuda_execution_evidence(ctx.primary)
        checks["kernel_execution_evidence"] = evidence["passed"]
        details["kernel_probe"] = "unknown_fallback_to_execution_evidence"
        details["execution_evidence"] = evidence
        ctx.add_finding(
            "kernel_probe_unknown",
            "info",
            "kernel_probe_ok is null; G2 relied on synthetic+combined CUDA execution "
            f"evidence (passed={evidence['passed']}).",
            run_id=ctx.primary.run_id,
        )
    else:
        checks["kernel_probe_ok"] = kernel_probe is True

    flavor = ctx.primary.require_run().get("flavor")
    if flavor == ctx.gates.target_flavor:
        missing = [arch for arch in ctx.gates.target_arch_required if arch not in arch_list]
        checks["target_arch_coverage"] = not missing
        details["target_arch_required"] = list(ctx.gates.target_arch_required)
        details["missing_arch"] = missing
    else:
        details["target_arch_coverage"] = f"not required for flavor {flavor!r}"

    return _checked(
        checks,
        details,
        f"{cuda.get('device_name')} {cuda.get('capability')}; kernel probe "
        f"{'unknown' if kernel_probe is None else kernel_probe}; arch {','.join(arch_list)}",
    )


def _devices_on(devices: Any, profile: str, *, allow_empty: bool = False) -> bool:
    """True for a list whose entries are all ``profile`` or ``profile:N``."""

    return (
        isinstance(devices, list)
        and (bool(devices) or allow_empty)
        and all(
            isinstance(device, str)
            and (device == profile or device.startswith(f"{profile}:"))
            for device in devices
        )
    )


def _secondary_enabled(combined: dict[str, Any], where: str) -> bool:
    """combined.secondary_enabled; absent means EfficientNet ran (the default)."""

    return _bool(combined.get("secondary_enabled", True), f"{where}.secondary_enabled")


def _observed_device_checks(combined: dict[str, Any], profile: str) -> dict[str, bool]:
    # YOLO-only runs (secondary_enabled false) never forward EfficientNet, so its
    # observed list may be empty; any entry present must still be on the profile.
    observed = combined.get("observed_devices")
    observed = observed if isinstance(observed, dict) else {}
    secondary = _secondary_enabled(combined, "combined")
    return {
        f"observed_{model}_on_{profile}": _devices_on(
            observed.get(model),
            profile,
            allow_empty=model == "efficientnet" and not secondary,
        )
        for model in _MODELS
    }


def _selected_devices_match(doc: dict[str, Any], profile: str) -> bool:
    selected = doc.get("selected_devices")
    return isinstance(selected, dict) and all(selected.get(m) == profile for m in _MODELS)


def gate_g3(ctx: Context) -> dict[str, Any]:
    """G3 observed devices: real forward passes ran on the requested device."""

    profile = ctx.require_profile()
    combined = ctx.primary.phase("combined")
    observed = _obj(_at(combined, "observed_devices", "combined"), "observed_devices")
    checks = _observed_device_checks(combined, profile)
    checks["combined_selected_devices_match"] = _selected_devices_match(combined, profile)
    details: dict[str, Any] = {
        "requested": profile,
        "secondary_enabled": _secondary_enabled(combined, "combined"),
        "observed_devices": observed,
        "combined_selected_devices": combined.get("selected_devices"),
    }
    synthetic = ctx.primary.try_phase("synthetic")
    if synthetic is not None:
        checks["synthetic_selected_devices_match"] = _selected_devices_match(
            synthetic, profile
        )
        details["synthetic_selected_devices"] = synthetic.get("selected_devices")
    return _checked(
        checks,
        details,
        f"observed yolo={observed.get('yolo')} efficientnet={observed.get('efficientnet')}",
    )


def gate_g4(ctx: Context) -> dict[str, Any]:
    """G4 model trust: model file hashes equal the declared digests."""

    identity = ctx.primary.phase("identity")
    hashes = _obj(_at(identity, "model_sha256", "identity"), "identity.model_sha256")
    checks = {}
    for model in _MODELS:
        observed = hashes.get(model)
        checks[f"{model}_sha256_matches"] = (
            isinstance(observed, str) and observed.lower() == ctx.gates.model_sha256[model]
        )
    return _checked(
        checks,
        {"observed": hashes, "declared": ctx.gates.model_sha256},
        "yolo and efficientnet digests compared case-insensitively",
    )


def gate_g5(ctx: Context) -> dict[str, Any]:
    """G5 precision: CUDA fp32 conv/matmul precision pinned to declared values."""

    if ctx.require_profile() == "cpu":
        return _not_applicable("profile is cpu")
    stage = ctx.require_stage()
    if stage not in ctx.gates.precision_stages:
        return _not_applicable(
            f"stage {stage} not in {sorted(ctx.gates.precision_stages)}"
        )
    identity = ctx.primary.phase("identity")
    precision = _obj(_at(identity, "precision", "identity"), "identity.precision")
    checks = {
        "conv_matches": precision.get("conv") == ctx.gates.precision_conv,
        "matmul_matches": precision.get("matmul") == ctx.gates.precision_matmul,
        "override_env_unset": precision.get("override_env") in _PRECISION_OVERRIDE_OFF,
    }
    return _checked(
        checks,
        {
            "observed": precision,
            "declared": {"conv": ctx.gates.precision_conv, "matmul": ctx.gates.precision_matmul},
        },
        f"api {precision.get('api')}: conv={precision.get('conv')} "
        f"matmul={precision.get('matmul')} override={precision.get('override_env')!r}",
    )


def _en_scores(rd: RunDir, where: str) -> list[float]:
    synthetic = rd.phase("synthetic")
    return _num_list(
        _at(synthetic, "efficientnet.scores", where), f"{where}.efficientnet.scores"
    )


def gate_g6(ctx: Context) -> dict[str, Any]:
    """G6 synthetic: blank-image YOLO/EN outputs, NMS probe, CPU/CUDA EN delta."""

    tol = ctx.gates.tolerances
    profile = ctx.require_profile()
    synthetic = ctx.primary.phase("synthetic")
    counts = _int_list(
        _at(synthetic, "yolo.detection_counts", "synthetic"), "yolo.detection_counts"
    )
    scores = _en_scores(ctx.primary, "synthetic")
    deviation = max(abs(score - tol.en_synthetic_expected) for score in scores)
    nms = _obj(_at(synthetic, "nms_probe", "synthetic"), "synthetic.nms_probe")
    probe_checks = synthetic.get("checks")
    probe_checks = probe_checks if isinstance(probe_checks, dict) else {}
    # Only an explicit False from the probe is gating; unknown keys are recorded.
    probe_failed = sorted(name for name, value in probe_checks.items() if value is False)

    checks = {
        "yolo_detection_counts_zero": all(count == 0 for count in counts),
        "en_scores_within_tolerance": deviation <= tol.en_synthetic_tolerance,
        "nms_probe_ok": nms.get("ok") is True,
        "probe_checks_not_false": not probe_failed,
    }
    details: dict[str, Any] = {
        "yolo_detection_counts": counts,
        "en_scores": scores,
        "en_expected": tol.en_synthetic_expected,
        "en_tolerance": tol.en_synthetic_tolerance,
        "en_max_deviation": deviation,
        "nms_probe": nms,
        "probe_checks": probe_checks,
        "probe_checks_failed": probe_failed,
    }
    summary = f"yolo counts {counts}; EN max deviation {_fmt(deviation)}"

    counterpart = ctx.cpu_counterpart
    if counterpart is None:
        details["cross_profile"] = {"status": NOT_APPLICABLE, "reason": "no --cpu-counterpart"}
    elif profile != "cuda":
        details["cross_profile"] = {
            "status": NOT_APPLICABLE,
            "reason": "candidate profile is cpu",
        }
    else:
        problems = _pairing_problems(
            ctx.primary, [counterpart], "cpu-counterpart", ("host", "stage")
        )
        if counterpart.value("profile") != "cpu":
            problems.append(
                f"cpu-counterpart {counterpart.run_id}: profile "
                f"{counterpart.value('profile')!r} is not 'cpu'"
            )
        cpu_scores = _en_scores(counterpart, "cpu-counterpart synthetic")
        delta = abs(_median(scores) - _median(cpu_scores))
        limit = tol.cross_profile_en_synthetic_max_delta
        checks["cpu_counterpart_paired"] = not problems
        checks["cross_profile_en_delta_within_limit"] = delta <= limit
        details["cross_profile"] = {
            "counterpart": counterpart.run_id,
            "cuda_median_score": _median(scores),
            "cpu_median_score": _median(cpu_scores),
            "delta": delta,
            "max_delta": limit,
            "pairing_problems": problems,
        }
        summary += f"; cuda-cpu EN delta {_fmt(delta)}"
    return _checked(checks, details, summary)


def gate_g7(ctx: Context) -> dict[str, Any]:
    """G7 combined outputs: per-detection parity with the reference outputs."""

    gates = ctx.gates
    tol = gates.tolerances
    candidate_doc = ctx.primary.phase("combined")
    reference_doc = ctx.reference.phase("combined")
    secondary = _secondary_enabled(candidate_doc, "combined")
    reference_secondary = _secondary_enabled(reference_doc, "reference combined")
    # YOLO-only runs use the palette-mode originals when the gates declare them
    # (v2+); every EfficientNet-enabled run must use the declared fixture tiles.
    if not secondary and gates.palette_tiles is not None:
        tile_set_name, tile_set = "palette_originals", gates.palette_tiles
    else:
        tile_set_name, tile_set = "tiles", gates.tiles
    names = [name for name, _ in tile_set]
    expected_tiles = [{"name": name, "sha256": sha} for name, sha in tile_set]

    checks = {
        "secondary_enabled_matches_reference": secondary == reference_secondary,
        "tile_hashes_verified": candidate_doc.get("tile_hashes_verified") is True,
        "tiles_match_gates": _tile_manifest(candidate_doc, "combined") == expected_tiles,
        "reference_tiles_match_gates": (
            _tile_manifest(reference_doc, "reference combined") == expected_tiles
        ),
    }
    details: dict[str, Any] = {
        "reference": {
            "run_id": ctx.reference.run_id,
            "stage": ctx.reference.value("stage"),
            "profile": ctx.reference.value("profile"),
            "secondary_enabled": reference_secondary,
        },
        "secondary_enabled": secondary,
        "tile_set": f"fixture.{tile_set_name}",
    }
    if not secondary:
        ctx.add_finding(
            "secondary_disabled",
            "warning",
            "combined ran YOLO-only (secondary_enabled=false): EfficientNet combined "
            "requirements were not applicable, so this verdict does not qualify the "
            "EfficientNet combined path.",
            run_id=ctx.primary.run_id,
        )

    candidate_runs = _combined_runs(candidate_doc, "combined")
    reference_runs = _combined_runs(reference_doc, "reference combined")
    candidate_measured = [run for run in candidate_runs if not run.warmup]
    reference_measured = [run for run in reference_runs if not run.warmup]
    checks["candidate_has_measured_run"] = bool(candidate_measured)
    checks["reference_has_measured_run"] = bool(reference_measured)

    # EN errors anywhere (warm-up runs included) disqualify the run.
    en_errors = [
        {"run_index": run.index, "error": error}
        for run in candidate_runs
        for error in _run_en(run, "combined")["errors"]
    ]
    reference_en_errors = [
        {"run_index": run.index, "error": error}
        for run in reference_runs
        for error in _run_en(run, "reference combined")["errors"]
    ]
    checks["en_errors_absent"] = not en_errors
    checks["reference_en_errors_absent"] = not reference_en_errors
    details["en_errors"] = en_errors
    details["reference_en_errors"] = reference_en_errors

    log = _obj(_at(candidate_doc, "log_findings", "combined"), "combined.log_findings")
    log_counts = {key: _int(log.get(key), f"log_findings.{key}") for key in _LOG_FINDING_KEYS}
    checks["log_findings_clean"] = all(count == 0 for count in log_counts.values())
    details["log_findings"] = log_counts

    summary = "no measured run to compare"
    if candidate_measured and reference_measured:
        candidate_last = candidate_measured[-1]
        reference_last = reference_measured[-1]
        candidate_results = _run_results(candidate_last, len(names), "combined")
        reference_results = _run_results(reference_last, len(names), "reference combined")
        candidate_counts = [len(tile) for tile in candidate_results]
        reference_counts = [len(tile) for tile in reference_results]
        checks["count_vector_matches_reference"] = candidate_counts == reference_counts

        outputs = compare_detection_sets(
            reference_results,
            candidate_results,
            names,
            iou_match=tol.iou_match,
            box=tol.box,
            conf=tol.conf,
            secondary=tol.secondary,
        )
        checks["detections_match_reference"] = outputs["passed"]

        candidate_en = _run_en(candidate_last, "combined")
        reference_en = _run_en(reference_last, "reference combined")
        if secondary:
            checks["en_candidates_match_reference"] = (
                candidate_en["candidates"] == reference_en["candidates"]
            )
            checks["en_candidates_positive"] = candidate_en["candidates"] > 0
            checks["en_batches_positive"] = candidate_en["batches"] >= 1
        else:
            details["en_requirements"] = "not_applicable: secondary_enabled is false"

        # Repeat determinism: every measured run against the first measured run.
        first_results = _run_results(candidate_measured[0], len(names), "combined")
        determinism = []
        for run in candidate_measured[1:]:
            repeat = compare_detection_sets(
                first_results,
                _run_results(run, len(names), "combined"),
                names,
                iou_match=tol.iou_match,
                box=tol.repeat_determinism,
                conf=tol.repeat_determinism,
                secondary=tol.repeat_determinism,
            )
            determinism.append(
                {
                    "run_index": run.index,
                    "against_run_index": candidate_measured[0].index,
                    "passed": repeat["passed"],
                    "max_box_delta": repeat["max_box_delta"],
                    "max_conf_delta": repeat["max_conf_delta"],
                    "max_secondary_delta": repeat["max_secondary_delta"],
                    "unmatched_reference": repeat["unmatched_reference"],
                    "unmatched_candidate": repeat["unmatched_candidate"],
                    "violations": repeat["violations"],
                    "failed_tiles": [t for t in repeat["tiles"] if not t["passed"]],
                }
            )
        checks["repeat_determinism"] = all(entry["passed"] for entry in determinism)

        details["reference"]["run_index"] = reference_last.index
        details["candidate_run_index"] = candidate_last.index
        details["measured_run_indexes"] = [run.index for run in candidate_measured]
        details["count_vectors"] = {
            "reference": reference_counts,
            "candidate": candidate_counts,
        }
        details["tolerances"] = {
            "iou_match": tol.iou_match,
            "box": tol.box,
            "conf": tol.conf,
            "secondary": tol.secondary,
            "repeat_determinism": tol.repeat_determinism,
        }
        details["max_deltas"] = {
            "box": outputs["max_box_delta"],
            "conf": outputs["max_conf_delta"],
            "secondary": outputs["max_secondary_delta"],
            "min_iou": outputs["min_iou"],
        }
        details["unmatched"] = {
            "reference": outputs["unmatched_reference"],
            "candidate": outputs["unmatched_candidate"],
        }
        details["tolerance_violations"] = outputs["violations"]
        details["tiles"] = outputs["tiles"]
        details["en"] = {"reference": reference_en, "candidate": candidate_en}
        details["determinism"] = determinism
        summary = (
            f"counts {candidate_counts}; max delta box {_fmt(outputs['max_box_delta'])} "
            f"conf {_fmt(outputs['max_conf_delta'])} "
            f"sec {_fmt(outputs['max_secondary_delta'])}; unmatched "
            f"{outputs['unmatched_reference']}/{outputs['unmatched_candidate']}; "
            + (
                f"EN candidates {candidate_en['candidates']}"
                if secondary
                else "YOLO-only (EN n/a)"
            )
        )

    contract = candidate_doc.get("contract")
    if isinstance(contract, dict):
        # The in-container contract uses its own manifest tolerances, which are not
        # part of the declared gates, so it is evidence rather than a gate input.
        contract_passed = contract.get("passed") is True
        details["contract"] = {"passed": contract_passed, "checks": contract.get("checks")}
        if not contract_passed:
            ctx.add_finding(
                "combined_contract_failed",
                "warning",
                "combined.contract.passed is not true (informational; G7 uses gates tolerances).",
                run_id=ctx.primary.run_id,
                checks=contract.get("checks"),
            )
    else:
        details["contract"] = None
    return _checked(checks, details, summary)


def _relative(
    candidate_values: Sequence[float], baseline_values: Sequence[float], relative_max: float
) -> dict[str, Any]:
    candidate_median = _median(candidate_values)
    baseline_median = _median(baseline_values)
    limit = relative_max * baseline_median
    return {
        "candidate_median": candidate_median,
        "baseline_median": baseline_median,
        "limit": limit,
        "ratio": candidate_median / baseline_median if baseline_median > 0 else None,
        "candidate_count": len(candidate_values),
        "baseline_count": len(baseline_values),
        "passed": candidate_median <= limit,
    }


def _memory_docs(runs: Sequence[RunDir]) -> list[tuple[RunDir, dict[str, Any]]]:
    return [(rd, rd.phase("memory")) for rd in runs]


def gate_g8(ctx: Context) -> dict[str, Any]:
    """G8 memory: device headroom, EN errors, and relative host/device growth."""

    gates = ctx.gates
    profile = ctx.require_profile()
    candidates = _memory_docs(ctx.candidates)
    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}

    en_errors = [
        {"run_id": rd.run_id, "error": error if isinstance(error, str) else json.dumps(error)}
        for rd, memory in candidates
        for error in _list(_at(memory, "en.errors", "memory"), "memory.en.errors")
    ]
    checks["memory_en_errors_absent"] = not en_errors
    details["en_errors"] = en_errors

    headroom = []
    for rd, memory in candidates:
        cuda = _at(memory, "cuda", "memory")
        if cuda is None:
            headroom.append({"run_id": rd.run_id, "cuda": None})
            continue
        cuda = _obj(cuda, "memory.cuda")
        min_free = cuda.get("min_free_bytes")
        samples = cuda.get("samples")
        # A failed device sampler reports min_free_bytes null / samples 0: that
        # is unproven headroom (fail), not a malformed document.
        sampled = _is_int(min_free) and _is_int(samples) and samples >= 1
        headroom.append(
            {
                "run_id": rd.run_id,
                "min_free_bytes": min_free,
                "total_bytes": cuda.get("total_bytes"),
                "samples": samples,
                "sampler_error": cuda.get("sampler_error"),
                "passed": sampled and min_free >= gates.min_device_free_bytes,
            }
        )
    measured_rows = [row for row in headroom if "passed" in row]
    if profile == "cuda":
        # A CUDA run without device-memory samples cannot prove headroom.
        checks["cuda_memory_recorded"] = len(measured_rows) == len(headroom)
    if measured_rows:
        checks["device_headroom"] = all(row["passed"] for row in measured_rows)
    details["absolute"] = {
        "min_device_free_bytes": gates.min_device_free_bytes,
        "runs": headroom,
    }
    min_free_values = [
        row["min_free_bytes"] for row in measured_rows if _is_int(row["min_free_bytes"])
    ]
    summary = (
        f"min device free {min(min_free_values) / 2**30:.2f} GiB"
        if min_free_values
        else "no CUDA memory samples"
    )

    if not ctx.baselines:
        details["relative"] = {"status": NOT_APPLICABLE, "reason": "no --baseline given"}
        return _checked(checks, details, summary + "; relative n/a")

    problems = _candidate_pool_problems(ctx) + _baseline_pool_problems(ctx)
    checks["runs_paired"] = not problems
    baselines = _memory_docs(ctx.baselines)
    metrics: dict[str, Any] = {}
    for key in ("vmhwm_bytes", "final_rss_bytes"):
        candidate_values = [_num(_at(m, f"host.{key}", "memory"), key) for _, m in candidates]
        baseline_values = [
            _num(_at(m, f"host.{key}", "baseline memory"), key) for _, m in baselines
        ]
        # The probe reports 0 when /proc is unreadable; 0 <= 1.1 x 0 must not pass.
        checks[f"{key}_measured"] = all(v > 0 for v in candidate_values + baseline_values)
        metrics[key] = _relative(candidate_values, baseline_values, gates.memory_relative_max)
        checks[f"{key}_within_relative_max"] = metrics[key]["passed"]
    candidate_cuda = [m.get("cuda") for _, m in candidates]
    baseline_cuda = [m.get("cuda") for _, m in baselines]
    if all(isinstance(c, dict) for c in candidate_cuda + baseline_cuda):
        metrics["cuda_max_reserved_bytes"] = _relative(
            [_num(c.get("max_reserved_bytes"), "max_reserved_bytes") for c in candidate_cuda],
            [_num(c.get("max_reserved_bytes"), "max_reserved_bytes") for c in baseline_cuda],
            gates.memory_relative_max,
        )
        checks["cuda_max_reserved_within_relative_max"] = metrics[
            "cuda_max_reserved_bytes"
        ]["passed"]
    else:
        metrics["cuda_max_reserved_bytes"] = {
            "status": NOT_APPLICABLE,
            "reason": "CUDA memory not recorded for both candidate and baseline",
        }
    details["relative"] = {
        "relative_max": gates.memory_relative_max,
        "pairing_problems": problems,
        "metrics": metrics,
    }
    ratios = ", ".join(
        f"{key} x{_fmt(value.get('ratio'), 4)}"
        for key, value in metrics.items()
        if "ratio" in value
    )
    return _checked(checks, details, f"{summary}; {ratios}")


def _startup_values(rd: RunDir) -> list[float]:
    return _num_list(
        _at(rd.phase("startup"), "measured_seconds", "startup"),
        "startup.measured_seconds",
        allow_empty=True,
    )


def _synthetic_values(model: str) -> Callable[[RunDir], list[float]]:
    # The probe times warm-up calls separately, so these lists are measured-only.
    def extract(rd: RunDir) -> list[float]:
        return _num_list(
            _at(rd.phase("synthetic"), f"{model}.inference_seconds", "synthetic"),
            f"synthetic.{model}.inference_seconds",
            allow_empty=True,
        )

    return extract


def _combined_values(rd: RunDir) -> list[float]:
    runs = _combined_runs(rd.phase("combined"), "combined")
    return [run.seconds for run in runs if not run.warmup]


_PERF_METRICS: tuple[tuple[str, Callable[[RunDir], list[float]]], ...] = (
    ("startup_seconds", _startup_values),
    ("synthetic_yolo_inference_seconds", _synthetic_values("yolo")),
    ("synthetic_en_inference_seconds", _synthetic_values("efficientnet")),
    ("combined_run_seconds", _combined_values),
)


def _warmup_counts(rd: RunDir) -> dict[str, Any]:
    startup = _list(_at(rd.phase("startup"), "warmup_seconds", "startup"), "warmup_seconds")
    combined = _combined_runs(rd.phase("combined"), "combined")
    return {
        "run_id": rd.run_id,
        "startup_warmups": len(startup),
        "combined_warmups": sum(1 for run in combined if run.warmup),
    }


def gate_g9(ctx: Context) -> dict[str, Any]:
    """G9 performance: pooled medians against same-host baseline medians."""

    if not ctx.baselines:
        return _not_applicable("no --baseline given")
    gates = ctx.gates
    rerun_threshold = gates.measured_runs + gates.borderline_extra_runs
    candidate_problems = _candidate_pool_problems(ctx)
    baseline_problems = _baseline_pool_problems(ctx)
    warmups = [_warmup_counts(rd) for rd in [*ctx.candidates, *ctx.baselines]]
    checks = {
        "candidate_pool_consistent": not candidate_problems,
        "baseline_paired": not baseline_problems,
        "warmups_discarded": all(
            row["startup_warmups"] >= gates.warmup_discard
            and row["combined_warmups"] >= gates.warmup_discard
            for row in warmups
        ),
    }

    metrics: dict[str, Any] = {}
    for name, extract in _PERF_METRICS:
        candidate_values = [v for rd in ctx.candidates for v in extract(rd)]
        baseline_values = [v for rd in ctx.baselines for v in extract(rd)]
        if min(len(candidate_values), len(baseline_values)) < gates.measured_runs:
            metrics[name] = {
                "status": "insufficient_samples",
                "candidate_count": len(candidate_values),
                "baseline_count": len(baseline_values),
                "required": gates.measured_runs,
            }
            checks[f"{name}_within_relative_max"] = False
            continue
        metric = _relative(candidate_values, baseline_values, gates.perf_relative_max)
        ratio = metric["ratio"]
        borderline = (
            ratio is not None
            and abs(ratio - gates.perf_relative_max) <= gates.borderline_band
            and len(candidate_values) < rerun_threshold
        )
        if borderline:
            metric["status"] = "borderline_rerun_required"
        else:
            metric["status"] = "pass" if metric["passed"] else "regression"
        metrics[name] = metric
        checks[f"{name}_within_relative_max"] = metric["status"] == "pass"

    statuses = {metric["status"] for metric in metrics.values()}
    ratios = {name: metric.get("ratio") for name, metric in metrics.items()}
    details: dict[str, Any] = {
        "relative_max": gates.perf_relative_max,
        "borderline_band": gates.borderline_band,
        "measured_runs": gates.measured_runs,
        "rerun_pool_threshold": rerun_threshold,
        "warmup_discard": gates.warmup_discard,
        "ratios": ratios,
        "metrics": metrics,
        "warmups": warmups,
        "pairing_problems": candidate_problems + baseline_problems,
    }
    pool_valid = all(
        checks[name]
        for name in ("candidate_pool_consistent", "baseline_paired", "warmups_discarded")
    )
    result = _checked(
        checks,
        details,
        ", ".join(f"{name.split('_seconds')[0]} x{_fmt(r, 4)}" for name, r in ratios.items()),
    )
    if result["status"] == FAIL:
        # borderline_rerun_required is reported only when a pooled rerun could
        # still change the outcome, i.e. nothing else is wrong.
        if "regression" in statuses:
            reason = "regression"
        elif "insufficient_samples" in statuses:
            reason = "insufficient_samples"
        elif not pool_valid:
            reason = "invalid_pool"
        else:
            reason = "borderline_rerun_required"
        result["details"]["reason"] = reason
        result["summary"] = f"{reason}; {result['summary']}"
    return result


def _load_trivy(path: Path, role: str) -> tuple[dict[tuple[str, str], dict[str, Any]], Any]:
    """Map (VulnerabilityID, PkgName) to aggregated info for one Trivy report."""

    try:
        doc = _load_json(path)
    except (OSError, ValueError) as exc:
        raise Unavailable(f"{role} scan {path.name}", f"unparseable: {exc}") from None
    doc = _obj(doc, f"{role} scan")
    results = doc.get("Results") or []
    findings: dict[tuple[str, str], dict[str, Any]] = {}
    for r_index, result in enumerate(_list(results, f"{role} scan Results")):
        result = _obj(result, f"{role} scan Results[{r_index}]")
        vulnerabilities = result.get("Vulnerabilities") or []
        for v_index, vuln in enumerate(_list(vulnerabilities, f"{role} Vulnerabilities")):
            where = f"{role} scan Results[{r_index}].Vulnerabilities[{v_index}]"
            vuln = _obj(vuln, where)
            key = (
                _str(vuln.get("VulnerabilityID"), f"{where}.VulnerabilityID"),
                _str(vuln.get("PkgName"), f"{where}.PkgName"),
            )
            entry = findings.setdefault(
                key, {"severities": set(), "installed_versions": set(), "targets": set()}
            )
            entry["severities"].add(str(vuln.get("Severity", "")).upper())
            entry["installed_versions"].add(str(vuln.get("InstalledVersion", "")))
            entry["targets"].add(str(result.get("Target", "")))
    return findings, doc.get("ArtifactName")


def _load_dispositions(path: Path) -> dict[str, str]:
    try:
        doc = _load_json(path)
    except (OSError, ValueError) as exc:
        raise Unavailable(f"dispositions {path.name}", f"unparseable: {exc}") from None
    dispositions = _obj(doc, "scan dispositions")
    for vuln_id, reason in dispositions.items():
        if not isinstance(reason, str) or not reason.strip():
            raise ContentError(f"disposition for {vuln_id} must be a non-empty reason")
    return dispositions


def gate_g10(ctx: Context) -> dict[str, Any]:
    """G10 security: no new CRITICAL/HIGH findings without a disposition."""

    if ctx.scan_reference is None or ctx.scan_candidate is None:
        return _not_applicable("no scans given")
    reference, reference_artifact = _load_trivy(ctx.scan_reference, "reference")
    candidate, candidate_artifact = _load_trivy(ctx.scan_candidate, "candidate")
    dispositions = (
        _load_dispositions(ctx.scan_dispositions) if ctx.scan_dispositions else {}
    )

    def blocking(findings: dict[tuple[str, str], dict[str, Any]]) -> list[tuple[str, str]]:
        return sorted(k for k, v in findings.items() if v["severities"] & _BLOCKING_SEVERITIES)

    new_findings = []
    for key in blocking(candidate):
        if key in reference:
            continue
        info = candidate[key]
        new_findings.append(
            {
                "vulnerability_id": key[0],
                "pkg_name": key[1],
                "installed_versions": sorted(info["installed_versions"]),
                "severity": sorted(info["severities"] & _BLOCKING_SEVERITIES),
                "targets": sorted(info["targets"]),
                "disposition": dispositions.get(key[0]),
            }
        )
    undisposed = sorted({f["vulnerability_id"] for f in new_findings if not f["disposition"]})
    checks = {"new_critical_high_dispositioned": not undisposed}
    return _checked(
        checks,
        {
            "reference_artifact": reference_artifact,
            "candidate_artifact": candidate_artifact,
            "reference_critical_high": len(blocking(reference)),
            "candidate_critical_high": len(blocking(candidate)),
            "resolved_critical_high": len(
                [key for key in blocking(reference) if key not in candidate]
            ),
            "new_findings": new_findings,
            "undisposed": undisposed,
        },
        f"new CRITICAL/HIGH {len(new_findings)} ({len(undisposed)} without disposition)",
    )


def gate_g11(ctx: Context) -> dict[str, Any]:
    """G11 failure behavior: injected failure detected and follow-up clean."""

    inject = ctx.primary.phase("inject")
    probe_checks = _obj(_at(inject, "checks", "inject"), "inject.checks")
    checks = {name: probe_checks.get(name) is True for name in _INJECT_CHECKS}
    details = {key: value for key, value in inject.items() if key not in ("checks",)}
    return _checked(checks, {"inject": details}, "injected failure and follow-up checked")


def gate_g12(ctx: Context) -> dict[str, Any]:
    """G12 completeness: every required phase ran with exit 0 and ok=true."""

    required = ctx.gates.required_phases
    runs = []
    for rd in ctx.candidates:
        problems = []
        if rd.run is None:
            problems.append({"item": "run.json", "reason": rd.run_error})
        for phase in required:
            if rd.run is not None:
                entry = rd.value(f"phases.{phase}")
                if not isinstance(entry, dict):
                    problems.append({"item": phase, "reason": "not declared in run.json"})
                else:
                    exit_code = entry.get("exit_code")
                    if isinstance(exit_code, bool) or exit_code != 0:
                        problems.append(
                            {"item": phase, "reason": f"exit_code {exit_code!r}"}
                        )
            try:
                doc = rd.phase(phase)
            except Unavailable as exc:
                problems.append({"item": phase, "reason": f"{exc.item}: {exc.reason}"})
                continue
            if doc.get("ok") is not True:
                problems.append(
                    {"item": phase, "reason": "ok is not true", "error": doc.get("error")}
                )
        runs.append({"run_id": rd.run_id, "complete": not problems, "problems": problems})
    # Check names use the candidate position; run ids can be long or repeated.
    checks = {f"candidate_{index}_complete": run["complete"] for index, run in enumerate(runs)}
    missing = list(
        dict.fromkeys(
            f"{run['run_id']}:{problem['item']}" for run in runs for problem in run["problems"]
        )
    )
    compact = []
    for index, run in enumerate(runs):
        reasons: dict[str, list[str]] = {}
        for problem in run["problems"]:
            reasons.setdefault(problem["item"], []).append(str(problem["reason"]))
        prefix = f"#{index} " if len(runs) > 1 else ""
        compact += [f"{prefix}{item} ({'; '.join(r)})" for item, r in reasons.items()]
    return _checked(
        checks,
        {"required_phases": list(required), "runs": runs, "missing": missing},
        f"{len(required)} phases x {len(runs)} run(s)"
        + (f"; problems: {', '.join(compact)}" if compact else ""),
    )


GATES: tuple[tuple[str, Callable[[Context], dict[str, Any]]], ...] = (
    ("G1", gate_g1),
    ("G2", gate_g2),
    ("G3", gate_g3),
    ("G4", gate_g4),
    ("G5", gate_g5),
    ("G6", gate_g6),
    ("G7", gate_g7),
    ("G8", gate_g8),
    ("G9", gate_g9),
    ("G10", gate_g10),
    ("G11", gate_g11),
    ("G12", gate_g12),
)


def _run_gate(gate: Callable[[Context], dict[str, Any]], ctx: Context) -> dict[str, Any]:
    try:
        return gate(ctx)
    except Unavailable as exc:
        return {
            "status": MISSING,
            "summary": f"missing input: {exc.item} ({exc.reason})",
            "details": {"missing": exc.as_details()},
        }
    except ContentError as exc:
        return {
            "status": FAIL,
            "summary": f"malformed input: {exc}",
            "details": {"reason": "malformed_input", "error": str(exc)},
        }
    except Exception as exc:  # noqa: BLE001 - fail closed, keep evaluating other gates
        return {
            "status": FAIL,
            "summary": f"evaluation error: {type(exc).__name__}: {exc}",
            "details": {"reason": "evaluation_error", "error": repr(exc)},
        }


# ---------------------------------------------------------------------------
# Findings and verdict
# ---------------------------------------------------------------------------


def _context_findings(ctx: Context) -> None:
    """Record evidence-hygiene warnings that do not change any gate status."""

    gates = ctx.gates
    reference = ctx.reference
    declared = (gates.reference_stage, gates.reference_profile)
    observed = (reference.value("stage"), reference.value("profile"))
    if observed != declared:
        ctx.add_finding(
            "reference_not_declared",
            "warning",
            f"reference-outputs run {reference.run_id} is stage/profile {observed}; "
            f"gates declare {declared}.",
        )
    others = [("candidate", rd) for rd in ctx.candidates[1:]]
    others += [("reference-outputs", reference)]
    others += [("baseline", rd) for rd in ctx.baselines]
    if ctx.cpu_counterpart is not None:
        others.append(("cpu-counterpart", ctx.cpu_counterpart))
    for key in ("source.probe_sha256", "source.contract_sha256", "fixture_manifest_sha256"):
        anchor_value = ctx.primary.value(key)
        for role, rd in others:
            value = rd.value(key)
            if anchor_value is not None and value is not None and value != anchor_value:
                ctx.add_finding(
                    "source_mismatch",
                    "warning",
                    f"{key} differs between candidate {ctx.primary.run_id} and "
                    f"{role} {rd.run_id}.",
                    key=key,
                    candidate=anchor_value,
                    other=value,
                )


def _historical_vector_finding(ctx: Context) -> None:
    expected = list(ctx.gates.historical_count_vector)
    try:
        runs = _combined_runs(ctx.primary.phase("combined"), "combined")
        measured = [run for run in runs if not run.warmup]
        if not measured:
            raise ContentError("combined has no measured run")
        counts = [
            len(tile) for tile in _run_results(measured[-1], len(expected), "combined")
        ]
    except (Unavailable, ContentError) as exc:
        ctx.add_finding(
            "historical_count_vector",
            "info",
            f"historical count vector not evaluated: {exc}",
            matches=None,
            expected=expected,
        )
        return
    differing = [
        ctx.gates.tile_names[i] for i, (a, b) in enumerate(zip(expected, counts)) if a != b
    ]
    ctx.add_finding(
        "historical_count_vector",
        "info",
        "candidate per-tile counts "
        + ("equal" if not differing else "differ from")
        + " the historical rc7.1/v0.1.2 vector (informational, not a gate).",
        matches=not differing,
        expected=expected,
        observed=counts,
        differing_tiles=differing,
    )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate(ctx: Context) -> dict[str, Any]:
    """Run every gate and assemble the verdict document."""

    _context_findings(ctx)
    results = {gate_id: _run_gate(gate, ctx) for gate_id, gate in GATES}
    for gate_id, result in results.items():
        result["title"] = GATE_TITLES[gate_id]
    if ctx.check_historical_vector:
        _historical_vector_finding(ctx)
    overall = PASS if all(r["status"] in _ACCEPTED_STATUSES for r in results.values()) else FAIL
    primary = ctx.primary
    return {
        "schema_version": 1,
        "generated_utc": _utc_now(),
        "gates_file_sha256": ctx.gates.sha256,
        "reference_outputs": ctx.reference.run_id,
        "candidates": [rd.run_id for rd in ctx.candidates],
        "baselines": [rd.run_id for rd in ctx.baselines],
        "cpu_counterpart": ctx.cpu_counterpart.run_id if ctx.cpu_counterpart else None,
        "profile": primary.value("profile"),
        "stage": primary.value("stage"),
        "flavor": primary.value("flavor"),
        "host": primary.value("host"),
        "gates": {
            gate_id: {
                "status": r["status"],
                "title": r["title"],
                "summary": r["summary"],
                "details": r["details"],
            }
            for gate_id, r in results.items()
        },
        "findings": ctx.findings,
        "overall": overall,
    }


def _md_cell(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_markdown(verdict: dict[str, Any]) -> str:
    lines = [
        f"# TASK-103 comparator verdict: {verdict['overall'].upper()}",
        "",
        f"- Generated (UTC): {verdict['generated_utc']}",
        f"- Gates file SHA-256: `{verdict['gates_file_sha256']}`",
        f"- Stage / profile / flavor: {verdict['stage']} / {verdict['profile']} / "
        f"{verdict['flavor']} on host {verdict['host']}",
        f"- Candidates: {', '.join(verdict['candidates'])}",
        f"- Reference outputs: {verdict['reference_outputs']}",
        f"- Baselines: {', '.join(verdict['baselines']) or 'none'}",
        f"- CPU counterpart: {verdict['cpu_counterpart'] or 'none'}",
        "",
        "| Gate | Status | Key details |",
        "| --- | --- | --- |",
    ]
    for gate_id, result in verdict["gates"].items():
        lines.append(
            f"| {gate_id} {_md_cell(result['title'])} | {result['status']} | "
            f"{_md_cell(result['summary'])} |"
        )
    lines += ["", "## Findings", ""]
    if verdict["findings"]:
        lines += [
            f"- [{finding['severity']}] {finding['id']}: {_md_cell(finding['message'])}"
            for finding in verdict["findings"]
        ]
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path, verdict: dict[str, Any]) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "verdict.json").write_text(
            json.dumps(verdict, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
        (out_dir / "verdict.md").write_text(render_markdown(verdict), encoding="utf-8")
    except OSError as exc:
        raise UsageError(f"cannot write verdict to {out_dir}: {exc}") from exc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare TASK-103 probe run directories against declared gates."
    )
    parser.add_argument("--gates", required=True, type=Path)
    parser.add_argument("--reference-outputs", required=True, type=Path)
    parser.add_argument("--candidate", required=True, action="append", type=Path)
    parser.add_argument("--baseline", action="append", default=[], type=Path)
    parser.add_argument("--cpu-counterpart", type=Path)
    parser.add_argument("--scan-reference", type=Path)
    parser.add_argument("--scan-candidate", type=Path)
    parser.add_argument("--scan-dispositions", type=Path)
    parser.add_argument("--check-historical-vector", action="store_true")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.scan_reference is None) != (args.scan_candidate is None):
        parser.error("--scan-reference and --scan-candidate must be given together")
    if args.scan_dispositions is not None and args.scan_candidate is None:
        parser.error("--scan-dispositions requires --scan-reference and --scan-candidate")
    return args


def _run_dirs(paths: Sequence[Path], role: str) -> list[RunDir]:
    run_dirs = []
    for path in paths:
        if not path.is_dir():
            raise UsageError(f"{role} {path} is not a directory")
        run_dirs.append(RunDir(path))
    return run_dirs


def build_context(args: argparse.Namespace) -> Context:
    gates = load_gates(args.gates)
    candidates = _run_dirs(args.candidate, "--candidate")
    baselines = _run_dirs(args.baseline, "--baseline")
    pooled = [rd.path.resolve() for rd in [*candidates, *baselines]]
    if len(set(pooled)) != len(pooled):
        raise UsageError("a run directory is repeated across --candidate/--baseline")
    for path in (args.scan_reference, args.scan_candidate, args.scan_dispositions):
        if path is not None and not path.is_file():
            raise UsageError(f"{path} is not a file")
    counterpart = (
        _run_dirs([args.cpu_counterpart], "--cpu-counterpart")[0]
        if args.cpu_counterpart is not None
        else None
    )
    return Context(
        gates=gates,
        reference=_run_dirs([args.reference_outputs], "--reference-outputs")[0],
        candidates=candidates,
        baselines=baselines,
        cpu_counterpart=counterpart,
        scan_reference=args.scan_reference,
        scan_candidate=args.scan_candidate,
        scan_dispositions=args.scan_dispositions,
        check_historical_vector=args.check_historical_vector,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        verdict = evaluate(build_context(args))
        write_outputs(args.out, verdict)
    except UsageError as exc:
        print(f"task103_compare: error: {exc}", file=sys.stderr)
        return 2
    statuses = ", ".join(f"{gid}={g['status']}" for gid, g in verdict["gates"].items())
    print(f"task103_compare: overall {verdict['overall']} ({statuses})")
    return 0 if verdict["overall"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
