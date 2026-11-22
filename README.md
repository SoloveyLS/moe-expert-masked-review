# MoE expert masking for code review

Research question: when a mixture-of-experts model reviews a proposed code change, do independent passes constrained to different expert subsets find more distinct, valid correctness issues than the same number of full-pool passes?

![Colored diagram of the expert masking review experiment](docs/expert-masking-preview.png)

[Editable Excalidraw diagram](docs/expert-masking-experiment.excalidraw)

## Components

- `vendor/strata` is a pinned Git submodule of the [Strata research branch](https://github.com/SoloveyLS/Strata/tree/2bd83ef6ca30cfaf9a19225c05fc86207cdaa4b8): opt-in routed-expert subsets and sparse expert loading, based on [upstream 87dfca0e](https://github.com/Niko1221/Strata/commit/87dfca0e7c3ee24ad36cc3f69a31b859587245f8). The upstream MIT notice remains in the fork.
- `download_benchmark.py`: downloads one fixed, public fmt source snapshot for an ordinary output-alignment benchmark fixture. It does not download patches, issue text, grading data or weights, and never extracts or runs the snapshot. It is a curated example, not the original multi-repository corpus.
- `test_downloader.py`: offline downloader argument, command and validation tests.

## Quick start

Requirements: Git, uv and Python 3.10+ already installed. The CPU demo also needs a C++17 compiler with pthread support (set `CXX` if needed). No third-party Python packages are required.

```sh
git clone --recurse-submodules https://github.com/SoloveyLS/moe-expert-masked-review.git
cd moe-expert-masked-review
uv run --frozen --offline python demo.py
uv run --frozen --offline python -m unittest -v
```

If you already cloned without submodules, run `git submodule update --init --recursive` first. The demo checks the committed Git submodule pin, rejects a modified submodule checkout, prints fixture provenance, and compiles and runs the fork's CPU expert-mapping regression in a temporary directory. It does not download the fixture, start Strata inference, or run model reviews.

To separately inspect or download the pinned example source:

```sh
uv run --frozen --offline python download_benchmark.py --show
uv run --frozen --offline python download_benchmark.py --out ./fmt-alignment-base.tar
```

The `--offline` flag prevents uv dependency network access; the explicit download command still uses Git to fetch only the fixed public fmt commit. The source stays under its upstream license. The downloader writes only to the selected path (which must not already exist), using a temporary directory for Git. It does not extract, build or execute the snapshot.

## Compare matched arms

Use user-owned code changes or reviewed benign fixtures, starting with an alignment/formatting behavior check. Freeze the proposed change before review, keep answer keys separate, and run the reviewers independently with identical prompts and comparable token budgets, sampling and review counts. Compare a full expert pool against one or more predeclared subset arms. Repeated full-pool reviews are the primary control; a single full-pool pass alone would not separate diversity from additional sampling.

Have a human adjudicate correctness findings against the specification and known behavior. Merge duplicate findings by root cause. Report unique valid findings, missed defects and false positives per arm, and record completion status, wall time and throughput independently. Keep author/grader inputs and raw review traces private; do not treat timeouts or absent outputs as clean reviews. Subset size is the eligible expert pool and does not itself reduce the number of routed experts per token.

## Validation and limitations

The fork's standalone CPU fixture checks identity mode, strict expert mapping, sparse reads, padding, short reads, concurrent reads and duplicate rejection. No end-to-end model run, GPU build or benchmark quality comparison is claimed for this release. The research branch is not an upstream-supported Strata feature. This repository contains methodology, a CPU regression demo and a minimal public snapshot downloader; it is not a batch reviewer or an automated vulnerability workflow.
