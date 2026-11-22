#!/usr/bin/env python3
"""Fetch the public base source for one curated code-correctness fixture."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

REPO = "https://github.com/fmtlib/fmt.git"
REVISION = "981b517ccf2d91bf3bf52c518ac43710b57b5e17"
FIXTURE = "fmt ordinary character-output alignment (base source only)"


def _git(repo, *args, capture_output=False):
    return subprocess.run(
        ("git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", "-c",
         "protocol.file.allow=never", *args), check=True, timeout=240,
        capture_output=capture_output, text=True,
    )


def _snapshot(repo, archive):
    _git(repo, "init", "--bare")
    _git(repo, "fetch", "--depth=1", "--no-tags", REPO, REVISION)
    got = _git(repo, "rev-parse", "FETCH_HEAD^{commit}", capture_output=True).stdout.strip()
    if got != REVISION:
        raise RuntimeError("Fetched commit does not match the pinned revision")
    _git(repo, "archive", "--format=tar", "-o", str(archive), REVISION)


def download(out):
    out = Path(out).absolute()
    if out.exists() or out.is_symlink():
        raise FileExistsError(out)
    with tempfile.TemporaryDirectory(prefix=".fmt-snapshot-", dir=out.parent) as path:
        work = Path(path)
        repo = work / "git"
        repo.mkdir()
        archive = work / "snapshot.tar"
        _snapshot(repo, archive)
        os.link(archive, out)  # atomic create; refuses overwrite even on a race
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path, help="write a source tar (destination must not exist)")
    group.add_argument("--show", action="store_true", help="show the pinned reference without downloading")
    args = parser.parse_args(argv)
    if args.show:
        print(f"{FIXTURE}\n{REPO}\n{REVISION}")
    else:
        print(download(args.out))


if __name__ == "__main__":
    main()
