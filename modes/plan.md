---
mode:
  name: study-plan
  description: "Design research methodology and hash-lock the pre-registration before any data is seen (/study-plan — not to be confused with modes-bundle's general /plan)"
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
      - delegate
      - recipes
      - load_skill
    warn:
      - bash
  default_action: block
---

# Mode: /study-plan

**Purpose:** Lock the methodology before seeing results. Produces a hash-sealed pre-registration artifact that becomes the baseline for honest-pivot behavior and exploratory-labeling classification.

> **Note on slash command name:** this mode is `/study-plan` (not `/plan`) to avoid a collision with the generic `/plan` mode shipped by `amplifier-bundle-modes`. Conceptually it's still "the plan mode" in the pipeline — prose elsewhere in this bundle uses both forms. Users should type `/study-plan` to activate it; the research-coordinator agent routes natural-language requests to this mode regardless of which phrase the user uses.

**Entrypoint:** recipes except `lit-review` (which skips to `/execute`) and `replication-study` (which starts here). `/plan` directly follows `/question` in the standard flow.

**Default agents:** `methodologist`, `statistician`, `preregistration-reviewer`

---

## Contract

**Input:** the sharpened question from `/question` (or the claim frame for Persona C) plus any domain-specific context (task details, existing code, corpus constraints, prototype evidence).

**Output:** a hash-sealed `preregistration.yaml` artifact plus a human-readable summary; confirmation of analysis plan, predictions, stopping rules, and the honest-pivot clause before proceeding to `/execute`.

**Exit condition:** user confirms the pre-registration, SHA256 is locked, and the mode hands off to `/execute`.

## Persona-aware behavior

**Persona A (non-scientist):**
- Translate "pre-registration" as "locking down the plan before we look at the results — so you can trust what we find."
- Ask for minimum viable specificity. For patent/policy work: (1) what evidence would count as novelty, (2) what would count as enablement, (3) what's the search strategy?
- For prior-art search: show a sample query and ask if the direction is right before going deep.
- Frame predictions as "what would you expect to find" — not as "hypothesis."
- Show the locked hash in plain English: "This hash is your proof we didn't change the plan after we saw the results."

**Persona B (working researcher):**
- Use discipline-appropriate terms: hypothesis, MDE, power analysis, stopping rules.
- Invoke `statistician` to confirm sample size against planned effect sizes; return effect-size estimates with CIs from prior work if available.
- Ask explicitly: exploratory zone or confirmatory only? (Mark clearly in artifact.)
- Confirm analysis plan is specific enough to be falsifiable: which tests, which outcome order, which corrections, fixed or adaptive?
- Invoke `preregistration-reviewer` to screen for specification gaps before hash-locking.

**Persona C (reviewer):**
- `/plan` is rarely the entrypoint. If invoked, it's typically to extract the implicit methodology from an incoming document (e.g., a whitepaper that never names a pre-registration but claims an analysis plan). Mode shifts: ask the user to provide the document, extract the methodology, and surface it for confirmation.
- Behavior: "Here's what the document claims its analysis plan was. Is this what it actually did?"

## Key outputs

On exit, `/plan` writes:

```
.amplifier/sessions/<session>/preregistration.yaml
  - sharpened_question (from /question)
  - recipe_name
  - personas_included: [A|B|C]
  - predictions: {confirmatory: [...], exploratory: [...]}
  - analysis_plan: {tests: [...], corrections: [...], order: [...]}
  - power_analysis: {n_per_condition: ..., mde: ..., power: ...}
  - stopping_rules: {p_threshold, early_termination_if: ...}
  - honest_pivot_clause: true
  - prior_art_search_plan: (Persona A/B) {databases: [...], queries: [...], depth: ...}
  - evidence_collection_plan: (Persona A) {source_categories: [...]}
  - locked_sha256: <hash>
  - locked_at: <timestamp>
```

## Persona A worked example (patent brief)

```
User (via /question): "A closed-loop compute allocator for AI agent sessions."

Mode:  Before we search for prior art, let's nail down exactly what
       we're looking for. Three things:

       1. NOVEL CLAIM: Is the novelty the feedback loop itself, the
          value estimator, the allocator, or some specific combination?

       2. ENABLEMENT: What's the minimum working demo that proves
          someone could build this? Do you have code?

       3. SEARCH SCOPE: Are we searching just patents, or also
          academic papers and open-source? Both matter.

User:  "1) the feedback coupling specifically. 2) yes, we have a
       working prototype in Python. 3) both."

Mode:  Good. Here's the prior-art search plan:

       DATABASES
         - Google Patents (US, WO)
         - IEEE Xplore
         - arXiv CS.AI
         - GitHub (keyword + "allocat" + "agent")

       SEED QUERIES
         - "compute allocation" + "feedback"
         - "agent" + "resource" + "dynamic"
         - "reinforcement learning" + "budget"

       SNOW-BALLING
         - Two rounds of cited-by expansion from top 5 results

       This will surface references where the loop is pre-registered,
       not discovered after results. That's our anchor: "What did
       prior art explicitly claim was possible?"

       Once locked, we'll build a claim-chart template showing:
         (A) Reference X's approach to allocation
         (B) Why it doesn't include the feedback loop
         (C) Why the loop is non-obvious given prior work

       Ready to lock this plan?

User:  "Yes."

Mode:  ✓ Pre-registration locked.
         SHA256: 3f9a2b7e...c4e8
         Locked at: 2026-04-22 14:33 UTC

       Next: /execute will run the prior-art search and populate
       the claim chart.
```

## Persona B worked example (empirical paper)

```
User (via /question): "Reflection tokens at trained intervals improve
                       reasoning on GSM8K and AIME."

Mode:  Let's lock the analysis plan. Four key questions:

       1. CONFIRMATORY PREDICTIONS
          What specific deltas are you committing to? (pp improvement,
          not "significant")

       2. POWER ANALYSIS
          You said "paired McNemar." How many items per condition
          does your test set have? I'll compute the n needed for
          your effect sizes at α=0.05, power=0.8.

       3. EXPLORATORY ZONE
          Anything you want to explore but not commit to?

       4. STOPPING RULES
          Run to completion or watch for early termination?

User:  "1) +3pp GSM8K, +2pp AIME. 2) both test sets have 750+ items.
       3) I want to explore reflection density (4 sweeps). 4) run to
       completion."

Mode:  Power analysis (using McNemar):
         - GSM8K, 3pp effect: n=512 paired at power=0.8
         - AIME, 2pp effect: n=512 paired at power=0.8
         - You have >750 in both. ✓ Sufficient.

       Confirmatory claims:
         - Reflection tokens improve GSM8K (McNemar, α=0.05,
           one-sided, directional)
         - Reflection tokens improve AIME (McNemar, α=0.05,
           one-sided, directional)

       Exploratory zone (will be labeled in Results):
         - Reflection density sweep: 4, 6, 8, 16 tokens per seq

       Analysis order (to prevent p-hacking):
         1. Run both tests
         2. Report results for GSM8K
         3. Report results for AIME
         4. Report density sweep under "Exploratory"
         5. No post-hoc tests until after density results locked

       Ready to lock?

User:  "Yes."

Mode:  ✓ Pre-registration locked.
         SHA256: a7c1b4d9...2e9f
         Locked at: 2026-04-22 15:07 UTC
         Honest-pivot clause: ACTIVE
         Exploratory zone: 1 zone flagged (density sweep)

       Next: /execute will run your test suite.
```

## Interaction with behaviors

**`honest-pivot`:** activates on `/plan` exit. Once the pre-registration is locked, any deviation from the predictions in `/execute` is flagged. The honest-pivot clause is written into the preregistration and becomes the commitment contract.

**`exploratory-labeling`:** zones marked in `/plan` carry that label through `/execute` results and into `/draft`. A result marked exploratory in the pre-registration cannot be claimed as confirmatory later.

## Failure modes to refuse

- **User wants to skip `/plan` and go straight to `/execute`.** Mode politely insists; this is the core of the bundle's value. One-paragraph explanation + `--skip-plan` bypass (logged as audit trail).
- **Pre-registration is too vague to be falsifiable.** "Predictions" like "there will be a significant effect" don't count. Mode returns to `methodologist` for specificity: what direction, what size, computed over what subsample?
- **Persona A/B can't articulate search/analysis strategy.** Mode asks clarifying questions or offers a default template appropriate to the recipe (e.g., "Patent prior-art search" template with boilerplate databases and queries).
- **Persona C tries to extract methodology from a document that has none.** Mode surfaces this: "The document doesn't describe how the analysis was planned in advance. I can only review what's documented. Would you like me to extract what analysis it appears to have done, post-hoc?"
