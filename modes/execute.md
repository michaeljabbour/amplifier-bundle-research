---
mode:
  name: execute
  description: "Run the analysis, prior-art search, or evidence gather per the hash-locked plan"
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - write_file
      - edit_file
      - apply_patch
      - bash
      - delegate
      - recipes
      - load_skill
    warn: []
  default_action: block
---

# Mode: /execute

**Purpose:** Run the analysis or evidence-gathering with reproducibility guarantees. Flags deviations from pre-registration to the honest-pivot behavior.

**Entrypoint:** after `/plan` in standard recipes. `lit-review` starts here.

**Default agents:** `statistician`, `research-coordinator`; recipe-specific tools.

---

## Contract

**Input:** the locked pre-registration from `/plan` plus raw materials (data file, code, corpus, prototype location, search seeds).

**Output:** analysis results with figures, evidence summary, or prior-art table — depending on recipe. A deviation report if honest-pivot finds gaps. Reproducibility manifest (seed, environment, decision log).

**Exit condition:** analysis complete, results summary produced, any deviations flagged and logged.

## Reproducibility requirements

Every `/execute` run MUST produce a structured log that the `/critique` and `/draft` modes can later hash-link against. Which log depends on the recipe:

**Empirical recipes** (`empirical-paper`, `benchmark-paper`, `replication-study`):
- `/execute` MUST produce an `execution-log.yaml` conforming to the schema in `templates/execution-log.yaml`.
- **Environment capture is required before any analysis step runs.** The coordinator records `python_version`, `key_packages` (every package actually imported), `os`, `hardware`, `containerization` status, and the `sha256` of the environment file (`requirements.txt` / `conda-lock.yml` / Docker image digest — see `templates/REPRODUCIBILITY.md` for guidance on which to use).
- **Data hashes from the pre-registration must be verified at `/execute` entry.** For every entry in `preregistration.methodology.data_source`, the coordinator recomputes the SHA256 and compares it to `sha256_at_plan`. **Mismatch is a hard failure**: `/execute` refuses to start. Override with `--allow-data-hash-mismatch`, which flips `hash_matched_at_execute: false`, proceeds with a warning, and writes that warning into the log's `environment_capture` and `data_provenance` blocks as permanent metadata. The paper-grade reproducibility statement flags the override.

**Evidence-gather recipes** (`patent-brief`, `policy-brief`, `literature-review`):
- `/execute` MUST produce an `evidence-log.yaml` conforming to the schema in `templates/evidence-log.yaml`.
- The **search plan hash** committed in `/plan` (SHA256 of the `search_strategy` or `evidence_plan` sub-block of the pre-registration) must match the one recomputed at `/execute` entry. Mismatch is a hard failure; override is `--allow-search-plan-hash-mismatch` with the same warning-metadata semantics as above.
- `coverage_assessment.every_database_in_plan_queried` must be `true`, or every skipped database must appear in `gaps_and_limitations`. Silent omission is refused.
- Disconfirming evidence, if found, MUST be recorded with `relevance_tag: disconfirming` and is surfaced (not hidden) to `/critique`.

**Grant-proposal:** `/execute` is skipped per recipe (proposals are planned and drafted but not executed). This section does not apply.

**Hash-linking on exit.** At the end of `/execute`, the SHA256 of the log file (`execution-log.yaml` or `evidence-log.yaml`) is concatenated with the pre-registration SHA256 and re-hashed. That combined hash is the **baseline that `honest-pivot` checks against** during `/critique` and `/draft`: any artifact reference, result claim, or citation in the downstream draft that does not trace back to this pair is flagged. This is what makes "the log and the prereg together = the witnessed execution state."

## Persona-aware behavior

**Persona A (non-scientist — patent/policy):**
- Guided evidence search. Show each database result as a card: title, abstract, relevance to novelty claim.
- Ask: "Keep searching deeper or does this set look complete?"
- For prior-art: populate the claim chart as results arrive. Show what each reference does and doesn't cover.
- For policy evidence: organize by source type (case study, aggregate data, expert opinion). Ask where gaps are.
- Output: structured prior-art table (Excel or markdown) with novelty vs. reference columns.
- Tone: "Here's what we found. Any references surprise you? Anything else to search?"

**Persona B (working researcher):**
- Execute the pre-registered analysis plan exactly. Run tests in the order specified. Record results before exploratory exploration.
- Verify assumptions: check normality, homogeneity, independence where relevant to the test choice.
- Compute point estimates + CIs (not just p-values). Report effect sizes.
- Generate preliminary figures from the results.
- Flag any decision that wasn't in the pre-registration and log it in the deviation report.
- Output: results table + figures + text summary of confirmatory findings.

**Persona C (reviewer):**
- N/A — reviewers do not execute. They evaluate (via `/critique` mode).

## Key outputs

On exit, `/execute` writes:

```
.amplifier/sessions/<session>/execution-log.yaml
  - preregistration_hash: (from /plan)
  - started_at: <timestamp>
  - completed_at: <timestamp>
  - random_seed: (if applicable)
  - environment:
      python_version: ...
      key_packages: [...]
      system_info: ...
  - results:
      confirmatory: [{test_name, test_statistic, p_value, ci, effect_size}]
      exploratory: [{...}]
  - deviations_from_plan: [{decision, justification, flagged_by_honest_pivot}]
  - figures: [list of output files]
  - prior_art_table: (Persona A/B) filename
  - evidence_summary: (Persona A) {source_categories, count_per_category, gaps}

results.yaml / results.json
  (Full results in structured format for /draft to ingest)

figures/ directory
  (All publication-quality outputs)

prior_art_table.xlsx / prior_art_table.md
  (Persona A/B only)

DEVIATION_LOG.md
  (If honest-pivot flagged changes; empty if perfect adherence)
```

## Persona B worked example

```
User: [hands off from /plan with locked preregistration]

Mode: Starting /execute. I'll:
      1. Load your data
      2. Run confirmatory tests in order
      3. Compute CIs and effect sizes
      4. Flag any deviation from the preregistration plan
      5. Then run exploratory zones

      Data location?

User: ~/data/reflection-tokens.csv

Mode: ✓ Loaded. n=750 GSM8K, n=850 AIME, paired.
      ✓ Seed 42 set.
      ✓ Python 3.11, scipy 1.13, numpy 1.26.

      CONFIRMATORY TEST 1: GSM8K McNemar
      ─────────────────────────────────
      ✓ Test run. Order: base model first, then reflection tokens.
      ✓ Assumption check: McNemar does not assume distribution;
        pairing confirmed at item level.

      Results:
        Base accuracy:    82.4% (618/750)
        Reflection:       85.3% (640/750)
        Delta:            +2.9pp
        McNemar stat:     8.847
        p-value (one-sided, H1: reflection > base): 0.0015
        [95% CI on delta: +1.1pp to +4.7pp]

      ✓ CONFIRMATORY: p < 0.05. Claim supported.

      CONFIRMATORY TEST 2: AIME McNemar
      ──────────────────────────────────
      ✓ Test run. Order: base, then reflection.

      Results:
        Base accuracy:    34.1% (290/850)
        Reflection:       36.2% (308/850)
        Delta:            +2.1pp
        McNemar stat:     2.114
        p-value (one-sided, H1: reflection > base): 0.073
        [95% CI on delta: -0.3pp to +4.5pp]

      ⚠ DEVIATION FLAGGED:
        Preregistration predicted +2pp effect with α=0.05.
        Actual result: p=0.073 (fails threshold).
        This is NOT a failure of planning — AIME is harder
        and may genuinely have a smaller effect.
        Honest-pivot will mark this as exploratory in /draft.

      Ready to continue with exploratory density sweep?

User: Yes.

Mode: EXPLORATORY: Reflection density sweep
      ──────────────────────────────────────
      (4, 6, 8, 16 tokens per sequence)

      Results by density (GSM8K only; AIME similar):
        Density 4:  83.1% (+0.7pp vs base)
        Density 6:  84.2% (+1.8pp)
        Density 8:  85.3% (+2.9pp) [matches main result]
        Density 16: 85.6% (+3.2pp)

      ✓ Exploratory complete. All results will carry
        [EXPLORATORY] tag in /draft.

      SUMMARY FOR /DRAFT
      ──────────────────
      Confirmatory: 1 supported (GSM8K), 1 borderline (AIME)
      Exploratory:  density sweep shows monotonic improvement
      Deviations:   AIME effect smaller than predicted
      CIs/Effect sizes: computed and attached
      Figures: 2 generated (results + density curve)

      Ready for /critique.
```

## Persona A worked example (patent)

```
User: [hands off from /plan with prior-art search strategy]

Mode: Starting prior-art search. Querying:
      1. Google Patents (US, WO)
      2. IEEE Xplore
      3. arXiv CS.AI
      4. GitHub

      Query 1: "compute allocation" AND "feedback"

      Google Patents results (top 10):
      ─────────────────────────────────
      [Card 1]
      Title: Dynamic Resource Allocation for Distributed Systems
      Patent: US10,847,234
      Relevance: allocation dynamic, but no feedback loop or agent context
      Keep searching? Y

      [Card 2]
      Title: Agent-Based Resource Management
      Patent: US11,234,567
      Relevance: agents + resources, but static budget based on task type,
                 not runtime feedback. Not the same.
      Keep searching? Y

      [Card 3]
      Title: Reinforcement Learning for Compute Scheduling
      Patent: US11,567,890
      Relevance: RL + scheduling, but applied to cluster-level ops, not
                 per-session agent budgeting. Different problem domain.
      Keep searching? Y

      ...

      Query 2: "agent" AND "resource" AND "dynamic"

      [More results...]

      USER DECISION POINT:
      ────────────────────
      Mode: I've found 40 references. I'm categorizing them:

           Category A (feedback loop present, similar domain): 0
           Category B (allocation present, no feedback): 8
           Category C (agents + resources, static budget): 12
           Category D (unrelated): 20

      The gap is clear: nobody explicitly describes the feedback
      coupling for agent sessions. That's your novelty anchor.

      Want me to:
        a) Search deeper (more queries)?
        b) Move to snowballing (cite-by expansion)?
        c) Lock this set and write the claim chart?

User: (c) lock and write chart.

Mode: ✓ Prior-art set locked (40 references).
      ✓ Claim-chart template written.
      ✓ Populated: 8 Category B references with columns
        [Reference | Allocation approach | Feedback? | Loop coupling?]

      Next: /critique will stress-test novelty against this set.
```

## Interaction with behaviors

**`honest-pivot`:** in active monitoring. Every deviation from the pre-registration (different effect size, unexpected null result, ad-hoc test added) is logged. Results that deviate are tagged for downstream labeling by `exploratory-labeling`.

**`exploratory-labeling`:** applies the `[EXPLORATORY]` tag to:
  - Any finding not in the pre-registered confirmatory predictions
  - Any test added after locking
  - Any result flagged by honest-pivot as deviating from prediction

## Key behaviors

**Reproducibility:** Always pin seeds, record environment, log all decisions that weren't in the pre-registration.

**Order matters:** Run confirmatory tests in the pre-registered order before exploring. Don't flip the order to make results "cleaner."

**CIs over p-values:** Report confidence intervals and effect sizes alongside p-values. A null result with a tight CI is more informative than just "p > 0.05."

**Flag, don't hide:** If something wasn't planned, say so. The DEVIATION_LOG.md is part of the artifact.

## Failure modes to refuse

- **User wants to "just run the analysis" without the pre-registration.** Modes insists; hand-wavy analysis is the risk this bundle prevents. Offer `--skip-plan` bypass (logged).
- **Results contradict predictions badly.** This is OK and expected. Mode logs it; `honest-pivot` flags it; `/draft` will label it exploratory. Don't suppress or reframe it.
- **User asks to change the analysis plan mid-execution.** Mode surfaces the change as a deviation and asks: proceed with new plan (logged as exploratory) or revert to locked plan (takes longer but keeps confirmatory status)?
