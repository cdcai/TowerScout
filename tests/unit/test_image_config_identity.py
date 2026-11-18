"""Saved-image and pulled-image identity checks without Docker or extraction."""

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/image_config_identity.py"
SPEC = importlib.util.spec_from_file_location("image_identity", SCRIPT)
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)
CONFIG = {"architecture": "amd64", "os": "linux", "config": {"Env": []},
          "rootfs": {"type": "layers", "diff_ids": ["sha256:" + "a" * 64]}}


def _archive(entries):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w") as tar:
        for name, value in entries:
            member = tarfile.TarInfo(name)
            if value is None:
                member.type = tarfile.SYMTYPE
                member.linkname = "/untrusted"
                tar.addfile(member)
            else:
                member.size = len(value)
                tar.addfile(member, io.BytesIO(value))
    stream.seek(0)
    return stream


def _entries(style="oci", config=None):
    payload = json.dumps(config if config is not None else CONFIG).encode()
    digest = hashlib.sha256(payload).hexdigest()
    name = "blobs/sha256/" + digest if style == "oci" else digest + ".json"
    manifest = json.dumps([{"Config": name, "RepoTags": None, "Layers": []}]).encode()
    return [(name, payload), ("manifest.json", manifest)], "sha256:" + digest


@pytest.mark.parametrize("style", ["classic", "oci"])
@pytest.mark.parametrize("manifest_first", [False, True])
def test_real_config_bytes_are_hashed_in_either_archive_order(style, manifest_first):
    entries, expected = _entries(style)
    if manifest_first:
        entries.reverse()
    stream = _archive(entries)
    assert identity.saved_config_digest(stream) == expected
    assert stream.tell() == len(stream.getvalue()), "The Docker output stream must be drained"


@pytest.mark.parametrize("mutation", ["missing-manifest", "missing-config", "duplicate-manifest",
                                     "duplicate-config", "hash-mismatch", "multiple-images",
                                     "traversal", "symlink", "invalid-json"])
def test_ambiguous_or_unverified_archive_identity_is_rejected(mutation):
    entries, _ = _entries()
    name, payload = entries[0]
    if mutation == "missing-manifest":
        entries = entries[:1]
    elif mutation == "missing-config":
        entries = entries[1:]
    elif mutation == "duplicate-manifest":
        entries.append(entries[1])
    elif mutation == "duplicate-config":
        entries.append(entries[0])
    elif mutation == "hash-mismatch":
        entries[0] = (name, payload + b" ")
    elif mutation == "multiple-images":
        entries[1] = ("manifest.json", json.dumps([{"Config": name}] * 2).encode())
    elif mutation == "traversal":
        entries[1] = ("manifest.json", json.dumps([{"Config": "../" + name}]).encode())
    elif mutation == "symlink":
        entries[0] = (name, None)
    else:
        entries[1] = ("manifest.json", b"not JSON")
    with pytest.raises(ValueError):
        identity.saved_config_digest(_archive(entries))


@pytest.mark.parametrize("changes", [{"architecture": "arm64"}, {"os": "windows"},
                                      {"rootfs": {}}, {"config": None}])
def test_unexpected_image_configuration_is_rejected(changes):
    entries, _ = _entries(config={**CONFIG, **changes})
    with pytest.raises(ValueError, match="Linux amd64"):
        identity.saved_config_digest(_archive(entries))


@pytest.mark.parametrize("limit", ["MAX_CONFIG", "MAX_METADATA", "MAX_ARCHIVE", "MAX_MEMBERS"])
def test_archive_limits_fail_closed(monkeypatch, limit):
    entries, _ = _entries()
    monkeypatch.setattr(identity, limit, 1)
    with pytest.raises(ValueError):
        identity.saved_config_digest(_archive(entries))


@pytest.mark.parametrize("kind", ["classic", "containerd", "unrelated", "malformed"])
def test_pulled_image_must_match_the_verified_config_or_pinned_manifest(kind):
    config = "sha256:" + "1" * 64
    manifest = "sha256:" + "2" * 64
    local = {"classic": config, "containerd": manifest,
             "unrelated": "sha256:" + "3" * 64, "malformed": "sha256:invalid"}[kind]
    if kind in ("classic", "containerd"):
        identity.verify_pulled_identity(local, config, manifest)
    else:
        with pytest.raises(ValueError):
            identity.verify_pulled_identity(local, config, manifest)
