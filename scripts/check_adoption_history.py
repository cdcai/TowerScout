"""Reject excluded investigation data anywhere in the candidate's Git ancestry."""

import subprocess
import sys

EXCLUDED_BLOB = "12426b689e2ba62b721b397fa20e021ffdc59d85"
EXCLUDED_CREDENTIAL_BLOBS = {
    "30af83ca6e40f01c326fcac31ca785d98a4f126d",
    "d452a016d2560dea5bfce0ca0e339bbdaf6c7061",
}


def git(*args):
    return subprocess.check_output(["git", *args], text=True, encoding="utf-8")


def main():
    # A shallow checkout cannot prove that the historical file is absent.
    if git("rev-parse", "--is-shallow-repository").strip() != "false":
        raise ValueError("Full Git history is required for the adoption check")
    if git(
        "log",
        "--full-history",
        "--format=%H",
        "HEAD",
        "--",
        ":(top,icase,literal)contents.txt",
    ).strip():
        raise ValueError("Excluded root contents.txt is reachable in candidate history")
    # Object enumeration de-duplicates blobs and trees, so its recorded path
    # cannot prove a private path never existed (or was never copied/renamed).
    if git(
        "log", "--full-history", "--format=%H", "HEAD", "--",
        ":(top,icase,literal).agent_work",
    ).strip():
        raise ValueError("Private working archive is reachable in candidate history")
    # Also reject the known data blob if it returns under a different filename.
    excluded = {EXCLUDED_BLOB, *EXCLUDED_CREDENTIAL_BLOBS}
    for line in git("rev-list", "--objects", "HEAD").splitlines():
        blob, _, path = line.partition(' ')
        if blob in excluded:
            raise ValueError("Excluded investigation or credential blob is reachable")
        lowered = path.lower()
        if lowered.startswith('.agent_work/'):
            raise ValueError("Private working archive is reachable in candidate history")
        if lowered == 'contents.txt':
            raise ValueError("Excluded root contents.txt is reachable in candidate history")
    print("Candidate ancestry excludes the historical investigation file")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"Adoption history check failed: {exc}", file=sys.stderr)
        sys.exit(1)
