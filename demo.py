#!/usr/bin/env python3
"""Verify the public fixture metadata and run the pinned Strata CPU regression."""
import os
from pathlib import Path
import subprocess
import tempfile

from download_benchmark import main as fixture_main

ROOT = Path(__file__).resolve().parent
STRATA = ROOT / "vendor" / "strata"
PIN = "2bd83ef6ca30cfaf9a19225c05fc86207cdaa4b8"


def git_at(path, *args):
    return subprocess.check_output(("git", "-C", str(path), *args), text=True).strip()


def main():
    parts = git_at(ROOT, "ls-tree", "HEAD", "vendor/strata").split()
    if parts[:3] != ["160000", "commit", PIN]:
        raise SystemExit("The Strata gitlink in HEAD does not match the release pin.")
    if not (STRATA / ".git").is_file() and not (STRATA / ".git").is_dir():
        raise SystemExit("Run git submodule update --init --recursive first.")
    if git_at(STRATA, "rev-parse", "HEAD") != PIN:
        raise SystemExit("Strata is not at the pinned revision; run git submodule update --init.")
    if git_at(STRATA, "status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("Strata has local changes; run the demo from a clean checkout.")
    fixture_main(["--show"])
    print(f"Verified Strata submodule: {PIN}", flush=True)
    with tempfile.TemporaryDirectory(prefix="strata-cpu-") as path:
        work = Path(path)
        exe = work / "review_subset_test"
        data = work / "fixture-data"
        data.mkdir()
        subprocess.run(
            (os.environ.get("CXX", "c++"), "-std=c++17", "-O2", "-pthread",
             "-Iinclude", "src/core/review_subset_test.cpp", "-o", str(exe)),
            cwd=STRATA, check=True, timeout=120,
        )
        subprocess.run((str(exe), str(data)), cwd=work, check=True, timeout=30)
    print("CPU demo passed. No model, GPU, fixture download, or reviewer was run.")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        raise SystemExit(f"Required executable not found: {exc.filename}") from exc
