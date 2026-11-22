# MoE expert masking for code review

Research question: when a mixture-of-experts model reviews a proposed code change, do independent passes constrained to different expert subsets find more distinct, valid correctness issues than the same number of full-pool passes?

## Components

- [Strata research branch](https://github.com/SoloveyLS/Strata/tree/2bd83ef6ca30cfaf9a19225c05fc86207cdaa4b8): opt-in routed-expert subsets and sparse expert loading, based on [upstream 87dfca0e](https://github.com/Niko1221/Strata/commit/87dfca0e7c3ee24ad36cc3f69a31b859587245f8). The upstream MIT notice remains in the fork.
- `download_benchmark.py`: downloads one fixed, public fmt source snapshot for an ordinary output-alignment benchmark fixture. It does not download patches, issue text, grading data or weights, and never extracts or runs the snapshot. It is a curated example, not the original multi-repository corpus.
- `test_downloader.py`: offline downloader argument, command and validation tests.

```sh
python3 download_benchmark.py --show
python3 download_benchmark.py --out ./fmt-alignment-base.tar
python3 -m unittest test_downloader
```

The source stays under its upstream license. The script requires Git and Python 3.10+. It writes only to the chosen output path (which must not already exist); the local Git fetch occurs in a temporary directory. No models, build tools or services are installed by the downloader.

## Compare matched arms

Use user-owned code changes or reviewed benign fixtures, starting with an alignment/formatting behavior check. Freeze the proposed change before review, keep answer keys separate, and run the reviewers independently with identical prompts and comparable token budgets, sampling and review counts. Compare a full expert pool against one or more predeclared subset arms. Repeated full-pool reviews are the primary control; a single full-pool pass alone would not separate diversity from additional sampling.

Have a human adjudicate correctness findings against the specification and known behavior. Merge duplicate findings by root cause. Report unique valid findings, missed defects and false positives per arm, and record completion status, wall time and throughput independently. Keep author/grader inputs and raw review traces private; do not treat timeouts or absent outputs as clean reviews. Subset size is the eligible expert pool and does not itself reduce the number of routed experts per token.

## Validation and limitations

The fork's standalone CPU fixture checks identity mode, strict expert mapping, sparse reads, padding, short reads, concurrent reads and duplicate rejection. No end-to-end model run, GPU build or benchmark quality comparison is claimed for this release. The research branch is not an upstream-supported Strata feature. This repository contains methodology and a minimal public snapshot downloader; it is not a batch reviewer or an automated vulnerability workflow.
