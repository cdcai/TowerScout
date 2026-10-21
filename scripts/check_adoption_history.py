"""Reject excluded investigation data anywhere in the candidate's Git ancestry."""

import subprocess
import sys

EXCLUDED_BLOB = "12426b689e2ba62b721b397fa20e021ffdc59d85"


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
        ":(top,literal)contents.txt",
    ).strip():
        raise ValueError("Excluded root contents.txt is reachable in candidate history")
    # Also reject the known data blob if it returns under a different filename.
    if any(
        line.split(" ", 1)[0] == EXCLUDED_BLOB
        for line in git("rev-list", "--objects", "HEAD").splitlines()
    ):
        raise ValueError("Excluded investigation-data blob is reachable")
    print("Candidate ancestry excludes the historical investigation file")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f"Adoption history check failed: {exc}", file=sys.stderr)
        sys.exit(1)
