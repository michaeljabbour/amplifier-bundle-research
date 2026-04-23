# A Methodology Scaffold for Patent Drafting

**Subtitle / Tagline:** How amplifier-bundle-research v0.4.0 makes an attorney's own discipline visible, auditable, and portable — and what it does not yet do.

**Prepared by:** Michael Jabbour (independent; author of the bundle described herein)
**Author(s):** Michael Jabbour
**Date:** April 23, 2026
**Version:** 0.1 (first public capability description)

---

## Disclosure: This Is a First-Person Capability Description

This paper is written by the author of amplifier-bundle-research. It describes what the bundle does and where it may be useful. **It does not constitute an independent capability evaluation.** Readers should treat the measured claims here as the author's best-faith walkthrough evidence and weigh them accordingly. A v1.0 milestone has been reserved for real-attorney validation by practitioners the author does not employ or direct; that validation has not yet been performed. Where the paper makes a capability claim, the evidence provided is of the form "the bundle produced this artifact when run" — not "this artifact improved an attorney's filing."

Conflict-of-interest posture: the author benefits from adoption of the bundle (reputational, not financial in v0.4.0; the bundle is open-source under Apache-2.0). The paper is therefore best read as an invitation to independent evaluation, not as an independent evaluation itself.

---

## Executive Summary

Patent prosecution is an evidence-defensibility craft. An attorney drafting a § 112-compliant specification and a § 103-resistant claim set is doing something structurally similar to what a scientific author does when drafting a methods section: committing to a scope and a standard of evidence before the examiner (or the reviewer) gets to test it.

The problem this paper addresses is specific: **when attorneys use general-purpose AI (ChatGPT, Claude, Gemini) to accelerate first-draft work, the methodology steps that the human was silently carrying — search scope discipline, overclaiming detection, enablement self-check — get quietly skipped.** The draft looks good. The examiner finds the gap later, when amendment space is expensive.

amplifier-bundle-research v0.4.0 is a machine-assisted methodology scaffold that forces these steps to happen, on the record, before the first draft exists. It is not a drafting robot. It does not emit filing-ready prose. It imposes a six-step sequence — `/question`, `/study-plan`, `/execute`, `/critique`, `/draft`, `/publish` — over the attorney's own drafting work, with hash-locked pre-registration of search scope and a structured peer-critique pass (severity-labeled: BLOCK / WARN / NOTE) before the draft ships.

**What the paper argues.** The bundle (1) makes the attorney's prior-art search scope reproducible by a second attorney reading the audit trail; (2) surfaces § 112 enablement gaps as BLOCK-severity findings before the final review pass; (3) does so without narrowing the claim scope the attorney would have chosen manually. The paper grounds each claim in three reproducible walkthroughs and a four-class competitive analysis.

**What the paper does not argue.** That the bundle saves wall-clock time against any baseline — no measured time-cost data exists for v0.4.0. That the bundle replaces an attorney's legal judgment. That it improves patentability of a weak invention. That it reduces malpractice exposure — exposure is *attorney* exposure, not tooling exposure, and the bundle's default hosted-LLM configuration **introduces trade-secret risks that make it inappropriate for confidential-invention matters until an on-prem deployment mode is validated**.

**Headline limitation.** v0.4.0 has passed programmatic verification (5 tests) and simulated-persona acceptance (3 personas, all performed by the author). It has **not** been used by a real patent attorney on a real filing. The paper should be read as a pre-validation capability description soliciting exactly that independent evaluation.

**Action for the reader.** Prosecution attorneys curious about methodology-visibility tooling are invited to run the bundle on a non-confidential disclosure and contact the author with feedback. Firms with confidentiality-bound matter should wait for the on-prem deployment mode (roadmap: v1.x).

---

## Problem Statement

### The craft attorneys already practice

Patent attorneys drafting for USPTO examination work against three statutory lenses that are, in substance, defensibility questions:

| Statutory lens | The question underneath it | Scientific-rigor analogue |
|---|---|---|
| **§ 102** (novelty) | Has anyone already done this? | Literature review; prior-art adequacy |
| **§ 103** (non-obviousness) | Would the obvious next step for a person of ordinary skill in the art get here? | Comparison-to-baseline; incremental-contribution argument |
| **§ 112** (enablement + written description) | Does the specification actually teach someone skilled how to build it? | Methods reproducibility; reader-can-rebuild test |

The correspondence is not accidental. Both domains evolved to protect downstream readers (examiners, reviewers, competitors, courts) from claims the author cannot back up. The craft is continuous even if the vocabulary differs.

### How general-purpose AI leaks the craft

General-purpose large language models (ChatGPT, Claude, Gemini) are now commonplace in first-draft patent work [1, 2]. The visible failure mode — hallucinated references — gets caught quickly by any attorney who reads the output. The **invisible** failure mode is the skipping of disciplined steps the human was silently carrying:

1. **Prior-art search scope drift.** An attorney with a raw-LLM workflow asks the model to draft, receives a draft, notices a reference they had not planned to exclude, and quietly excludes it. No audit trail records that this scope narrowing happened.
2. **Silent enablement gaps.** The model writes a plausible detailed description using intuitive-sounding parameters. The specification looks complete. It is not — a person of ordinary skill in the art (a "PHOSITA" in § 112 vocabulary) could not rebuild the invention from the description because certain assumptions were never stated.
3. **Adverb creep.** "Substantially," "dramatically," "significantly" and similar adverbs accumulate in the detailed description. Each is a small overclaim; together they weaken the enablement the specification is supposed to provide.

None of these failures are specific to AI. They have existed as long as patent drafting has. AI accelerates draft production without accelerating the disciplined checks that would catch them. The result is that the checks get deferred to the final review pass, where they are more expensive to address.

### Regulatory context: USPTO AI-use disclosure

The USPTO's 2024 AI-assistance guidance and subsequent 2025 updates impose registration and disclosure obligations when AI tools are used in prosecution, and extend the duty of candor (37 CFR 1.56) to cover AI-induced errors [3]. An attorney using AI-assisted drafting is therefore obligated to understand — and, if necessary, disclose — which steps the tool performed. A methodology scaffold that makes those steps visible is not only a rigor benefit; it is adjacent to a compliance benefit. The paper does not claim that the bundle satisfies USPTO AI-disclosure requirements on its own. It claims only that the methodology trail the bundle produces is structured in a way that would make such disclosure easier to draft.

### Why this matters now

Two things have changed in 2024-2025 that make the problem newly acute. First, AI-drafted prose has become good enough that attorneys do not feel the traditional "this is awkward, let me rewrite it" reflex on the output — the draft flows, and review slows. Second, the USPTO has explicitly put AI use under the disclosure lens, which means the internal "I cannot remember if I searched that class" moment is now potentially externally observable. The missing piece is tooling that imposes the audit trail without demanding that the attorney learn a new vocabulary.

---

## Background and Market Context

### Industry landscape

Tools that touch the "draft patent applications" job split into four categories, each optimized for a different piece of the problem. The bundle does not replace any of these — it occupies a niche they collectively under-serve.

**Class 1: IP portfolio and docket management suites** — PatSnap, Anaqua, Clarivate IP Management. Mature prior-art search across millions of records; portfolio analytics; deadline docketing; family-tree management. **Not a drafting tool.** These are comparison points on the "auditable methodology trail" dimension only, not on drafting capability.

**Class 2: AI-assisted drafting tools** — Rowan Patents, Solve Intelligence, ClaimMaster, Patent Bots, and similar 2024-2025 entrants. Optimized for filing-ready prose output and claim-chart automation. Methodology layer is typically proprietary and not externally auditable. Attorney cannot reproduce a drafting decision without vendor cooperation.

**Class 3: General-purpose LLMs** — ChatGPT o1/o3, Claude Sonnet/Opus, Gemini 2.5 Pro. Zero setup; universal access; no patent-specific scaffolding. Attorney carries all discipline manually. The de facto baseline for solo practitioners and small firms that cannot justify Class-1 procurement.

**Class 4: Firm-internal checklists and templates** — tacit knowledge encoded in drafting templates, MPEP-derived checklists, AIPLA-published templates where available. Battle-tested but invisible to audit. Scales poorly across attorneys; degrades with turnover.

### Related prior work

The conceptual ancestor of the bundle's approach is the **pre-registration movement in empirical science** [4]. Nosek and colleagues documented that in fields where authors commit their analysis plan to a public repository before seeing the data, downstream rates of motivated-reasoning-driven post-hoc analysis drop measurably. ClinicalTrials.gov registration obligations under the FDA Amendments Act of 2007 extended the same principle into a regulatory framework for medical trials.

**This is an analogical argument, not a transferred evidence base.** Nothing in the patent-specific literature establishes that pre-registration discipline improves patent prosecution outcomes. The bundle takes the *mechanism* (locking methodology decisions before results, creating an audit trail for any later narrowing) and applies it to a domain where the same failure modes — motivated-reasoning-driven scope narrowing, unstated enablement assumptions, adverb creep — are documented and familiar.

### Development timeline

The bundle's public history is short. v0.2.0 was released April 22, 2026 (initial public release). v0.4.0 was released the same day, adding programmatic verification of the tool protocol, the LaTeX compilation pipeline, and simulated-persona acceptance tests. This white paper is dated the day after v0.4.0 and is the first public capability description. A same-day capability paper after a tool release should be read with appropriate skepticism about commercial motivation — the author discloses that the primary goal of the paper is to solicit independent evaluation, not to drive sales (the bundle is free).

---

## Proposed Approach

### Core concept

**Impose an auditable six-step drafting sequence over the attorney's own work.** The bundle does not take over drafting. It provides six sequential modes, each of which produces a concrete artifact that the attorney (or a second attorney) can inspect, reproduce, or challenge.

```
/question  →  /study-plan  →  /execute  →  /critique  →  /draft  →  /publish
(sharpen     (hash-lock      (prior-art    (severity-   (populate   (format
 the claim)   scope and       search +      labeled      template)   for venue)
              method)         enablement    findings)
                              plan)
```

Each mode takes the previous mode's artifact as input. The artifact chain is the audit trail.

> **Reader note:** The slash command for the second mode is `/study-plan` rather than `/plan` because `/plan` is reserved by a companion bundle (`amplifier-bundle-modes`). Prose elsewhere in this paper uses "the plan mode" as shorthand when the slash command naming is not the point.

### How it works

**`/question` — Sharpen the rough claim.** The attorney types the invention description in plain English. The bundle's `hypothesis-designer` agent produces a structured artifact naming: a one-line statement of what the invention is; a claim frame (what kind of claim it is, and what it is not); directional predictions with named mechanisms; explicit disconfirmation criteria; and a novelty note positioning the invention against identified prior-art classes.

The sharpening step is particularly useful for patent work because it exposes, early, which parts of the invention the inventor considers load-bearing and which parts are scaffolding. The artifact can survive into the Field of Invention / Summary sections of the specification.

**`/study-plan` — Lock methodology before search.** Produces a hash-sealed `preregistration.yaml` file committing to: the prior-art search plan (search terms, CPC/IPC classification codes, date cutoff, explicitly excluded classes); the enablement-demonstration plan (what prototype, simulation, or reasoned argument will support § 112); the honest-pivot clause (what happens if the search reveals a claim needs narrowing); and abandonment criteria (conditions under which the filing should not proceed).

**This is the load-bearing innovation.** A hash-sealed search plan means that later narrowing — excluding a class because it surfaced uncomfortable art, dropping a search term because it returned too much to review — is visible in a timestamped amendment log rather than invisible in the final draft. A second attorney auditing the work can reproduce the planned search and compare it to the executed search. The cost of reproducibility is paid at plan time, not at office-action-response time.

**`/execute` — Run the plan.** Performs the prior-art search against configured sources (USPTO, Google Patents, arXiv, IEEE Xplore); populates a claim chart; runs an enablement demonstration if one was planned. Any deviation from the plan is logged as an honest-pivot entry. The output is an evidence log keyed to the claims the `/question` artifact identified.

**`/critique` — Argue against the draft.** The `honest-critic` agent issues severity-labeled findings (BLOCK / WARN / NOTE) across five dimensions: thesis defensibility, overclaiming detection, evidence gaps, generalization limits, and limitation specificity. The `BLOCK` label is reserved for issues that would survive into the filed application as traceable weaknesses — silently narrowed claims, unsupported enablement statements, superlatives without numeric backing. The attorney retains accept-reject control over every finding; the bundle emits the finding-with-context, never the forced edit.

**`/draft` — Populate the venue-specific template.** For patent work, the template is the USPTO invention-disclosure structure (Field of Invention → Background → Summary → Detailed Description → Claims → Abstract → Drawings). The `technical-writer` agent composes the sections from the evidence log; the `citation-manager` agent assembles the prior-art bibliography in USPTO format. This is the step most similar to what classic AI-drafting tools (Class 2 above) provide.

**`/publish` — Format for the venue.** The `venue-formatter` agent applies USPTO document formatting — 37 CFR 1.52 margins, line spacing, consecutive page numbering, claim numbering — and emits filing-ready DOCX and PDF. A deterministic Python script (`scripts/compile_latex.py`) handles the final compilation step where mechanical correctness matters more than language-model fluency. The `/publish` gate refuses to execute unless at least one `/critique` pass has been run and any honest-pivot entries are acknowledged.

### What makes it different

Most AI-assisted drafting tools (Class 2) and general LLMs (Class 3) optimize for *output quality*. The bundle optimizes for *methodology visibility*. The differentiating choices:

1. **Pre-registration is mandatory, not opt-in.** `/publish` blocks if `/study-plan` did not produce a sealed prereg.
2. **Critique is a separate, structured pass.** Not "the draft looks good and the user accepts it," but a labeled-finding pass that an attorney can re-inspect after a year.
3. **The attorney holds the pen at every mode.** The bundle never commits an edit without the attorney's acceptance at that mode boundary.
4. **The audit trail is human-readable.** `preregistration.yaml`, `evidence-log.yaml`, `critique.yaml` are YAML, not proprietary binaries. A second attorney can reproduce a run from these files.
5. **Output is inspectable at every stage.** Every mode writes a named artifact to disk. A failed run is debuggable by reading those artifacts.

These choices come at a cost: the bundle is slower than a raw-LLM "draft me this application" prompt. The sequence takes as long as the attorney spends reviewing each mode's output. For an attorney whose pain is "I want prose fast," the bundle is the wrong tool. For an attorney whose pain is "I can write the prose; I just cannot remember every step I should have done," the bundle's sequence carries the discipline.

---

## Evidence and Case Studies

All three case studies below are **author-generated** — two from dogfood runs of the bundle on itself, one from a simulated-persona acceptance test the author ran during v0.4.0 development. They are presented as capability demonstrations (the bundle produces these artifacts when run) and not as outcome evidence (these artifacts improved attorney filings). This framing matches what the evidence actually supports; attempts to present these as outcome evidence would fail the paper's own `/critique` pass.

### Case Study 1: `/question` dogfood on the bundle's own design

**Context.** The bundle was asked to run `/question` on the statement "amplifier-bundle-research should be valuable for patent attorneys." Captured during v0.3 verification on 2026-04-22 (git commit `d528196`).

**Intervention.** `/question` mode with the `hypothesis-designer` agent.

**Outcome.** A 97-line structured `sharpened_question.yaml` artifact containing: a one-line thesis with explicit claim type, three directional predictions with measurable criteria, disconfirmation conditions, scope boundaries, and a four-class novelty note distinguishing the bundle from IP management suites, AI-drafting tools, raw-LLM chat, and firm-internal checklists.

**Measured impact.** Artifact size: 97 lines. Reproducibility: any reader can re-run the same prompt against their own `amplifier` install and diff the outputs to test drift.

**What this does and does not prove.** It proves the bundle produces a question-sharpening artifact with the claimed shape. It does **not** prove the artifact is useful to a patent attorney; no attorney has yet reviewed it.

### Case Study 2: `/study-plan` smoke test — patent-schema pre-registration

**Context.** A `/study-plan` run on a synthetic software-ML invention, producing a populated instance of `templates/patent-prereg.yaml`. Captured during v0.3 verification on 2026-04-22.

**Intervention.** `/study-plan` mode with `methodologist` + `preregistration-reviewer` agents.

**Outcome.** A 57-line `patent-prereg.yaml` artifact containing: prior-art search plan (search terms, CPC classes, date cutoff), enablement-demonstration plan, honest-pivot clause, abandonment criteria, and a sha256 seal section.

**Measured impact.** All 8 required patent-prereg fields populated. sha256 seal present. Honest-pivot clause reads as attorney-interpretable (per the author's own self-review — not an independent judgment).

**What this does and does not prove.** It proves the pipeline produces a structurally complete pre-registration artifact. It does **not** prove the search plan is well-chosen for any real invention, nor that an attorney would accept the generated terms without revision.

### Case Study 3: Simulated Persona-A acceptance test (the mixed case)

**Context.** v0.4 simulated-persona acceptance test (documented in release notes for `d528196`). The author played the role of a patent attorney taking a plausible software-ML invention through `/question` → `/study-plan`. The test was designed to answer: does the pipeline produce what a patent attorney would expect to see at each stage?

**Intervention.** End-to-end `/question` → `/study-plan` pipeline.

**Outcome.** A patent-schema preregistration with prior-art search plan, enablement demonstration, honest-pivot clause, and abandonment criteria. Overclaiming adverbs in the scratch specification were correctly flagged for removal during the pass.

**Measured impact.** Pipeline ran to completion. Every required artifact section was populated. By the author's own rubric — answering "does this look like what I expect a patent attorney would expect?" — the output was persona-appropriate.

**What this does and does not prove (this is the mixed case).** The author is both the bundle designer **and** the simulated attorney. This is a correctness-of-shape test, not a usefulness test. A real attorney reading the output might find it overengineered, underengineered, or calibrated wrongly in ways the author cannot self-detect. This case is cited as evidence of **capability** (the bundle produces what it claims) not of **usefulness** (attorneys prefer this workflow).

CS3 is the headline mixed result: **the bundle passed the author's own acceptance test and still has not been validated by a real attorney.** That gap is the paper's headline limitation, not a footnote.

### Supporting data

Programmatic verification of v0.4.0 (all passing):

- `tool-paperbanana.mount()` protocol compliance: 8 of 8 checklist items (figure-generation tool exposes the expected interface to the coordinator).
- `scripts/compile_latex.py` produces a clean 82 KB PDF from a test `.tex` input across supported venue templates.
- `scripts/download_templates.py` handles ACL + IEEE + ACM template downloads via CTAN without manual intervention; NeurIPS + ICML produce a graceful manual-download-instruction path.
- `/question` dogfood produces the 97-line sharpened_question artifact referenced in CS1.
- `/study-plan` smoke test produces the 57-line patent-schema prereg referenced in CS2.

Simulated-persona acceptance (all passing):

- Persona A (patent attorney): `/question` + `/study-plan` with enablement demo, honest-pivot clause, abandonment criteria.
- Persona B (ML researcher): `/question` with discipline-specific statistical terminology (pass@1, McNemar, BH-FDR, TOST, mixed-effects); three operationalized predictions; novelty note distinguishing from Reflexion and Self-Refine.
- Persona C (peer reviewer): `/critique` standalone with severity-labeled findings, REFORMS-ML checklist correctly selected over PRISMA/STROBE for an ML paper, scholar-evaluation scores, WEAK verdict with three remediation asks.

Each verification step is reproducible by any reader cloning the bundle repository and running the referenced scripts or dogfood prompts. What these verifications do **not** establish is whether the outputs are *useful*; utility requires real-user validation, which is scheduled as the next milestone.

---

## Competitive Analysis

The bundle occupies a methodology-visibility niche. The table below compares across a single axis — "does the workflow produce an attorney-reviewable audit trail of its methodology decisions?" — because that is the axis the bundle claims as its differentiator. Comparators B1 (IP management) and B4 (internal checklists) are adjacent-concern rather than rival products; they are included for landscape completeness, not to suggest the bundle outperforms them on their native axes.

| Approach | Strengths | Weaknesses (for methodology-visibility niche) | Best fit |
|---|---|---|---|
| **IP management suites** (PatSnap, Anaqua, Clarivate) | Mature prior-art search across millions of records; portfolio and docket management; enterprise audit-readiness | Not a drafting tool; no pre-registration of search scope; priced for enterprise procurement | Firms with portfolio-scale docketing and procurement budget |
| **AI-assisted drafting tools** (Rowan, Solve Intelligence, ClaimMaster, Patent Bots) | Filing-ready prose output; claim-chart automation; integrated drafting UI | Methodology layer proprietary and not externally auditable; attorney cannot reproduce drafting decisions; "filing-ready" framing risks deskilling on judgment steps | Attorneys whose primary pain is prose-output speed |
| **General-purpose LLMs** (ChatGPT, Claude, Gemini) | Zero setup; universal access; wide general capability | Attorney carries all discipline manually; no audit trail; inconsistent across sessions; no venue-aware formatting | Quick drafting tasks where attorney provides the full methodology layer |
| **Firm-internal checklists / AIPLA templates** | Battle-tested; tuned to firm philosophy; free | Invisible to audit (which parts were applied?); scales poorly across attorneys; degrades with turnover; rarely portable | Firms with strong senior-to-junior tacit transmission |
| **amplifier-bundle-research v0.4.0 (this paper)** | Pre-registration of search scope before execution; severity-labeled peer-critique pass; honest-pivot enforcement; USPTO-compliant venue formatting; open source; one-command install | **No real-attorney UX validation yet** (v0.4 is simulated-persona only); no measured time-cost comparisons against any baseline; trade-secret-sensitive matters unsafe with default hosted-LLM configuration; prose-polish has received less optimization than Class-2 competitors | Solo / small-firm attorneys who want methodology visibility and are willing to trade prose speed for audit trail |

The bundle's honest weaknesses row (last row above) is populated deliberately. A competitive table where every other product has weaknesses and the author's tool has none is a sales sheet, not a white paper.

### Alternative explanations for any observed appeal

Even if readers find the walkthroughs persuasive, there are at least four alternative explanations for that appeal that the paper should name rather than dismiss:

1. **Novelty effect.** The bundle is new. Attorneys may find it appealing because it is new, not because its methodology scaffolding works. Only longitudinal real-attorney use would distinguish this.
2. **Well-written-checklist effect.** The methodology-visibility benefit the paper claims may be achievable by an attorney using a sufficiently well-written paper checklist. A three-arm comparison (raw LLM / paper checklist / bundle) would be needed to isolate the bundle's contribution. That comparison has not been run.
3. **Boilerplate acceleration confound.** If any time savings do exist, they may be attributable to LLM acceleration of boilerplate prose — a capability *all* AI-drafting tools share — rather than to the bundle's methodology scaffolding specifically.
4. **Over-narrowing risk.** The bundle's honest-pivot and `/critique` passes could encourage attorneys to over-narrow their claims by surfacing every possible concern. Prediction P3 (claim-scope preservation) is an attempt to forestall this; it is not yet empirically validated.

The paper flags these alternatives because they are the critiques a skeptical reviewer would raise — and because the author cannot rebut them with evidence that does not yet exist.

---

## Implementation Considerations

### Prerequisites

- An installation of [Amplifier](https://github.com/microsoft/amplifier) (open source, one-line install).
- Access to a language-model provider configured through Amplifier's standard provider layer (Anthropic Claude, OpenAI, Azure OpenAI, or a local Ollama model).
- Familiarity with the six mode names and their order. The modes are plain English; no prior knowledge of scientific-methodology vocabulary is required. Plain-language explanations appear in the `/study-plan` mode's own output when the attorney first runs it.

### Deployment path

A realistic adoption arc for a solo practitioner or small firm:

1. **Pilot on a non-confidential disclosure.** Run the full six-mode sequence on a published invention (one of the attorney's own already-filed applications, or a public example). Inspect each mode's artifact. Decide whether the scaffolding matches the attorney's own drafting habits.
2. **Evaluate the audit trail.** Open `preregistration.yaml`, `evidence-log.yaml`, `critique.yaml`. Ask: could I reproduce this work six months from now from these files? Could a colleague?
3. **Test critique-finding quality.** Examine the `critique.yaml` output. How many findings are actionable? How many are false positives? The paper predicts these numbers are attorney-specific; only the attorney can judge them.
4. **Do not skip to confidential matter until the deployment mode is validated.** See Risk Analysis below.

### Integration points

The bundle operates on text files on the attorney's local filesystem. It does not require modifications to the firm's docketing system, PDM, or document-management workflow. Output is DOCX + PDF in standard USPTO format. Attorneys can carry the bundle's artifacts into existing workflows without changing other systems.

### Cost and effort

The bundle is free (Apache-2.0). The meaningful cost is attorney time to (a) learn the six-mode vocabulary and (b) review each mode's artifact before proceeding. Order-of-magnitude estimate: half a day of hands-on learning on a pilot disclosure before the attorney can judge fit. This estimate is the author's; real-attorney validation has not measured it.

**The paper explicitly does not claim the bundle saves attorney time compared to any baseline.** It claims the bundle imposes the methodology sequence up front rather than leaving it to be reconstructed during final review. Whether that trade is worth it is an attorney-specific judgment the bundle does not make on their behalf.

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation | Residual |
|---|---|---|---|---|
| **R1. Trade-secret leakage to hosted LLM provider.** Default configuration sends invention disclosures to a hosted model (Anthropic, OpenAI, etc.). This may violate client confidentiality expectations or, in edge cases, export-control restrictions. | Medium (depends on client consent posture) | **High** (legal exposure + malpractice-adjacent) | On-prem deployment modes exist in the broader Amplifier ecosystem (Ollama, local Azure OpenAI). The RESEARCH bundle has **not** been validated end-to-end under these modes for v0.4.0. | **Significant — unresolved for v0.4.0.** Do not use the default configuration on trade-secret-sensitive matter until the bundle's on-prem deployment path is validated (roadmap: v1.x). |
| **R2. Attorney-UX unvalidated.** v0.4.0 has passed simulated-persona acceptance tests (all performed by the author). No real patent attorney has used it on a real filing. Mode-transition friction, default-wording appropriateness, and vocabulary pitch are all unvalidated in anger. | High (this gap is known, not hypothetical) | Medium (delays v1.0; does not harm carefully-reviewed matters) | Post-v0.4 roadmap commits to at least 3 real-attorney sessions before v1.0. The paper itself is an artifact of that validation effort — it exists partly to surface the bundle to attorneys who might participate. | **Significant — the headline limitation.** Early adopters should treat their own use as pilot data. |
| **R3. Claim-scope regression via false-positive critique findings.** `honest-critic` may flag language that is defensible in context as overclaiming, leading an attorney under deadline pressure to accept a narrower claim than they should have filed. | Medium | Medium (catchable on final review by an unpressured attorney) | Findings are severity-labeled (BLOCK / WARN / NOTE); attorney retains accept-reject control; `/critique` shows the specific flagged text in context. | **Minor — mitigable with normal review practice.** The mitigation is UX-theoretic, not UX-measured; v1.0 validation will test attorney accept-reject behavior under realistic deadline conditions. |
| **R4. Methodology-theater risk.** The bundle *could* become a theater of rigor rather than actual rigor — attorneys running through the six modes as ceremony while skipping the substantive review each mode requires. | Medium | Medium-High (worse than no tooling, because it provides false assurance) | The audit-trail design makes skipping visible after the fact; a second attorney can tell whether `/critique` findings were meaningfully addressed. | **Minor — but requires firm-level culture of honest use.** |

### Residual risk

R1 and R2 remain significant for v0.4.0. R1 is a hard external constraint on the bundle's applicability to confidential matter; R2 is the paper's own headline limitation. The honest framing is that v0.4.0 is appropriate for **non-confidential pilot use by attorneys willing to treat their own usage as validation data**. Any other framing overclaims.

---

## Limitations

This section collects limitations the paper has already surfaced in context and names them as the paper's load-bearing honest admissions.

**L1. No real-attorney validation yet.** v0.4.0 passed programmatic verification (5 tests) and simulated-persona acceptance (3 personas, all performed by the author). No real patent attorney has used the bundle on a real filing. All capability claims in this paper are of the form "the bundle produces this artifact when run," not "this artifact improved an attorney's filing." The v1.0 milestone has been reserved for this validation.

**L2. No measured time-cost comparisons.** The paper makes no claim that the bundle is faster or slower than any baseline. No wall-clock data exists on either side of any comparison. Any time-cost claim from a reader's own pilot use should be treated as their own pilot data, not as evidence of a general time-cost property.

**L3. Default configuration inappropriate for trade-secret matter.** See R1. An on-prem deployment mode is on the roadmap; until it is validated end-to-end, the default hosted-LLM configuration is not safe for invention disclosures under pre-filing confidentiality obligations.

**L4. Analogical-reasoning load.** The pre-registration mechanism is drawn from an evidence base in empirical science (Nosek 2018, ClinicalTrials.gov) that does not directly apply to patent prosecution. The argument is "same failure mode, same mechanism should help" — which is a mechanism-similarity argument, not a transferred evidence claim.

**L5. Competitive analysis is asymmetric by design.** Comparators B1 (IP management) and B4 (firm internal checklists) are adjacent product categories, not direct rivals. The table compares them on a single axis — methodology-visibility audit trail — on which the bundle claims differentiation. This is fair only for that axis; readers choosing among these products on other axes (portfolio management, prose polish, integration with existing firm tooling) should not use this table as a ranking.

**L6. The author wrote the paper about the author's tool.** Every capability claim should be read with that conflict in mind. The paper is an invitation to independent evaluation, not an independent evaluation.

**L7. Vocabulary drift.** "Pre-registration," "hash-locked plan," and "sealed methodology" are used across bundle documentation to refer to the same mechanism. The paper uses "pre-registration" consistently; readers of the bundle's source files will encounter the other terms.

---

## Recommendations

**For solo practitioners and small firms:** Run the bundle on a non-confidential disclosure. Open the artifact files. Decide whether the methodology scaffolding matches your own drafting discipline. Feed back what does not fit. Do not use the default configuration on confidential matter until the on-prem deployment mode is validated.

**For firms with confidential matter and procurement budget:** Treat v0.4.0 as a reference architecture for methodology visibility. If the audit-trail idea is compelling, the open-source nature of the bundle allows the methodology layer to be re-implemented behind a firm-internal deployment. Procurement-scale tooling decisions should wait for the v1.x on-prem deployment path and for real-attorney validation data.

**For attorneys considering participating in v1.0 validation:** The path is cheap — a one-line install and a non-confidential disclosure. Participation would produce exactly the evidence this paper cannot yet provide.

**For the author:** The paper's headline limitation (L1) commits the author to prioritizing real-attorney sessions over further feature work until the gap is closed.

---

## Conclusion

**Thesis, restated.** amplifier-bundle-research v0.4.0 imposes a six-step, auditable sequence — sharpen the question, lock the method, execute the plan, argue against the draft, populate the template, format for the venue — over a patent attorney's first-draft work. It makes the attorney's own methodology visible, reproducible, and portable. It does not replace legal judgment, does not emit filing-ready prose autonomously, and **has not yet been validated by a real attorney on a real filing**.

**Strongest evidence.** Three reproducible walkthroughs (CS1, CS2, CS3) demonstrate that the bundle produces artifacts of the claimed shape; five programmatic verifications document that the tool protocol, compile pipeline, and dogfood paths work end-to-end; four classes of competitive alternative are analyzed honestly, including the author's own tool with its weaknesses row.

**Strongest honest concession.** Every capability claim is a capability claim, not an outcome claim. No data exists on whether the bundle helps attorneys write better applications in fewer cycles. That gap is the paper's reason for existing — to solicit the real-attorney sessions that would produce that data.

**Concrete next step for the reader.** Attorneys curious about methodology-visibility tooling should install the bundle, run it on a non-confidential disclosure, and send feedback. The bundle's repository is public, the source is readable, and the v1.0 validation milestone is open for participation.

---

## About the Author

### Michael Jabbour

Michael is the author of amplifier-bundle-research. He is not a practicing patent attorney. His prior work includes the design of methodology-enforcement tooling for evidence-defensibility domains (scientific rigor, technical due diligence). The bundle described in this paper is his attempt to carry that methodology-enforcement approach into patent-drafting workflows. He discloses that he benefits reputationally (not financially in v0.4.0) from adoption of the bundle; the paper is explicitly written as a first-person capability description soliciting independent evaluation, not as a neutral assessment.

---

## References

[1] IPWatchdog. "AI-Assisted Patent Drafting: Practitioner Perspectives, 2024-2025." Series of articles; see `ipwatchdog.com` archive for the 2024-2025 AI-drafting coverage cited in the Problem Statement.

[2] Patently-O. "Artificial Intelligence and Patent Practice." Series of posts by Dennis Crouch et al., 2024-2025, surveying AI-drafting tool use and failure modes in practice; see `patentlyo.com` archive.

[3] United States Patent and Trademark Office. *Guidance on Use of Artificial Intelligence-Based Tools in Practice Before the USPTO.* April 2024, with subsequent 2025 updates. Available: https://www.uspto.gov/ (search: "AI guidance 2024"). Registration and disclosure obligations under 37 CFR 1.56 extended to AI-induced errors.

[4] Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). "The preregistration revolution." *Proceedings of the National Academy of Sciences*, 115(11), 2600-2606. https://doi.org/10.1073/pnas.1708274114 — **cited as analogical support only**; does not directly evidence patent-prosecution improvement.

[5] United States Patent and Trademark Office. *Manual of Patent Examining Procedure (MPEP)*, § 2100 series (patentability), § 2141 (obviousness / Graham v. Deere factors), § 2163 (written description and enablement under § 112(a)). Available: https://www.uspto.gov/web/offices/pac/mpep/

[6] 37 CFR 1.52. "Language, paper, writing, margins, compact disc specifications." Governs USPTO document-formatting requirements referenced in the `venue-formatter` implementation.

[7] FDA Amendments Act of 2007, Public Law 110-85, § 801. Establishes the ClinicalTrials.gov registration obligation cited as an analogical regulatory-pre-registration precedent.

[8] Graham v. John Deere Co., 383 U.S. 1 (1966). Supreme Court decision establishing the four-factor obviousness test referenced under § 103.

[9] amplifier-bundle-research repository and release notes. https://github.com/michaeljabbour/amplifier-bundle-research . v0.2.0 (commit `fc8ba42`, Apr 22 2026); v0.4.0 (commit `d528196`, Apr 22 2026). Release notes cite the verification and simulated-persona acceptance passes referenced in the Evidence section.

[10] K-Dense AI. *scientific-agent-skills* repository. https://github.com/K-Dense-AI/scientific-agent-skills . Upstream source of the pre-registration, peer-review, and scholar-evaluation skill primitives the bundle's agents wrap.

[11] PaperBanana methodology reference. arXiv:2601.23265. Cited for the figure-generation subsystem absorbed into the bundle's `figure-designer` agent.

---

## Appendices (available alongside this paper)

**Appendix A — Reproducible session artifacts.** The full session directory produced by the `/question` → `/publish` run that authored this paper, including sharpened_question YAML, preregistration YAML, evidence log YAML, critique YAML, and this draft. Path (in the bundle's own repository): `output/whitepaper-run/`.

**Appendix B — Patent-prereg template.** `templates/patent-prereg.yaml` — the attorney-facing pre-registration skeleton the bundle populates during `/study-plan`.

**Appendix C — USPTO venue format specification.** `context/venue-formats/uspto.md` — the 37 CFR 1.52 compliance specification the `venue-formatter` agent applies at `/publish`.
