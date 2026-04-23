# UX Mockup

A full transcript of Persona A — a patent attorney with no scientific training — using the bundle end-to-end. This is what "as easy as stories" should feel like.

---

## Scenario

Persona A has a client invention: a closed-loop system that adjusts AI agent compute spend per session based on realized task value. Needs a USPTO-ready brief.

## Installation

```bash
$ amplifier bundle add --app git+https://github.com/michaeljabbour/amplifier-bundle-research@main
✓ Registered bundle: research (v0.1.0)
✓ Skills registered (10): hypothesis-generation, scientific-critical-thinking,
  statistical-analysis, peer-review, scholar-evaluation, scientific-writing,
  scientific-schematics, citation-management, venue-templates,
  scientific-brainstorming
✓ Recipes available (7): patent-brief, policy-brief, white-paper,
  lit-review, empirical-paper, grant, replication-study

$ amplifier bundle use research
✓ Active bundle: research
```

Total: two commands. No config file edits. No API keys beyond the one Amplifier already has.

## First interaction — interactive mode

```bash
$ amplifier
Amplifier research bundle v0.1.0
Type /modes to see available modes, /recipes to see recipes.

> I have a client invention I need to draft a patent for.

Nice. I can walk you through a USPTO-ready brief. The recipe is
`patent-brief`, which runs six modes end-to-end:

  /question  — sharpen the invention into defensible claims
  /plan      — lock the approach: prior-art search, claim structure
  /execute   — do the prior-art search, build the claim chart
  /critique  — stress-test for novelty and enablement
  /draft     — produce the brief
  /publish   — USPTO-formatted DOCX + PDF

Want me to start, or would you rather describe the invention first?

> describe first: it's a system that watches an AI agent session and
> adjusts how much compute it gets based on whether the work is
> actually paying off. closes the loop between value and spend.

Got it. Before we commit to claims, a quick /question pass to
sharpen. Three things I need to pin down:

  1. What exactly is novel — the closed loop, the value estimator,
     the allocator, or the combination?
  2. What's the measurable effect vs. prior art — tokens saved?
     task completion? something else?
  3. What's the minimum enablement demo — can you actually
     demonstrate this, or is it conceptual?

> 1) the combination, especially the feedback mechanism
> 2) tokens spent per task that gets resolved
> 3) yes we have a working prototype

Good. Here's the sharpened claim frame:

  CLAIM FRAME
  A runtime governance system comprising:
    (a) a per-session value estimator that scores realized task
        progress against a declared goal
    (b) a compute allocator that adjusts per-step inference budget
        based on (a)'s output
    (c) a feedback loop connecting (a) and (b) with a documented
        update rule

  DIFFERENTIATION
  Prior art includes static budget caps and per-prompt rate
  limits. The novelty candidate is the closed-loop coupling of
  realized-value measurement to allocation, not either piece alone.

  MEASURABLE EFFECT
  Tokens-per-resolved-task reduction vs. baseline (static budget,
  same model, same task).

Does this frame match your intent? If yes, I'll move to /plan.

> yes exactly

[ honest-pivot: ON · exploratory-labeling: ON ]

Moving to /plan. This will take ~2 minutes. I'm going to:
 - design the prior-art search strategy
 - write the preregistration artifact (hash-locked)
 - set up the claim chart template
 - identify the enablement experiments to describe

...

✓ Pre-registration written to docs/plans/2026-04-22-preregistration.yaml
  SHA256: 3f9a2b...c4e8
✓ Prior-art search plan: 4 databases, 12 seed terms, snowball depth 2
✓ Claim chart template: 7 columns, one row per independent claim
✓ Enablement sketch: minimal working demo in 1 notebook, 3 figures

Ready for /execute? This will search prior art (~5 min) and
run your enablement demo if you point me at the prototype.

> go, prototype is at ~/src/rolling-roi

...

[output abbreviated — prior-art results, enablement runs, claim
 chart populated]

Moving to /critique. I'll stress-test what we have.

✓ Novelty stress test: 2 close references found. Both on static
  allocation. Neither describes the feedback coupling. Novelty
  claim stands with respect to these references.

⚠ Enablement stress test: the description of the value estimator
  is underspecified. A PHOSITA reading only the current draft
  could not reproduce it. Fix before /draft.

⚠ Overclaim flag: draft text says "substantially reduces" — we
  have n=1 prototype. Recommend softening to "reduces in
  prototype testing" with CI or dropping quantifier entirely
  until broader evidence.

✓ Scholar-eval scores:
    novelty:       4.2/5
    clarity:       3.1/5  ← improve in /draft
    enablement:    2.8/5  ← fix before /draft
    evidence:      3.6/5

Would you like me to pause here so you can fix the enablement
description, or should I /draft with the flags visible in the
document so your reviewer sees them?

> pause, I'll add more detail to the estimator

...later...

> I've updated the doc, re-run /critique

✓ Enablement stress test: passes. PHOSITA could now reproduce.
✓ Overclaim: fixed.
✓ Scholar-eval scores: novelty 4.2 / clarity 3.9 / enablement 4.1 /
  evidence 3.6

Ready for /draft.

> go

✓ Drafted USPTO-style brief:
    Field of Invention
    Background
    Summary of the Invention
    Detailed Description
    Claims (1 independent, 14 dependent)
    Abstract
    Drawings (4 figures, generated via figure-designer)

Moving to /publish. Target: USPTO.

✓ Output written:
    ./output/patent-brief.docx
    ./output/patent-brief.pdf
    ./output/drawings/
    ./output/claim-chart.xlsx
    ./output/prior-art-table.xlsx
    ./output/preregistration.yaml (hash-locked)

Total time: ~25 minutes of your attention spread over ~45 minutes
of wall clock. Ready for your filing attorney's review.
```

---

## What makes this feel easy

Five things, deliberate:

1. **The bundle does the translation.** The attorney never hears "operationalize" or "falsifiable." They hear "what specifically is novel" and "can you actually demonstrate this." Same concept, plain English.

2. **The bundle asks one thing at a time.** No wall-of-questions. Each mode has a few key decisions; the user answers them in turn.

3. **Flags are actionable.** When `honest-critic` finds an overclaim, it names the specific sentence and suggests the fix. Not "your paper has issues" — "line 47 says 'substantially reduces' but you have n=1; suggest softening."

4. **Output is real.** At the end there's a DOCX the attorney can hand to a filing colleague. Not a chat log, not a set of notes — an artifact.

5. **The discipline is invisible but present.** The user didn't know they did pre-registration. They did. They didn't know they wrote a CONSORT-style methods section. They did (adapted to patent context). The rigor is baked in, not taught.

---

## Same mockup, Persona B — working researcher

```bash
$ amplifier
> /plan
  What's the pre-registration for?

> reflection tokens experiment — comparing base model vs. base +
> reflection insertions, on GSM8K and AIME, seed 42, paired McNemar.

✓ Drafting preregistration from your description...

Questions before I lock the hash:
  1. Confirmatory predictions — what delta are you committing to?
  2. Minimum detectable effect — power analysis says you need
     n=512 paired items at α=0.05, power=0.8 for a 3pp shift.
     That fits your test set?
  3. Exploratory zone — anything you want to explore but not
     claim confirmatorily?

> 1) +3pp on GSM8K, +2pp on AIME
> 2) yes, both >512
> 3) reflection density sweep (4 densities)

✓ Pre-registration written. SHA256: a7c1b4...9f2e
✓ Honest-pivot clause: ON
✓ Exploratory zone labeled: reflection density sweep → will be
  reported under "Exploratory" in Results, not Confirmatory.

Ready for /execute whenever you are.
```

Persona B hits the bundle fluent. Same contract, less hand-holding.

---

## Same mockup, Persona C — reviewer

```bash
$ amplifier run --mode critique --input incoming-whitepaper.pdf \
    --recipe due-diligence

✓ Extracted 6 load-bearing claims from the whitepaper.

CLAIM EVALUATION
  Claim 1: "Our model outperforms GPT-5 on reasoning."
    Evidence: benchmark scores on Appendix B table.
    Issues: baseline is GPT-5 base, not GPT-5 with reasoning mode.
            Sample size n=50 per benchmark, no CIs.
    Verdict: WEAK — claim as stated is unsupported; a narrower
             claim (outperforms base GPT-5 on specific subset)
             would be defensible.

  Claim 2: "40% cost reduction in customer deployments."
    Evidence: single case study, no methodology section.
    Issues: survivorship bias (one customer shown), no baseline,
            no confidence interval.
    Verdict: SPECULATIVE — treat as anecdote, not evidence.

  ...

SCHOLAR-EVAL AGGREGATE
  Methodology: 2.1/5
  Evidence:    2.4/5
  Clarity:     4.0/5
  Novelty:     3.3/5

RECOMMENDED FOLLOW-UPS
  - Request raw benchmark data with CIs
  - Request additional customer case studies
  - Request method section detail for cost-reduction claim

Written to ./output/whitepaper-critique.md
```

One command, structured output, ready to act on.
