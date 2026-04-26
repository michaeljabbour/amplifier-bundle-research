# Experiment Provenance Awareness

The research bundle includes `tool-experiment-provenance-check` — a first-class capability
for pre-experiment data provenance auditing. It ensures all data files referenced by an
experiment script are committed to git before the experiment runs.

## Why this tool exists

In April 2026, every A12a experiment in the reflection-tokens project used
`data/persistent_blocks/hle_handcrafted.json` for 4+ days before anyone noticed it had
never been committed to git (discovered in commit `e189188`). The gap was closed manually
(commit `545a295`), but this tool would have caught it automatically before the first run.

## When to use it

Use `experiment_provenance_check` / `amplifier-research-provenance-check` whenever you need to:

- **Audit a script** before running it to verify all input data files are git-tracked.
- **Block a launch** from a shell wrapper if any untracked artifact is found.
- **Spot-check specific files** you know you're using (lighter-weight than full audit).
- **Produce a Markdown report** documenting the provenance state of an experiment.

## The three subcommands

| Subcommand | Question answered | Inputs → Output | Exit codes |
|---|---|---|---|
| `audit-script` | Are all data files in this script tracked? | script + repo → **Markdown report** | 0 always |
| `check-files` | Are these specific files tracked? | file list + repo → **stdout + exit code** | 0=OK, 1=untracked, 2=missing |
| `pre-experiment-gate` | Can I launch this experiment safely? | script + repo → **gate verdict** | 0=pass, 1=fail |

---

## File statuses

| Status | Meaning | Action needed? |
|---|---|---|
| `TRACKED` | Committed to git — reproducible ✓ | None |
| `UNTRACKED` | Exists on disk but NOT in git | `git add` immediately |
| `MISSING` | Path referenced but file doesn't exist | Investigate broken reference |
| `IN_GITIGNORE` | Intentionally excluded from git | Review if this is correct |
| `OUTSIDE_REPO` | Absolute path outside repo root | Not checkable |

---

## How to invoke

### CLI — audit a script

```bash
amplifier-research-provenance-check audit-script \
    --script scripts/sweep_exploratory.py \
    --repo /path/to/repo \
    --output reports/provenance.md
```

### CLI — hard gate (for shell wrappers)

```bash
# In your experiment launcher:
amplifier-research-provenance-check pre-experiment-gate \
    --script scripts/sweep_exploratory.py \
    --repo /path/to/repo
# Exits 1 and refuses to continue if any untracked data file found
```

### CLI — direct file check

```bash
amplifier-research-provenance-check check-files \
    --files data/inputs/test.jsonl data/persistent_blocks/foo.json \
    --repo /path/to/repo
```

### Python API

```python
from amplifier_research_provenance_check.ast_walker import walk_script
from amplifier_research_provenance_check.git_check import check_files, FileStatus
from amplifier_research_provenance_check.report import generate_report

source = open("scripts/sweep_exploratory.py").read()
paths = walk_script(source)
results = check_files(paths, repo="/path/to/repo")

# Check for gaps
untracked = [p for p, s in results.items() if s == FileStatus.UNTRACKED]
if untracked:
    print(f"WARNING: {len(untracked)} untracked data file(s)!")

# Full report
md = generate_report(results, script_path="sweep_exploratory.py")
```

### Amplifier tool protocol

```
experiment_provenance_check(
    operation="audit_script",
    script_path="scripts/sweep_exploratory.py",
    repo_path="/path/to/repo",
    output_path="reports/provenance.md"
)
```

---

## Path detection

The AST walker detects paths via four strategies:

```python
# 1. String literal
open("data/foo.json")                         → data/foo.json

# 2. Path(...) constructor
Path("data/foo.json")                         → data/foo.json

# 3. Path / '...' / '...' chain
Path("data") / "sub" / "file.json"           → data/sub/file.json

# 4. Variable-base chain (handles _PROJECT_ROOT patterns)
_PROJECT_ROOT / "data" / "reserved" / "f.jsonl"  → data/reserved/f.jsonl
```

Watched prefixes: `data/`, `experiments/`, `configs/`, `inputs/`, `outputs/`, `results/`, `models/`, `checkpoints/`

---

## Relationship to sibling tools

| Tool | Purpose |
|---|---|
| `experiment_provenance_check` | **Verify data files are tracked BEFORE running** |
| `experiment_audit` | Verify experiment data integrity AFTER running |
| `experiment_resume` | Repair aborted runs — plan / subset / merge |
| `experiment_power` | Pre-register sample sizes; compute MDE and post-hoc power |
| `experiment_stage_analyzer` | Root-cause analysis of empty-response failures by stage |

**Recommended pre-experiment workflow**:
1. Run `experiment_provenance_check audit-script` — verify all data files are tracked.
2. Run `experiment_power required-n` — verify sample size is powered.
3. Run the experiment.
4. Run `experiment_audit` — verify integrity of results.

## Installing the tool

```bash
pip install -e modules/tool-experiment-provenance-check/
```
