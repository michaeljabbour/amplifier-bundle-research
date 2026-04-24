# tool-experiment-resume

Experiment resume/repair capability for the Amplifier research bundle.  When a
sweep aborts mid-run (rate-limit cascade, provider overload, sanity-gate trip),
this tool helps identify which items have clean records, which need re-running,
and merges the preserved + new records into a unified result.

Run this **before discarding any partial results.jsonl**.

---

## Quick start

```bash
# Step 1: Categorise partial results → manifest
amplifier-research-resume plan \
    --partial-results experiments/production/a4_clean_dev/results.jsonl.partial \
    --full-input data/reserved/dev.jsonl \
    --approaches A0,A4 \
    --output-manifest experiments/production/a4_clean_dev/resume_manifest.json

# Step 2: Write items-to-rerun subset
amplifier-research-resume subset \
    --manifest experiments/production/a4_clean_dev/resume_manifest.json \
    --full-input data/reserved/dev.jsonl \
    --output-jsonl data/reserved/dev_resume.jsonl

# Step 3: Re-run the sweep against dev_resume.jsonl (manual step)

# Step 4: Merge preserved + new → unified
amplifier-research-resume merge \
    --manifest experiments/production/a4_clean_dev/resume_manifest.json \
    --partial-results experiments/production/a4_clean_dev/results.jsonl.partial \
    --new-results experiments/production/a4_clean_dev_resume/results.jsonl \
    --output-merged experiments/production/a4_clean_dev/results.merged.jsonl
```

---

## The resume contract

### `plan` — categorise records and produce a resume manifest

Rules for categorisation:

| Category | Condition |
|----------|-----------|
| `clean_complete` | ALL --approaches have records AND no record contains `[HANDLER_ERROR]` in `response` AND no response is suspiciously short (1–9 chars) |
| `errored` | ANY approach missing OR any response has `[HANDLER_ERROR]` OR any response is 1–9 chars long |
| `never_started` | Item ID appears in `--full-input` but has zero records in the partial file |

Note: empty string `""` responses (len=0) are treated as valid "no-answer" responses
where the judge ran and scored the item as incorrect — they are **not** flagged as errors.

### `subset` — emit items-to-rerun jsonl

Writes only items in `errored ∪ never_started`.  Preserves the original item
structure exactly (all fields pass through).

### `merge` — combine preserved + new records

1. Loads preserved records: only items in `clean_complete_items`
2. Loads new records from the resume run
3. Concatenates and deduplicates by `(item_id, approach_id)` — new run wins on collision
4. Writes unified jsonl
5. Returns a summary with counts and any gap warning

---

## Installation

```bash
# From the research bundle root:
pip install -e modules/tool-experiment-resume/

# Or from the module directory:
cd modules/tool-experiment-resume
pip install -e .
```

---

## Python API

```python
from pathlib import Path
from amplifier_research_resume import categorize_records, write_subset, merge_results

# Plan
manifest = categorize_records(
    partial_results=Path("experiments/foo/results.jsonl.partial"),
    full_input=Path("data/reserved/dev.jsonl"),
    approaches=["A0", "A4"],
)
manifest.save(Path("experiments/foo/resume_manifest.json"))
print(manifest.totals)  # {'clean_complete_count': 122, 'errored_count': 32, ...}

# Subset
n = write_subset(manifest=manifest, full_input=..., output_jsonl=...)
print(f"Items to rerun: {n}")

# Merge (after running the sweep)
from amplifier_research_resume import merge_results
summary = merge_results(
    manifest=manifest,
    partial_results=Path("experiments/foo/results.jsonl.partial"),
    new_results=Path("experiments/foo_resume/results.jsonl"),
    output_merged=Path("experiments/foo/results.merged.jsonl"),
)
print(summary.format_report())
```

---

## Module structure

```
modules/tool-experiment-resume/
├── src/amplifier_research_resume/
│   ├── __init__.py      # Public API
│   ├── manifest.py      # ResumeManifest dataclass + JSON serialisation
│   ├── plan.py          # categorize_records() — core categorisation logic
│   ├── subset.py        # write_subset() — emit items-to-rerun jsonl
│   ├── merge.py         # merge_results() + MergeSummary
│   ├── cli.py           # argparse CLI (plan / subset / merge subcommands)
│   └── mount.py         # Amplifier Tool protocol mount
├── tests/
│   ├── conftest.py
│   ├── test_plan.py         # 6 tests covering all categorisation rules
│   ├── test_subset.py       # 3 tests covering subset output
│   ├── test_merge.py        # 4 tests covering merge + dedup + gap detection
│   └── test_cli_integration.py  # 1 end-to-end pipeline test
├── pyproject.toml
└── README.md
```

---

## Running tests

```bash
cd modules/tool-experiment-resume
pip install -e .
python -m pytest tests/ -v
```

Expected: **14 tests, 0 failures**.

---

## Amplifier mount

The module registers an `experiment_resume` tool with the Amplifier coordinator:

```python
# In a session that loads this module:
result = experiment_resume(
    operation="plan",
    partial_results="experiments/foo/results.jsonl.partial",
    full_input="data/reserved/dev.jsonl",
    approaches="A0,A4",
    output_manifest="experiments/foo/resume_manifest.json",
)
# Returns: {"manifest_path": "...", "totals": {"clean_complete_count": 122, ...}}
```

---

## Smoke test result (2026-04-24)

Running `plan` against `amplifier-bundle-reflection` production experiment `a4_clean_dev`:

```
clean_complete: 122
errored:        32
never_started:  146
rerun_count:    178
expected_total: 300
```

Matches the manual analysis exactly.
