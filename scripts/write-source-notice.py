"""Write the container's source notice using the same ref as its OCI label."""

import argparse
from pathlib import Path
import re


SOURCE_REPOSITORY = "https://github.com/cdcai/TowerScout"


def source_notice(source_ref):
    if re.fullmatch(r"[0-9a-f]{40}", source_ref):
        location = (
            f"Source URL: {SOURCE_REPOSITORY}/tree/{source_ref}\n"
            f"Source download: {SOURCE_REPOSITORY}/archive/{source_ref}.tar.gz\n"
            "Release maintainers must verify public access to this exact source\n"
            "and its agreement with the image before publication.\n"
        )
    else:
        location = (
            "LOCAL VALIDATION ONLY: no immutable release source ref was supplied.\n"
            "This image must not be presented as a source-qualified release.\n"
        )
    return (
        "TowerScout Corresponding Source Notice\n\n"
        "Release track: agpl-yolo\n"
        f"Source repository: {SOURCE_REPOSITORY}\n"
        f"Build source ref: {source_ref!r}\n"
        f"{location}\n"
        "Corresponding source includes the TowerScout application, vendored\n"
        "YOLOv5 source and local patches, Dockerfile, Compose files, launcher,\n"
        "packaging and asset import scripts, dependency manifests, and build/run\n"
        "instructions for this exact version. Retain required dependency source\n"
        "and notices. Make the complete matching source available without charge\n"
        "alongside the release; a source URL or SBOM alone is not sufficient.\n\n"
        "See LICENSE, licenses/Apache-2.0.txt, licenses/AGPL-3.0.txt,\n"
        "licenses/CC-BY-NC-SA-4.0.txt, NOTICE,\n"
        "THIRD_PARTY_NOTICES.md, MODEL_LICENSES.md and DATA_LICENSES.md.\n"
        "The matching control ZIP records image digest and artifact checksums.\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(source_notice(args.source_ref), encoding="utf-8")


if __name__ == "__main__":
    main()
