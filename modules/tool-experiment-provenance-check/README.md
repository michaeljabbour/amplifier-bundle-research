# tool-experiment-provenance-check

Reusable **pre-experiment data provenance checker** for reproducible research.
Fifth scientific-rigor tool in the Amplifier research bundle — sibling to
`tool-experiment-audit`, `tool-experiment-resume`, `tool-experiment-power`,
and `tool-experiment-stage-analyzer`.

## Purpose

When an experiment runs against data files that are never committed to git,
reproducibility is broken. This tool was created to detect that situation
automatically, motivated by the `hle_handcrafted.json` gap discovered in
commit `e189188` (reflection-tokens project, April 2026).

The tool:
1. Parses the experiment script's source code with AST to find all data file references.
2. Checks each discovered file against git (`git ls-files --error-unmatch`).
3. Classifies each as **TRACKED**, **UNTRACKED**, **MISSING**, or **IN_GITIGNORE**.
4. Emits a Markdown report highlighting integrity gaps and `git add` recommendations.

## Installation

```bash
pip install -e modules/tool-experiment-provenance-check/
```

## CLI

### `audit-script` — full pipeline → Markdown report

```bash
amplifier-research-provenance-check audit-script \
    --script experiments/sweep_exploratory.py \
    --repo /path/to/repo \
    --output reports/provenance.md
```

Parses the script → discovers all data paths → checks git tracking → writes report.
Exit code 0 always (report is the artifact, even if UNTRACKED files are found).

### `check-files` — lightweight direct check

```bash
amplifier-research-provenance-check check-files \
    --files data/inputs/test.jsonl data/persistent_blocks/foo.json \
    --repo /path/to/repo
```

Exit codes: **0** = all tracked, **1** = any untracked, **2** = any missing.

### `pre-experiment-gate` — hard gate for shell wrappers

```bash
amplifier-research-provenance-check pre-experiment-gate \
    --script experiments/sweep_exploratory.py \
    --repo /path/to/repo
```

Prints minimal summary, exits **1** if ANY untracked or missing file is found.
Designed for shell wrappers that launch experiments — refuses to launch with
untracked artifacts.

## Python API

```python
from amplifier_research_provenance_check.ast_walker import walk_script
from amplifier_research_provenance_check.git_check import check_files, FileStatus
from amplifier_research_provenance_check.report import generate_report

source = open("experiments/sweep_exploratory.py").read()
paths = walk_script(source)
results = check_files(paths, repo="/path/to/repo")

md = generate_report(results, script_path="sweep_exploratory.py")
print(md)
```

## Path detection strategies

The AST walker uses three complementary strategies:

| Strategy | Example | Detected as |
|---|---|---|
| String literal | `open("data/foo.json")` | `data/foo.json` |
| `Path(...)` constructor | `Path("data/foo.json")` | `data/foo.json` |
| `/`-chain | `Path("data") / "sub" / "f.json"` | `data/sub/f.json` |
| Variable-base chain | `_ROOT / "data" / "reserved" / "f.jsonl"` | `data/reserved/f.jsonl` |

The last strategy (variable-base chain) is what enables detecting patterns like:

```python
DATA_RESERVE_PATH = _PROJECT_ROOT / "data" / "reserved" / "composition_reserve.jsonl"
```

## File statuses

| Status | Meaning |
|---|---|
| `TRACKED` | File is committed to git — reproducible ✓ |
| `UNTRACKED` | File exists on disk but is NOT git-tracked — reproducibility gap! |
| `MISSING` | File path referenced in script but doesn't exist on disk |
| `IN_GITIGNORE` | File exists but is intentionally excluded from git |
| `OUTSIDE_REPO` | Absolute path resolves outside the repo root (not checkable) |

## Tests

```bash
pytest modules/tool-experiment-provenance-check/tests/ -v
# 19 tests, all passing
```

## Relationship to sibling tools

| Tool | Purpose |
|---|---|
| `experiment_audit` | Verify experiment data integrity before trusting results |
| `experiment_resume` | Repair aborted runs — plan / subset / merge |
| `experiment_power` | Pre-register sample sizes; compute MDE and post-hoc power |
| `experiment_stage_analyzer` | Root-cause analysis of empty-response failures by stage |
| `experiment_provenance_check` | **Verify all data files are git-tracked before running** |
