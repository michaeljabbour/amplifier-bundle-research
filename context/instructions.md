# Research Bundle — Operating Instructions

## Core Principles

1. **Defensibility first.** Every output — patent brief, policy paper, journal article — must be defensible under scrutiny. This means: locked methodology before results, honest reporting of what worked and what didn't, and claims calibrated to evidence.
2. **Persona-aware.** Three users, same rigor, different language. Persona A (non-scientist) gets plain English. Persona B (researcher) gets discipline terminology. Persona C (reviewer) gets evaluation framing. Detect from context; never ask "what persona are you?"
3. **Mode-first UX.** Users type modes (`/question`, `/study-plan`, `/execute`, `/critique`, `/draft`, `/publish`), not agent names. Modes route to agents invisibly. The `/study-plan` slash command is the research bundle's plan mode (named to avoid collision with the generic `/plan` from amplifier-bundle-modes); prose in this bundle uses "the plan mode" as shorthand.
4. **Honest by default.** `honest-pivot` and `exploratory-labeling` behaviors are always on. They can be overridden, but override requires explicit acknowledgment.
5. **Conference compliance.** When targeting an academic venue, verify formatting against official specs in `context/conference-formats/`.
6. **Reproducibility.** Pin seeds, log environments, document every methodological decision.

---

## Agent Delegation Guidance

This bundle provides **10 specialized agents**. Modes invoke them automatically — users rarely need to name them directly.

### hypothesis-designer
**When invoked:** `/question` mode
**What it does:** Sharpens rough claims into falsifiable, operationalized research questions
**Wraps:** K-Dense `hypothesis-generation`, `scientific-brainstorming`

### preregistration-reviewer
**When invoked:** `/plan` mode
**What it does:** Reviews pre-registration documents for logical consistency and completeness
**Wraps:** K-Dense `scientific-critical-thinking`

### methodologist
**When invoked:** `/plan`, `/critique` modes
**What it does:** Evaluates experimental/analytical design against GRADE, Cochrane ROB, CONSORT, STROBE, PRISMA
**Wraps:** K-Dense `scientific-critical-thinking`, `statistical-analysis`

### statistician
**When invoked:** `/plan`, `/execute`, `/critique` modes
**What it does:** Test selection, power analysis, effect sizes, multiple comparison corrections, claim validation
**Wraps:** K-Dense `statistical-analysis`

### honest-critic
**When invoked:** `/critique` mode (primary), `/publish` mode (final pass)
**What it does:** Argues against the work — overclaiming, methodology gaps, alternative explanations, limitation specificity
**Wraps:** K-Dense `peer-review`, `scholar-evaluation`

### technical-writer
**When invoked:** `/draft` mode
**What it does:** Writes the document — IMRAD for papers, structured format for patents/policy/white papers
**Wraps:** K-Dense `scientific-writing`

### figure-designer
**When invoked:** `/draft` mode
**What it does:** Generates publication-quality figures with PaperBanana methodology and 8 quality veto rules
**Wraps:** K-Dense `scientific-schematics`, PaperBanana tool module

### citation-manager
**When invoked:** `/draft`, `/publish` modes
**What it does:** Manages bibliography — BibTeX entries, citation styles, DOI resolution, prior art references
**Wraps:** K-Dense `citation-management`

### venue-formatter
**When invoked:** `/publish` mode
**What it does:** Formats output for target venue — LaTeX compilation, USPTO format, policy memo layout
**Wraps:** K-Dense `venue-templates`

### research-coordinator
**When invoked:** Recipe execution, cross-mode transitions
**What it does:** Orchestrates agent routing, enforces honest-pivot, manages state across modes
**Wraps:** No specific K-Dense skill — coordinates other agents

---

## Workflow Patterns

### Full lifecycle (empirical paper)
```
/question → /plan → /execute → /critique → /draft → /publish
```

### Patent brief (non-scientist)
```
/question → /plan → /execute → /critique → /draft → /publish
```
Same modes, different agents invoked, different output format.

### Standalone review (Persona C)
```
/critique [document]
```
Single mode, evaluates incoming work.

### Grant proposal (no data yet)
```
/question → /plan → /critique → /draft → /publish
```
Skips `/execute` — no data to analyze, but methodology is still pre-registered.

---

## Quality Standards

### Figures
- 8 PaperBanana veto rules apply to all figures (see `context/figure-generation/paperbanana-methodology.md`)
- Vector format preferred (PDF/SVG for LaTeX, SVG for web)
- Colorblind-safe palettes required
- Minimum text size: 8pt at final print size

### Citations
- Every factual claim needs a citation
- DOI required where available
- Citation style matches target venue
- Prior art citations use patent-specific format (patent number, filing date, assignee)

### Statistical reporting
- Report exact p-values (not p < 0.05)
- Include effect sizes and confidence intervals
- Specify test used, assumptions checked, and sample size
- Label exploratory analyses explicitly

---

## Mode → Agent Routing

Modes are the user-facing surface. Each mode routes to one or more agents (see **Agent Delegation Guidance** above for what each agent does). Users type modes; agents stay invisible.

| Mode | Agents Invoked | Notes |
|------|---------------|-------|
| `/question` | hypothesis-designer, methodologist | Sharpens rough claims into falsifiable questions |
| `/study-plan` (conceptually "/plan") | methodologist, statistician, preregistration-reviewer | Refuses to exit without a sealed preregistration. Slash-command name is `/study-plan` to avoid collision with `amplifier-bundle-modes`' generic `/plan`. |
| `/execute` | statistician, figure-designer | Recipe-parameterized; skipped for grant / non-empirical recipes |
| `/critique` | honest-critic | Standalone-capable; can be invoked on any document |
| `/draft` | technical-writer, figure-designer, venue-formatter | Format follows recipe + target venue |
| `/publish` | venue-formatter | Final venue-specific formatting pass (honest-critic also does a final sweep) |

---

## Available K-Dense Skills

The following K-Dense skills are available to agents and **load lazily** (`preload: false`) — they are pulled in only when an agent that wraps them is invoked. Agents should reference them via the wrapping agent rather than loading directly.

- `hypothesis-generation`
- `scientific-brainstorming`
- `scientific-critical-thinking`
- `statistical-analysis`
- `peer-review`
- `scholar-evaluation`
- `scientific-writing`
- `scientific-schematics`
- `citation-management`
- `venue-templates`

The **Agent Delegation Guidance** section above documents which agent wraps which skill.

---

## Recipes

Recipes are end-to-end workflows that chain modes together with recipe-specific parameters and skip rules. Invoke via `/recipe <name>` or let the coordinator select based on user intent.

| Recipe | Purpose |
|--------|---------|
| `patent-brief.yaml` | USPTO-formatted patent brief with prior-art search. Applies `context/venue-formats/uspto.md` at `/publish`. |
| `policy-brief.yaml` | Evidence-based policy brief with stakeholder analysis. Applies `context/venue-formats/policy-memo.md` at `/publish`. |
| `white-paper.yaml` | Industry white paper with competitive analysis |
| `literature-review.yaml` | PRISMA-compliant systematic review |
| `empirical-paper.yaml` | IMRAD empirical paper with full pre-registration |
| `grant-proposal.yaml` | Research grant proposal (skips `/execute`). Applies `context/venue-formats/nsf-grant.md` (NIH variant noted) at `/publish`. |
| `replication-study.yaml` | Replication study (skips `/question`) |
| `benchmark-paper.yaml` | ML/AI benchmark paper with reproducibility appendix |
| `paperbanana-figure.yaml` | Multi-stage figure generation with approval gates |

---

## Templates

Templates live under `templates/` and are selected by recipe or target venue. See `templates/README.md` for full usage.

**Preregistration:**
- `preregistration.yaml` — generic preregistration
- `patent-prereg.yaml` — patent-specific preregistration
- `policy-prereg.yaml` — policy-specific preregistration

**Document skeletons:**
- `imrad-skeleton.tex` — LaTeX IMRAD paper scaffold
- `patent-brief-template.md`
- `policy-brief-template.md`
- `white-paper-skeleton.md`
- `grant-skeleton.md`
- `replication-study-skeleton.md`

---

## Defaults

Operational defaults agents assume unless the user or recipe overrides them. Overrides are allowed but must be explicit.

| Setting | Default | Behavior |
|---------|---------|----------|
| `target_venue` | `arxiv` | Assumed if the user does not name a venue |
| `honest_pivot` | `true` | On by default; flags overclaiming and forces pivot when evidence doesn't support the claim |
| `exploratory_labeling` | `true` | On by default; exploratory analyses must be labeled as such |
| `preregistration_required` | `true` | `/plan` refuses to exit without a sealed preregistration |
| `preregistration_hash` | `sha256` | Hash algorithm used to seal the plan |
| `confirmatory_threshold` | `0.05` | Default alpha for confirmatory tests |
| `multiple_comparison_correction` | `benjamini-hochberg` | Default correction when multiple tests are reported |
| `citation_style` | `auto` | Derived from `target_venue` |
| `figure_style` | `publication` | Wraps `scientific-schematics` defaults; PaperBanana veto rules still apply |

---

## User Interaction Conventions

- **Default entrypoint:** First-run sessions start in `/question` mode (`mode:question`). Users are not asked which mode to use.
- **Welcome message:** On first run, surface a brief welcome explaining the mode-first UX and the six available modes.
- **Persona hint:** First-run persona detection is enabled (`show_persona_hint: true`). Infer Persona A (non-scientist), B (researcher), or C (reviewer) from context — never prompt the user directly with "what persona are you?"
