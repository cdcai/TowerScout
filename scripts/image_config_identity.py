"""Verify image configuration identity across classic and containerd stores.

The saved-image command reads a Docker archive stream without extracting files.
Export by immutable local image ID; retain manifest/config identities separately.
"""

import argparse
import hashlib
import json
import re
import sys
import tarfile


DIGEST = re.compile(r"sha256:[0-9a-f]{64}", re.ASCII)
CONFIG_PATH = re.compile(r"(?:blobs/sha256/([0-9a-f]{64})|([0-9a-f]{64})\.json)", re.ASCII)
MAX_CONFIG = 2 * 1024 * 1024
MAX_METADATA = 16 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024 * 1024
MAX_MEMBERS = 4096


class BoundedStream:
    def __init__(self, source):
        self.source = source
        self.total = 0

    def read(self, size):
        data = self.source.read(size)
        self.total += len(data)
        if self.total > MAX_ARCHIVE:
            raise ValueError("Saved image exceeds the archive limit")
        return data


def saved_config_digest(source):
    stream = BoundedStream(source)
    metadata = {}
    seen = set()
    total = 0
    with tarfile.open(fileobj=stream, mode="r|") as archive:
        for count, member in enumerate(archive, 1):
            if count > MAX_MEMBERS or member.size > MAX_ARCHIVE:
                raise ValueError("Saved image exceeds archive limits")
            name = member.name.removeprefix("./")
            if name != "manifest.json" and not CONFIG_PATH.fullmatch(name):
                continue
            if not member.isfile():
                raise ValueError("Image metadata must be a regular file")
            if name in seen:
                raise ValueError("Duplicate image metadata")
            seen.add(name)
            # Large blobs are layers, never the bounded configuration document.
            if member.size > MAX_CONFIG:
                if name == "manifest.json":
                    raise ValueError("Image manifest exceeds the metadata limit")
                continue
            total += member.size
            if total > MAX_METADATA:
                raise ValueError("Saved image exceeds the metadata limit")
            metadata[name] = archive.extractfile(member).read()
    # Consume the trailer so docker save does not receive a broken pipe.
    while stream.read(1024 * 1024):
        pass
    manifest = json.loads(metadata.get("manifest.json", b"null"))
    if not isinstance(manifest, list) or len(manifest) != 1 or not isinstance(manifest[0], dict):
        raise ValueError("Expected exactly one saved image manifest")
    path = manifest[0].get("Config", "")
    if not isinstance(path, str):
        raise ValueError("Invalid image config reference")
    path = path.removeprefix("./")
    match = CONFIG_PATH.fullmatch(path)
    if match is None or path not in metadata:
        raise ValueError("Image config is missing or exceeds its limit")
    payload = metadata[path]
    digest = hashlib.sha256(payload).hexdigest()
    if digest != (match.group(1) or match.group(2)):
        raise ValueError("Image config content does not match its digest")
    config = json.loads(payload)
    if (not isinstance(config, dict) or config.get("os") != "linux"
            or config.get("architecture") != "amd64" or not isinstance(config.get("config"), dict)
            or not isinstance(config.get("rootfs"), dict)
            or config["rootfs"].get("type") != "layers"
            or not isinstance(config["rootfs"].get("diff_ids"), list)
            or not all(isinstance(value, str) and DIGEST.fullmatch(value)
                       for value in config["rootfs"]["diff_ids"])):
        raise ValueError("Expected a Linux amd64 image configuration")
    return "sha256:" + digest


def verify_pulled_identity(image_id, config_digest, manifest_digest):
    if not all(isinstance(value, str) and DIGEST.fullmatch(value)
               for value in (image_id, config_digest, manifest_digest)):
        raise ValueError("Image identities must be full sha256 digests")
    if image_id not in (config_digest, manifest_digest):
        raise ValueError("Pulled image differs from the verified config and pinned manifest")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("saved-config")
    verify = sub.add_parser("verify-pulled")
    for name in ("image-id", "config-digest", "manifest-digest"):
        verify.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        if args.command == "saved-config":
            print(saved_config_digest(sys.stdin.buffer))
        else:
            verify_pulled_identity(args.image_id, args.config_digest, args.manifest_digest)
    except (ValueError, tarfile.TarError, OSError, EOFError) as error:
        print("Image identity error: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
