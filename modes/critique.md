---
mode:
  name: critique
  description: "Apply structured critique (CONSORT/STROBE/PRISMA) to a draft or incoming document"
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - delegate
      - recipes
      - load_skill
    warn:
      - bash
  default_action: block
---

# Mode: /critique

**Purpose:** Argue against your own work (or someone else's) before anyone else does. Produces a structured critique with severity levels and actionable feedback.

**Entrypoint:** after `/execute` in standard recipes (for Persona A/B). PRIMARY ENTRY POINT for Persona C (standalone evaluation mode).

**Default agents:** `honest-critic`, `methodologist`, `statistician`

---

## Contract

**Input:** either (a) results from `/execute` + pre-registration, or (b) an incoming document (draft, whitepaper, protocol) for Persona C evaluation.

**Output:** a structured `critique.yaml` artifact with severity levels (BLOCK/WARN/NOTE) plus scholar-eval quantitative scores. BLOCK items must be resolved before `/draft`.

**Exit condition:** user acknowledges critique, decides to fix BLOCKs or accept risks, and hands off to `/draft` (or publication).

## Persona-aware behavior

**Persona A (non-scientist — patent/policy):**
- Critique organized as: (1) novelty stress test, (2) enablement stress test, (3) overclaim flags, (4) evidence gaps.
- Severity BLOCK = "an examiner/competitor/skeptic would reject this on this specific point."
- Severity WARN = "fixable before submission, but you should know about it."
- Severity NOTE = "doesn't block submission, but makes the argument stronger if addressed."
- Language: plain English, no jargon. Point to the specific sentence in the draft. Suggest the fix, not just the problem.
- Example: "Line 47 says 'substantially reduces,' but you have n=1 prototype. WARN: soften to 'reduces in prototype demonstration' or drop the quantifier."

**Persona B (working researcher):**
- Critique via CONSORT/STROBE/PRISMA checklists (recipe-appropriate).
- Point to specific methodology gaps, stat violations, or overclaims.
- Compute missing power analysis if applicable. Flag multiple-comparison corrections if absent.
- Severity BLOCK = "this violates a core methodological assumption and must be fixed."
- Severity WARN = "this weakens the claim and should be addressed before publication."
- Severity NOTE = "this is good practice but not required for this venue."
- Scholar-eval scores (methodology, evidence, clarity, novelty) with textual commentary.
- Example: "Your McNemar test assumes pairing at the item level, not batch level. I see pairing at item level in your code. OK. But your power analysis footnote says 'batch-level pairs — confirm this was not your actual implementation.'"

**Persona C (reviewer — standalone evaluation):**
- PRIMARY MODE. Extracts load-bearing claims from the document.
- Evaluates each claim against the evidence in the document itself.
- Does NOT assume pre-registration; instead, evaluates against what the document claims its methodology was.
- Severity BLOCK = "this claim is unsupported by the evidence in the document; recommend rejection or major revision."
- Severity WARN = "this claim is weakly supported; request additional evidence or soften language."
- Severity NOTE = "this claim is supported but would be stronger if..."
- Scholar-eval scores + summary verdict (e.g., "WEAK," "SPECULATIVE," "SOLID").
- Generates a standalone critique report ready for the original author or for a review board.

## Key outputs

On exit, `/critique` writes:

```
.amplifier/sessions/<session>/critique.yaml
  - preregistration_hash: (if exists; Persona A/B)
  - document_identifier: (if Persona C)
  - evaluation_date: <timestamp>
  - persona: [A|B|C]
  - claims_identified: [{claim_text, evidence_cited, severity, resolution}]
  - severity_breakdown: {BLOCK: N, WARN: N, NOTE: N}
  - scholar_eval:
      methodology: {score: X/5, commentary: ...}
      evidence:    {score: X/5, commentary: ...}
      clarity:     {score: X/5, commentary: ...}
      novelty:     {score: X/5, commentary: ...}
  - checklists: (CONSORT/STROBE/PRISMA if applicable)
      {item: "randomization", status: "OK|MISSING|UNCLEAR", note: ...}
  - resolutions:
      BLOCK: [{item, suggested_fix, effort: "low|medium|high"}]
      WARN:  [{item, suggested_fix, effort: ...}]
      NOTE:  [{item, suggested_fix, effort: ...}]

critique-summary.md
  (Human-readable version for sharing)
```

## Persona B worked example

```
User: [hands off from /execute with results]

Mode: Running /critique against your preregistration and results.

      ✓ Assumption check (McNemar test)
        - Requires dichotomous outcome: ✓ (correct/incorrect)
        - Requires paired data: ✓ (same 750 items, both models)
        - No distributional assumptions: ✓
        OK

      ✓ Multiple comparisons
        - You registered 2 confirmatory tests (GSM8K, AIME)
        - You ran 2 tests (GSM8K, AIME)
        - No correction needed for 2 tests at α=0.05
        OK

      ✓ Pre-registered exploratory zone
        - Density sweep flagged in preregistration: ✓
        - Reported under [EXPLORATORY] tag: ✓
        OK

      ⚠ WARN: Effect size reporting
        You report McNemar p-values and CIs on deltas. Good.
        But you don't report an effect size measure (e.g., odds
        ratio from McNemar contingency table). Add to Results
        section for completeness.

      ⚠ WARN: AIME result (p=0.073)
        Preregistration predicted +2pp at α=0.05. Actual result
        is p=0.073, falling outside threshold. This is NOT a
        failure of your study — AIME is harder, effect may be
        smaller. But it is a deviation from prediction. Make sure
        /draft labels this clearly: "Consistent with but not
        meeting preregistered threshold; treat as exploratory."

      ✓ Scholar-eval scores
        Methodology:  4.5/5 (clear, preregistered, appropriate tests)
        Evidence:     4.2/5 (good CIs, but AIME borderline)
        Clarity:      4.7/5 (results clearly reported)
        Novelty:      3.1/5 (not applicable for this replication
                             but scores well on reproducibility)

      RESOLUTION CHECKLIST
      ────────────────────
      [NOTE] Add McNemar effect-size (odds ratio) to Results.
             Effort: 5 min. Suggested: report in results table.

      [WARN] Clarify AIME result language in /draft.
             Effort: 10 min. Suggested text: "The AIME effect
             (p=0.073) did not meet the preregistered threshold
             (α=0.05) and is reported as exploratory."

      Ready to move to /draft, or adjust anything?

User: Make those two changes in my code, then re-run /critique?

Mode: [code updated, re-run]

      ✓ McNemar effect size (odds ratio) computed and inserted.
        OR (95% CI): 1.34 [1.07, 1.68]

      ✓ AIME result language clarified.

      Updated scholar-eval:
        Methodology:  4.5/5 (unchanged)
        Evidence:     4.6/5 (improved with odds ratios)
        Clarity:      4.9/5 (improved with AIME language)
        Novelty:      3.1/5 (unchanged)

      All items resolved. Ready for /draft.
```

## Persona A worked example (patent)

```
User: [hands off from /execute with draft brief + prior-art table]

Mode: Running /critique against novelty and enablement claims.

      NOVELTY STRESS TEST
      ───────────────────
      Your claim: "A system coupling real-time value estimation
                   to per-step compute allocation via a closed-loop
                   feedback mechanism."

      Prior-art set (40 references):
        - 8 have allocation mechanisms
        - 0 have feedback coupling + per-session agent context
        - 12 have agents + resource mgmt (but static budgets)

      Combining Claims:
        Claim: Feedback loop is non-obvious given prior art?
        Evidence: No prior reference combines value estimation +
                  allocation feedback at the agent-session level.
        Verdict: ✓ NOVEL. Examiner might cite combinations, but
                 each piece alone is pre-existing.

      ✓ NOVELTY CLAIM STANDS

      ENABLEMENT STRESS TEST
      ──────────────────────
      Your draft says: "The value estimator scores task progress
                       against declared goals."

      Test: Can a PHOSITA (person having ordinary skill in the art
            — here, an ML engineer) read this and reproduce it?

      Issues found:
        ⚠ BLOCK: The phrase "scores task progress" is vague.
                 Does it use ground truth outcomes? Intermediate
                 signals? How is "progress" quantified?
                 
                 Suggested fix: "The value estimator compares the
                 agent's stated goal (input) against observed
                 intermediate task completion (measured by [specific
                 metric]), returning a score in range [0,1] at each
                 step." Show the scoring function or pseudo-code.

      ⚠ WARN: You mention the prototype uses a specific value
               estimator architecture (you showed me the code), but
               the brief doesn't specify it. Will an examiner ask
               for more detail?
               
               Suggested fix: Add 1-2 sentence pseudo-code block in
               the Detailed Description section.

      OVERCLAIM STRESS TEST
      ─────────────────────
      Your draft: "substantially reduces token expenditure"

      Evidence: n=1 prototype, not validated on diverse tasks

      Severity: ⚠ WARN

      Suggested fix: Soften language. "The prototype demonstrates
                     reduced token expenditure compared to baseline
                     on [specific task distribution]" removes the
                     "substantially" and scope to your demo.

      SCHOLAR-EVAL SCORES
      ───────────────────
      Novelty:       4.3/5 (claim is clear and novel vs. prior art)
      Clarity:       3.1/5 ← needs work on enablement section
      Enablement:    2.9/5 ← fix BLOCK item
      Evidence:      3.6/5 (prototype good, generalization unclear)

      RESOLUTION CHECKLIST
      ────────────────────
      [BLOCK] Specify the value estimator scoring function.
              Effort: medium. Suggested: add pseudocode block.

      [WARN]  Add prototype architecture detail.
              Effort: low. Suggested: reference code snippet.

      [WARN]  Soften "substantially reduces" claim.
              Effort: low. Suggested: replace with proto-scoped claim.

      Fix BLOCK and WARN items before /draft, or accept the risks?

User: I'll fix the value estimator detail now.

Mode: [doc updated, re-run]

      ✓ Value estimator function now specified with pseudocode.
        A PHOSITA can now understand how to build it.

      Updated scores:
        Novelty:       4.3/5 (unchanged)
        Clarity:       4.0/5 (improved)
        Enablement:    4.1/5 (BLOCK resolved)
        Evidence:      3.6/5 (unchanged)

      Remaining items (WARN): reference architecture detail,
      soften "substantially." Ready to proceed to /draft with
      these notes attached, or make those changes too?

User: I'll fix them in /draft.

Mode: OK. Carrying the WARN items into /draft as reminders.
      When you're ready for /draft, they'll be in the sidepanel.
```

## Persona C worked example (standalone)

```
User: amplifier run --mode critique --input incoming-whitepaper.pdf

Mode: Extracting load-bearing claims from the document...

      ✓ Identified 6 main claims:
        1. "Our model outperforms GPT-5 on reasoning tasks."
        2. "Achieves 40% cost reduction in customer deployments."
        3. "Training method is novel vs. prior RL approaches."
        4. "Generalizes to unseen task families."
        5. "Interpretability is improved vs. baseline."
        6. "No safety regression observed."

      CLAIM 1: Model outperforms GPT-5
      ──────────────────────────────────
      Evidence cited: Table B.1, benchmark scores on 4 benchmarks

      Evaluation:
        ✓ Evidence is quantitative (scores reported)
        ⚠ Sample size: n=50 per benchmark (small)
        ⚠ Baseline: GPT-5 "base" — not GPT-5 with reasoning mode
        ⚠ No confidence intervals reported
        ⚠ No multiple-comparison correction for 4 benchmarks

      Severity: ⚠ WEAK

      Verdict: The claim as stated ("outperforms on reasoning") is
               not fully supported. A narrower claim would be: "scores
               higher than GPT-5 base on these 4 benchmarks" — but even
               that needs CIs and baseline clarification.

      Suggested follow-up: Request CIs, compare to GPT-5 reasoning mode,
                          or accept n=50 as preliminary.

      CLAIM 2: 40% cost reduction in deployments
      ──────────────────────────────────────────
      Evidence cited: Case study, Appendix C (1 customer)

      Evaluation:
        ⚠ Sample: 1 customer (not generalizable)
        ⚠ No control: no comparison to other cost-reduction
          methods (e.g., batching, distillation)
        ⚠ Survivorship bias: customer is still deployed
          (presumably successful; unsuccessful deployments missing?)
        ⚠ No cost breakdown (which model? which region?)

      Severity: ⚠ SPECULATIVE

      Verdict: This is anecdotal evidence, not a claim. Reframe as
               "A single customer achieved 40% cost reduction in a
               case study" or request additional customer evidence.

      Suggested follow-up: Request 3+ customer case studies with
                          cost accounting, or 1 controlled experiment.

      [Claims 3–6: similar analysis...]

      SCHOLAR-EVAL AGGREGATE
      ─────────────────────
      Methodology:    2.1/5  (no control group, no power analysis,
                              no preregistration)
      Evidence:       2.4/5  (small n, 1 case study, no CIs)
      Clarity:        4.0/5  (well-written, easy to understand)
      Novelty:        3.3/5  (RL+reasoning is known, method
                              contribution unclear)

      RECOMMENDATION
      ──────────────
      Major revision required. Recommend:
        - Request raw benchmark data with CIs
        - Request 3+ customer cost studies or 1 RCT
        - Clarify baseline (GPT-5 reasoning mode, not base)
        - Compute multiple-comparison corrections for 4 benchmarks
        - Reframe cost-reduction claim as preliminary

      Written to: ./output/whitepaper-critique.md
```

## Interaction with behaviors

**`honest-pivot`:** critique explicitly surfaces deviations from pre-registration (Persona B). Any result flagged by honest-pivot as exploratory is called out here as a deviation, not a failure.

**`exploratory-labeling`:** builds the tag list for `/draft`. Items that should be labeled `[EXPLORATORY]` are identified here.

## Failure modes to refuse

- **User wants to skip `/critique` and go straight to `/draft`.** Mode offers a quick "OK to publish?" sanity check, but recommends the full critique. Bypass available with `--skip-critique` (logged).
- **Persona C critique reveals zero supporting evidence for a claim.** Mode flags this clearly: "This claim has no evidentiary support in the document. Recommend: remove the claim, reframe as speculation, or add evidence."
- **BLOCK items are ignored.** Mode warns: "You have 3 BLOCK items preventing /draft. Fix them or acknowledge the risk and move forward anyway (logged)."
