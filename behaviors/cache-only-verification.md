---
bundle:
  name: research-cache-only-verification
  version: 0.1.0
  description: |
    Codifies the committee-audit pattern from PSE-PG14 v4f: every validation
    script that wraps an LLM call accepts a `--from-cache` flag that asserts
    the relevant cache file exists and exits cleanly without making any API
    call. This makes a paper's reproducibility bundle re-verifiable by a
    committee reviewer who does not have API credentials.
---

# Behavior: cache-only-verification

**Default:** opt-in (per-script via `--from-cache` flag, OR per-recipe via `cache_only: true`)
**Applies to:** all validation scripts and recipes that wrap an LLM call

---

## What it does

Every validation script in this bundle that calls an LLM (judge validation, cross-judge sensitivity, tertiary-judge audit, memory experiment, etc.) ships with a `--from-cache` flag. Behavior:

- `--from-cache` and the cache file exists → load from cache, run analysis, exit 0
- `--from-cache` and the cache file is missing → exit non-zero with a clear error message naming the missing path
- (no flag) and the cache file exists → load from cache, run analysis, exit 0 (idempotent)
- (no flag) and the cache file is missing → make API calls, write cache, run analysis, exit 0

The committee-audit path is therefore: extract bundle → run each validation script with `--from-cache` → all should exit 0. No API key required.

## Why this exists

PSE-PG14 v4f shipped a 3.6 MB reproducibility bundle that survived four rounds of peer review. One of the late-round reviewer findings was that validation scripts could not be re-run without API credentials, so a committee reviewer had to take the paper's numbers on faith for the LLM-mediated steps. The `--from-cache` mechanism closed that gap. Every cache-only run from the v4f bundle exits 0; the reviewer can verify all artifact-side numbers without spending a dollar.

## Implementation pattern

For any new validation script:

```python
import sys
FROM_CACHE = "--from-cache" in sys.argv

# ...

CACHE_FILE = Path("validation/judge_validation_raw.json")

if CACHE_FILE.exists():
    # Already cached; load and proceed (works in either mode)
    raw = json.load(CACHE_FILE.open())
else:
    # No cache; need to make API calls
    if FROM_CACHE:
        raise SystemExit(
            f"[--from-cache] required cache file missing: {CACHE_FILE}. "
            f"Re-run without --from-cache to generate it (requires API key)."
        )
    raw = run_api_calls()
    CACHE_FILE.write_text(json.dumps(raw))
```

## Recipe-level integration

For recipes that orchestrate multiple validation steps, add `cache_only` to the recipe context:

```yaml
context:
  cache_only: false        # default: live API calls if cache absent

stages:
  - name: judge-validation
    steps:
      - id: run-judge-validation
        type: shell
        command: |
          {% if cache_only %}python3 run_judge_validation.py --from-cache
          {% else %}python3 run_judge_validation.py{% endif %}
```

## What this guarantees

- **Acceptance bar:** `extract → cd → make distclean && make → pytest → all 4 validation scripts --from-cache → all exit 0` is the contract a committee reviewer can run without any account on any LLM provider.
- **Bit-identical paper rebuild:** the cache-only mode is consistent with the bundle's `make distclean && make` rebuild path; the same cache files feed both.
- **Honest residuals:** a cache file that's missing is named explicitly in the error message; the reviewer knows exactly which file the original author would need to regenerate.

## What this does NOT guarantee

- Live behavioral reproducibility. The cache is a frozen snapshot; if the underlying model has been retrained or the API has changed, re-running without the flag may produce different numbers. That is a separate kind of reproducibility (see v3 paper §"Reproducibility, decomposed" — three tiers: artifact, evaluation replay, live behavioral).
- Forward compatibility. A cache file from v4f may not be parseable by v0.9 of the harness if schema changes. The cache file format is versioned; mismatch produces an error, not a silent wrong answer.
