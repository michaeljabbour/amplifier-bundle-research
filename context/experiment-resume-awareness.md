# Experiment Resume Awareness

The research bundle includes `tool-experiment-resume` — a first-class capability for
resuming or repairing aborted experiment runs.

## When to use it

Use `experiment_resume` / `amplifier-research-resume` whenever:

- A sweep run (`sweep_exploratory.py` or similar) aborts before completing all items.
- A `results.jsonl.partial` exists with valuable completed records you want to preserve.
- You need to identify exactly which items succeeded and which need re-running.
- You want to merge a resumed run's results with the preserved records into a single clean file.

**Do NOT discard a partial results file without first running `plan`** — even a heavily-aborted
run may contain 40–60% clean records worth preserving.

## The three-step workflow

### Step 1 — `plan`: categorise what you have

```bash
amplifier-research-resume plan \
    --partial-results experiments/foo/results.jsonl.partial \
    --full-input data/reserved/dev.jsonl \
    --approaches A0,A4 \
    --output-manifest experiments/foo/resume_manifest.json
```

Produces `resume_manifest.json` with:
- `clean_complete_items`: item IDs with all approaches clean → **preserve these**
- `errored_items`: item IDs with [HANDLER_ERROR] or missing approaches → **re-run these**
- `never_started_items`: item IDs not in partial at all → **re-run these**
- `totals`: counts of all categories and expected total

### Step 2 — `subset`: prepare the re-run input

```bash
amplifier-research-resume subset \
    --manifest experiments/foo/resume_manifest.json \
    --full-input data/reserved/dev.jsonl \
    --output-jsonl data/reserved/dev_resume.jsonl
```

Writes only the items in `errored ∪ never_started` — ready to pass directly to the sweep.

### Step 3 — `merge`: unify results after the resume run

```bash
amplifier-research-resume merge \
    --manifest experiments/foo/resume_manifest.json \
    --partial-results experiments/foo/results.jsonl.partial \
    --new-results experiments/foo_resume/results.jsonl \
    --output-merged experiments/foo/results.merged.jsonl
```

Combines preserved clean records + new run records, deduplicates, and flags any remaining gaps.

## Categorisation rules

| Category | Condition |
|----------|-----------|
| `clean_complete` | ALL `--approaches` have records **AND** no record contains `[HANDLER_ERROR]` in `response` **AND** no response is 1–9 chars long |
| `errored` | Any approach missing **OR** any `[HANDLER_ERROR]` in response **OR** any 1–9 char response |
| `never_started` | Item ID in `--full-input` but no records in partial |

**Note on empty responses**: Records with `response: ""` (empty string, len=0) and a valid
`correct_by_judge` field are treated as **clean** — the model ran but returned nothing, the
judge evaluated and scored it False. These do not need re-running.

## When the merge surfaces a gap

If the resume run also had errors, `merge` exits with code 1 and prints:

```
Missing items (4): ['item_A', 'item_B', 'item_C', 'item_D']
```

Run `plan` again on the latest merged results to prepare a second round of re-runs, or
investigate the specific items with `amplifier-research-audit`.

## Tool protocol usage

The `experiment_resume` tool accepts an `operation` field (`plan` / `subset` / `merge`)
along with the relevant paths.  Invoke it from within a session to integrate resume logic
into a larger orchestration workflow.

## Relationship to `tool-experiment-audit`

| Tool | Purpose |
|------|---------|
| `experiment_audit` | Detect integrity problems in a completed or partial results file |
| `experiment_resume` | Fix the problems by producing a repair manifest, subset, and merged result |

**Typical sequence**: run `audit` to detect → run `resume plan` to categorise → `subset` to
prepare → re-run sweep → `merge` to unify → run `audit` again to verify the merged result passes.
