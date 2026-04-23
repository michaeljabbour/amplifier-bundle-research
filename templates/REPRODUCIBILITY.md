# Reproducibility: three files, one decision

This bundle ships three environment templates. They are not alternatives — they are **progressive layers**. Pick the lowest layer that fits your project today; add the others when the project grows.

| File | Layer | Use when | Effort |
|---|---|---|---|
| `requirements.in` + `requirements.txt` | 1 — pip lock | Pure-Python analysis; you can install on any OS with `pip` | 5 min |
| `environment.yml` + `conda-lock.yml` | 2 — conda lock | You need C extensions, system libs, or non-PyPI packages (torch+CUDA, GDAL, rdkit, pymc) | 15 min |
| `Dockerfile.research` | 3 — full image | You need LaTeX, pandoc, graphviz, or want reviewers to run without installing anything | 30 min |

**Recommendation:** *develop* with one layer, *ship* all three. A reviewer with `pip` alone gets Layer 1. A reviewer with `conda` gets Layer 2. An archivist ten years from now gets Layer 3.

## When each is appropriate

- **Solo patent attorney / policy analyst, Python stack only.** Layer 1. Copy `requirements.in`, run `uv pip compile requirements.in -o requirements.txt`, commit both. Done.
- **Working researcher, empirical paper with scikit-learn + matplotlib.** Layer 1 suffices unless you hit a C-extension issue. If so, move up to Layer 2.
- **ML paper with CUDA, or geospatial paper with GDAL.** Start at Layer 2. conda-forge wheels handle the ABI mess.
- **Paper going to archival review (NeurIPS reproducibility track, ACM artifact evaluation, journal replication package).** Layer 3. Ship the Dockerfile plus a built image digest.

## What goes in the paper's reproducibility appendix

Copy this block and fill it in:

```
Reproducibility.  All analyses were executed on <OS + CPU/GPU>.
Python <3.11.x>; package versions are pinned in `requirements.txt`
(sha256: <hash of requirements.txt>) / `conda-lock.yml` (sha256:
<hash>). A container image reproducing the full environment
including LaTeX is available at <registry>/<image>@sha256:<digest>.
Random seed: <42>. Raw data: <DOI or archive link>, sha256
<hash>. Code: <git URL>@<commit SHA>. Execution log: see
`execution-log.yaml` in the supplementary materials.
```

The hashes come directly from `execution-log.yaml → environment_capture → environment_file_digest` and `data_provenance[*].sha256`. Do not recompute them by hand; copy them from the log that `/execute` wrote.

## The recommended pattern

1. **`/plan`** commits `requirements.in` (intent) alongside `preregistration.yaml`.
2. **Before `/execute`**, generate the lockfile:
   ```bash
   uv pip compile requirements.in -o requirements.txt
   ```
   Commit `requirements.txt` too.
3. **`/execute`** records the sha256 of the lockfile, the Python interpreter path and version, and the key package versions actually imported, into `execution-log.yaml → environment_capture`.
4. **Before submission**, optionally build `Dockerfile.research`, pin the `FROM` line to a digest, push the image somewhere durable, and record the image digest in the execution log.

## What "pinned" means at each layer

- Layer 1 (`requirements.txt` after `pip-compile`): every package pinned to exact version + sha256 hash of the wheel. `pip install --require-hashes` refuses any drift.
- Layer 2 (`conda-lock.yml`): every package pinned to exact version + build string + URL, resolved per-platform. `conda-lock install` refuses any drift.
- Layer 3 (`Dockerfile.research` with `FROM python:3.11-slim@sha256:...`): the base OS layer is also pinned. The image digest produced by `docker build` is a hash over the whole filesystem.

Each layer widens the blast radius of reproducibility: Python packages → system libraries → the whole runtime.

## Anti-patterns to refuse

- Shipping `requirements.txt` with `numpy>=1.20` style ranges. That is not a lockfile; it is a wish.
- Committing `environment.yml` without `conda-lock.yml`. The YAML is intent, the lock is reproducibility.
- Using `FROM python:3.11-slim` (tag, not digest) in an archival image. Tags are mutable.
- Regenerating the lockfile the day the paper submits "to get the latest versions." That invalidates every sha256 recorded at `/execute`.
