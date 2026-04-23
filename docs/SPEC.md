# Specification — amplifier-bundle-research

**Status:** `v0.2.0` — fully specified and implemented, pre-functional-test
**Author:** Michael Jabbour
**Target ecosystem:** Microsoft Amplifier

---

## 1. Purpose

Give anyone who needs to produce a defensible written artifact the same disciplined workflow a trained researcher uses — without requiring the training.

The bundle does not write papers autonomously. It keeps the human in the driver's seat and prevents sloppy reasoning at each step: fuzzy questions, motivated-reasoning methodology, cherry-picked results, overclaiming, sloppy citations, wrong venue format.

## 2. Scope

### In scope

Any artifact where a reader asks "is this claim defensible?" and the author needs to answer yes. Concretely:

- Patent briefs and invention disclosures
- Evidence-based policy briefs
- Technical white papers
- Due-diligence and market-analysis reports
- Literature reviews
- Conference and workshop papers
- Journal articles
- Grant applications
- Replication studies

### Out of scope

- Creative writing (use `amplifier-bundle-stories`)
- Code-first engineering work (use `amplifier-bundle-superpowers`)
- Real-time experimental operation (the bundle drafts the plan and analyzes the results; a human or a separate pipeline runs the experiment)
- Fully autonomous paper generation (see Denario; explicit non-goal here)

## 3. Design principles

**Human-led, rigor-enforced.** Denario aims for AI as primary author. This bundle aims for humans as primary author, with AI as the methodology coach and honest critic. The human makes every substantive call; the bundle refuses to let them skip a step.

**Rigor is discoverable, not required.** Modes default to the rigorous path. A user who wants to skip pre-registration can. The bundle will label the resulting output as exploratory rather than confirmatory and carry that label through to the draft.

**One install, zero config.** Matches `amplifier-bundle-stories`: `amplifier bundle add` then `amplifier bundle use`. No API keys beyond Amplifier's existing provider config. Default templates cover the 80% case.

**Output ladder, not monoculture.** Same scaffolding — question, plan, execute, critique, draft, publish — produces a 2-page patent brief or a 12-page Nature submission. The recipe picks the output shape; the discipline stays constant.

**Skills stay lazy.** The 10 K-Dense skills are registered but unloaded. Modes pull them on demand. No context tax for browsing or for projects that only need a subset.

**Thin wrappers, upstream owns the content.** Agents are ~30 lines each, referencing K-Dense skill files by path. The skill library stays a single source of truth. Following the [ramparte/amplifier-collection-superpowers](https://github.com/ramparte/amplifier-collection-superpowers) pattern.

## 4. Personas

Three users with different starting points and the same destination — a defensible written artifact.

### Persona A: The non-scientist

Patent attorney, policy analyst, product manager, technical founder, journalist, due-diligence analyst. Has a claim to defend. Has never written IMRAD. Doesn't know what a p-value does or doesn't mean. Needs the bundle to translate ordinary intent into rigorous scaffolding without condescending.

### Persona B: The working researcher

ML researcher writing a workshop paper. PI drafting a grant. Engineer writing a technical report. Knows IMRAD, has strong intuitions, wants Superpowers-style discipline enforcement so their own shortcuts don't leak through. Treats the bundle as a rigor co-pilot.

### Persona C: The research-adjacent reviewer

Due-diligence partner, policy adviser, standards editor, patent examiner. Doesn't generate claims — evaluates them. Uses the `/critique` mode standalone against incoming artifacts and the `scholar-evaluation` agent as a structured scorer.

Full persona detail in [`PERSONAS.md`](PERSONAS.md).

## 5. The output ladder

| Output | Target length | Recipe | Primary mode sequence |
|---|---|---|---|
| Patent brief | 2–5 pages | `patent-brief` | question → plan → execute (prior-art) → critique → draft → publish |
| Policy brief | 2–8 pages | `policy-brief` | question → plan → execute (evidence gather) → critique → draft → publish |
| White paper | 6–20 pages | `white-paper` | full sequence, heavier draft phase |
| Literature review | 8–25 pages | `lit-review` | question → execute (systematic search) → critique → draft → publish |
| Workshop / conference paper | 4–10 pages | `empirical-paper` | full sequence with pre-registered experiments |
| Journal article | 10–30+ pages | `empirical-paper` with `--long` | full sequence with multi-round critique |
| Grant application | venue-specific | `grant` | question → plan → critique → draft → publish |
| Replication study | 6–15 pages | `replication-study` | starts at plan (question comes from source paper) |

All recipes compose from the same six modes and the same eight agents. Only the templates, venue configs, and critique emphasis differ.

## 6. Modes

Six modes, fixed names, stable contract. Each mode has clear inputs, outputs, and agents invoked. The CLI vocabulary is plain English so non-scientists get it immediately.

| Mode | Inputs | Outputs | Primary agents |
|---|---|---|---|
| `/question` | A rough claim or topic in the user's own words | A sharpened, falsifiable, operationalized question with success criteria | `hypothesis-designer`, `methodologist` |
| `/plan` | The sharpened question | A locked pre-registration artifact (YAML + human-readable summary) with methodology, predictions, analysis plan, and the honest-pivot clause | `methodologist`, `statistician`, `preregistration-reviewer` |
| `/execute` | The pre-registration and any raw materials (code, data, corpus, prior art seeds) | Results, figures, prior-art table, or evidence list — depending on recipe | `statistician`, `figure-designer`; recipe-specific tools |
| `/critique` | The results or the draft | A structured critique: confirmatory vs exploratory separation, named limitations, overclaim flags, scholar-eval scores | `honest-critic` |
| `/draft` | Pre-registration + results + critique | The artifact in the right structure: IMRAD, patent-brief skeleton, policy-brief skeleton, etc. | `technical-writer`, `figure-designer`, `venue-formatter` |
| `/publish` | The draft + target venue | Venue-ready output: LaTeX with correct preamble, DOCX with citations, or plain markdown brief | `venue-formatter` |

Each mode has a full definition in `modes/*.md`. The mode files are agent prompts, not code.

## 7. Agents

Eight thin wrappers over K-Dense skills. Each agent is a ~30-line `AGENT.md` that references the skill it wraps and sets the agent's role, tone, and output contract.

| Agent | Wraps | Role |
|---|---|---|
| `hypothesis-designer` | `hypothesis-generation` | Turn rough claims into falsifiable, operationalized questions with predictions and mechanisms |
| `methodologist` | `scientific-critical-thinking` | Design methodology, flag bias risks, reference GRADE / Cochrane ROB / CONSORT / STROBE / PRISMA where relevant |
| `preregistration-reviewer` | `scientific-critical-thinking` | Review the pre-registration before data is seen. Confirm predictions, stat tests, MDEs, and analysis plan are specific enough to be falsifiable |
| `statistician` | `statistical-analysis` | Test selection, assumption checking, power analysis, APA-formatted reporting |
| `honest-critic` | `peer-review` + `scholar-evaluation` | Structured critique with CONSORT/STROBE/PRISMA checklists + quantitative scoring. Defaults to skeptical |
| `technical-writer` | `scientific-writing` | IMRAD and non-IMRAD structures. Two-stage outline → prose |
| `figure-designer` | `scientific-schematics` | Publication-quality diagrams and charts |
| `venue-formatter` | `venue-templates` + `citation-management` | LaTeX/DOCX venue output with proper bibliography |

Full agent manifests in `agents/*.md`. See `agents/hypothesis-designer.md` for the canonical thin-wrapper pattern.

## 8. Skill layer

The bundle does not reimplement scientific skills. It wraps [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) as the single source of truth. The 10 skills used:

```
hypothesis-generation       scientific-critical-thinking
scientific-brainstorming    statistical-analysis
peer-review                 scholar-evaluation
scientific-writing          scientific-schematics
citation-management         venue-templates
```

Skills are registered at bundle install and loaded by agents on demand via `load_skill()`. The remaining 124 K-Dense skills are available but not registered — researchers in a specific domain (genomics, chemistry, astrophysics) can add them explicitly.

## 9. Behaviors

Two behaviors run silently across every mode:

**`honest-pivot`** — If the analysis diverges from the pre-registered predictions, the bundle surfaces this explicitly and marks the deviation in the draft. No quiet rewriting of the hypothesis after results are in.

**`exploratory-labeling`** — Any finding that wasn't in the pre-registration gets tagged `exploratory` and carries that label through to the draft's Results section and the publish-phase formatting.

Both are on by default. Both can be disabled explicitly (with a visible warning) for users who know what they're doing.

## 10. Recipes

Recipes are YAML files that compose modes, set defaults, and bind the output template. A minimal recipe:

```yaml
name: patent-brief
description: USPTO-style invention disclosure with prior-art section
modes: [question, plan, execute, critique, draft, publish]
defaults:
  template: templates/patent-brief-skeleton.md
  venue: uspto
  critique_emphasis: [novelty, enablement, prior-art-coverage]
  honest_pivot: true
```

Recipes ship for every output-ladder entry in §5. Users can copy and edit them without touching the bundle.

## 11. Install and UX contract

**The contract:** install is one command, first run is one mode, zero YAML edits required. This is the `amplifier-bundle-stories` bar.

Installation:

```bash
amplifier bundle add --app git+https://github.com/michaeljabbour/amplifier-bundle-research@main
amplifier bundle use research
```

First run options:

```bash
# Interactive — start at /question
amplifier

# Recipe-driven — hand it an intent, get a finished artifact
amplifier run --recipe patent-brief "Rolling-ROI control for AI agent sessions"

# Mode-specific — e.g., critique an incoming document
amplifier run --mode critique --input incoming-claim.md
```

Full UX transcript in [`UX_MOCKUP.md`](UX_MOCKUP.md).

## 12. Non-goals

- **Not a Denario replacement.** Denario targets autonomous end-to-end paper generation, with the human as optional editor. This bundle explicitly keeps the human as primary author.
- **Not a domain-science toolkit.** The bundle provides the research scaffolding. Domain-specific tools (protein folding, molecular dynamics, cosmology) stay in K-Dense's larger skill set and are opt-in.
- **Not a LaTeX IDE.** Venue formatting is the final step, not the focus. The core value is the discipline upstream of formatting.
- **Not a plagiarism checker or IP-clearance tool.** Prior-art search in `/execute` surfaces candidate references; legal clearance remains a human call.

## 13. Evaluation

The bundle ships with its own eval target: the RCE (Reflection Capability Evaluation) benchmark. A successful `v1.0` release means:

- Persona A produces a patent brief that a patent attorney rates ≥ 4/5 on defensibility
- Persona B produces a workshop paper that passes the bundle's own `/critique` at ≥ 80% on CONSORT/STROBE-relevant items
- Persona C can run `/critique` standalone against an incoming document and produce feedback rated ≥ "useful and correct" by ≥ 70% of reviewers

The first paper this bundle produces should be the paper *about this bundle*, evaluated against these targets. Dogfooding is the proof.

## 14. Roadmap

See [`ROADMAP.md`](ROADMAP.md). Short version:

- **v0.1** (now) — Spec, skeleton, 3 recipes fully working (patent-brief, policy-brief, empirical-paper)
- **v0.2** — All recipes, all modes, RCE eval harness
- **v0.3** — Venue pack (ICML, NeurIPS, Nature, USPTO, federal policy)
- **v1.0** — RCE-validated, dogfooded paper published, public release

## 15. Open questions

- Should `/execute` for non-empirical recipes (patent-brief, policy-brief) always invoke a prior-art / evidence-gather sub-agent, or should that be a separate mode? Current answer: same mode, recipe-parameterized. Worth revisiting after first user tests.
- How much of the K-Dense skill set should be registered vs opt-in? Current answer: 10 registered, 124 opt-in. Domain researchers will push for more.
- Should behaviors be enforceable at the publish step (refuse to ship a draft that violates `honest-pivot`)? Current answer: warn, don't block. Users get final call.
