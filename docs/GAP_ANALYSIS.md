# Gap Analysis — `amplifier-bundle-scientificpaper` → `amplifier-bundle-research`

**Source studied:** `~/dev/amplifier-bundle-scientificpaper` (v1.0.0, 853 files, ~20K lines of content)
**Date:** 2026-04-22
**Scope:** What to absorb from the earlier bundle into the new one.

---

## Executive summary

The earlier bundle (`scientificpaper`) is a real, well-constructed piece of work focused tightly on the academic-paper production end of the lifecycle. It complements `research` rather than overlapping with it:

- `scientificpaper` is strong where `research` is thin: **writing, figures, LaTeX, conference formatting**.
- `research` is strong where `scientificpaper` is absent: **pre-registration, honest critique, methodology discipline, non-scientist UX, patent/policy outputs**.

The merge strategy is **absorb the content, keep the frame.** We import `scientificpaper`'s craft material (conference specs, PaperBanana methodology, writing-style guidance, Python scripts) into `research`'s architectural shell (modes, personas, honest-pivot, output ladder). Neither bundle survives alone as well as the merged result.

---

## What `scientificpaper` has that `research` should absorb

### High priority — merge into v0.2

**1. PaperBanana figure methodology.** A published, benchmarked (arXiv 2601.23265) multi-agent approach to figure generation: Retriever → Planner → Stylist → Visualizer → Critic, with 8 veto rules (no low-quality artifacts, professional colors, no black backgrounds, modern style, vector preferred, appropriate aspect ratio, clear labels, data integrity). Ships with ~600 lines of Python implementing the full pipeline (`tool-paperbanana/`).

**Action:** Absorb the methodology into our `figure-designer` agent. Ship the Python module as an optional sub-bundle (`bundles/with-paperbanana.md` variant) rather than a hard dependency — our "pure configuration" principle bends but doesn't break, since the module is genuinely useful and self-contained.

**2. Six conference format specifications.** ~2700 lines of reference material covering NeurIPS, ICML, ACL, IEEE, ACM, arXiv — column widths, page limits, font requirements, citation styles, submission checklists. Already written, already accurate.

**Action:** Drop verbatim into `references/conference-formats/`. Lazy-load via `venue-formatter` agent. This is free mass to absorb.

**3. The paper-architect agent's writing-craft content.** 872 lines including:
- 5-component abstract framework (Background → Gap → Approach → Results → Implications)
- Section flow principles with paragraph-level guidance
- Active-voice enforcement and weak-phrase detection
- Precision-in-claims patterns
- IMRaD variants for different paper types (empirical / theoretical / survey / benchmark)
- Revision workflows for reviewer feedback

**Action:** Expand our `technical-writer` agent to incorporate this. Our current agent is a 30-line stub; the merged version should be ~300 lines — still thinner than theirs (we don't need every paragraph), but comprehensive.

**4. The matplotlib-scientific + TikZ reference material.** 1700+ lines in `context/imaging/` covering matplotlib patterns for scientific plotting, tikzplotlib conversion, TikZ/PGFPlots for mathematical diagrams, colorblind palettes.

**Action:** Drop into `references/imaging/`. Lazy-loaded by `figure-designer` when a figure task fires.

**5. Approval-gate pattern in recipes.** Their `paperbanana-figure.yaml` uses `approval_required: true` with a human-readable `approval_prompt` at stage boundaries. This is the pattern `honest-pivot` should manifest as in recipe-level orchestration — we had it as a behavior, they have it as a recipe primitive. Both levels matter.

**Action:** Add `approval_required` and `approval_prompt` fields to our recipe schema. Update `recipes/empirical-paper.yaml` and `recipes/patent-brief.yaml` to use them at mode boundaries.

**6. Python scripts for deterministic operations.** Four working scripts: `compile_latex.py` (multi-format LaTeX compilation with error diagnosis), `validate_format.py`, `generate_figure.py`, `download_templates.py`.

**Action:** Absorb into `scripts/`. These make `/publish` robust — LaTeX compilation is one place where shell-out-to-a-known-good-script beats LLM reasoning every time. Bends the "pure config" principle by ~200 lines of Python; worth it.

### Medium priority — v0.3

**7. Split `citation-manager` out as a standalone agent.** Their 1123-line citation-manager is cleaner than our current design where citation lives inside `venue-formatter`. BibTeX entry creation from DOIs, citation style conversion (numeric ↔ author-year), duplicate detection, cross-reference validation are enough surface area to warrant a dedicated agent.

**Action:** Split `venue-formatter` into `venue-formatter` + `citation-manager`. Update `bundle.md` to register nine agents, not eight.

**8. Bundle variants.** They list `bundles/with-gemini.md`, `bundles/latex-only.md`, `bundles/neurips-focused.md`. This is a clean pattern for letting users pick compositions without editing the root `bundle.md`.

**Action:** Add `bundles/` directory to our structure. Initial variants: `with-paperbanana.md`, `latex-only.md`, `non-scientist.md` (default on, turns off pre-registration jargon and tightens persona-A behavior).

**9. `Use PROACTIVELY when:` agent-trigger blocks.** Their agent frontmatter has explicit trigger lists (10+ specific conditions) that help Amplifier's routing pick the right agent. Our current agents don't have this.

**Action:** Add `proactively_when:` block to each of our eight agent manifests.

### Low priority / deliberately skip

**10. Their positioning as "scientific paper" bundle.** This is exactly what we're not doing. Our `research` frame keeps the patent-brief, policy-brief, and white-paper use cases alive. Absorb content, not positioning.

**11. Their monolithic agent triggers.** Theirs uses agent-selection-by-keyword (`"if user says X, route to agent Y"`); ours uses mode-first (`/question`, `/plan`, etc.) with agents behind modes. Keep ours — non-scientists benefit from the mode vocabulary.

**12. Their assumption of researcher audience.** `scientificpaper`'s tone and examples assume the user knows what IMRaD means. We keep persona-A framing throughout.

---

## What `research` has that `scientificpaper` doesn't

Recording this for completeness — these are the things we keep and don't touch:

1. **Pre-registration discipline.** Hash-locked preregistration.yaml. `honest-pivot` and `exploratory-labeling` behaviors. Core differentiator.
2. **Output ladder.** Patent briefs, policy briefs, white papers, literature reviews, replication studies, grants. `scientificpaper` is papers-only.
3. **Three-persona framing.** Non-scientist / researcher / reviewer, with tone-switching. `scientificpaper` assumes researcher throughout.
4. **Mode-based UX.** `/question /plan /execute /critique /draft /publish`. `scientificpaper` has no mode layer.
5. **Methodology critique.** GRADE / Cochrane ROB / CONSORT / STROBE / PRISMA references. `scientificpaper`'s critique is structural-only.
6. **Scholar-evaluation scoring.** Quantitative rigor dimensions. Not in `scientificpaper`.
7. **Replication-study recipe.** Explicit support for reproducing prior work. Not in `scientificpaper`.
8. **Standalone `/critique` for Persona C.** Due-diligence and reviewer use cases. Not in `scientificpaper`.

---

## Merge plan

### v0.1.1 (now) — surgical absorptions

Low-cost, high-value additions that fit within the current spec:

- Add `references/conference-formats/` with the six format specs (verbatim copy, credit `scientificpaper`)
- Add `references/imaging/` with matplotlib-scientific + TikZ patterns
- Add `scripts/compile_latex.py` and `scripts/validate_format.py`
- Expand `agents/technical-writer.md` from stub to ~300 lines with paper-architect's writing-craft content
- Expand `agents/figure-designer.md` from stub to reference PaperBanana methodology
- Add `proactively_when:` blocks to all agent frontmatter
- Update `docs/LINEAGE.md` to credit the earlier bundle

### v0.2.0 — structural changes

- Split `venue-formatter` → `venue-formatter` + `citation-manager` (9 agents total)
- Add `bundles/` with three variants (`with-paperbanana`, `latex-only`, `non-scientist`)
- Add `approval_required` / `approval_prompt` to recipe schema
- Update all recipes to use approval gates at mode boundaries

### v0.3.0 — optional sub-modules

- Absorb `tool-paperbanana/` as the canonical figure generator for the `with-paperbanana` variant
- Keep as opt-in: core bundle stays pure-config; variant adds the Python module
- Expand Python scripts set based on what `/publish` + `/execute` actually need

---

## What I'm *not* doing

1. **Not absorbing the whole bundle verbatim.** Some of their content is specifically ML-paper-shaped (PlotNeuralNet for neural-network diagrams, ICML column widths as implicit defaults). Our bundle's broader scope means we pick cherries, not branches.

2. **Not reframing as "scientificpaper."** The `research` name is doing real work — it's what lets a patent attorney, policy analyst, or due-diligence partner see themselves in the bundle. A `scientificpaper` bundle can live alongside as a specialized variant; it shouldn't displace the broader framing.

3. **Not deleting our pre-registration discipline.** This is the bundle's core value. `scientificpaper` doesn't have it and doesn't need to — it targets a different problem. We keep it.

4. **Not changing the mode layer.** Their agent-triggered routing is fine for working researchers but opaque to Persona A. Modes stay.

---

## One-sentence summary per file category

| Their file | What to do |
|---|---|
| `README.md`, `QUICK_START.md` | Study tone; our README already matches stories-bar. No change needed. |
| `bundle.md` | Different schema (YAML frontmatter + markdown body). Ours is cleaner. Keep ours. |
| `docs/development/ARCHITECTURE.md` | Absorb the "context sink" terminology; our ARCHITECTURE.md is otherwise more complete. |
| `agents/paper-architect.md` | Mine for `technical-writer` content (not full verbatim; cherry-pick). |
| `agents/figure-artist.md` | Mine for `figure-designer` content + PaperBanana reference. |
| `agents/latex-expert.md` | Mine for `venue-formatter` content; LaTeX error diagnosis is useful. |
| `agents/citation-manager.md` | Absorb wholesale as new agent. |
| `behaviors/*.md` | Theirs are thin YAML bundle definitions; our behavior docs are thicker and better-shaped. Keep ours. |
| `context/conference-formats/*.md` | Drop into `references/conference-formats/` verbatim with credit. |
| `context/imaging/*.md` | Drop into `references/imaging/` verbatim with credit. |
| `context/paperbanana-methodology.md` | Drop into `references/figure-generation/paperbanana.md` verbatim with credit. |
| `templates/ieee/`, `templates/acl/` | Drop into `templates/venues/` — real LaTeX files are free mass. |
| `scripts/*.py` | Absorb into `scripts/`. |
| `modules/tool-paperbanana/` | Hold for v0.3 as the `with-paperbanana` variant. |
| `recipes/paperbanana-figure.yaml` | Study the approval-gate pattern; adapt for our recipes. |

---

## Honest verdict

Your earlier `scientificpaper` bundle is substantially *more implemented* than our current `research` skeleton — 20K lines of real content vs. our 130KB of spec + stubs. The gap in our favor is architectural: we have the right shape (modes, personas, output ladder, pre-registration discipline) but little content. Theirs has the content but a narrower shape.

The merge produces something better than either: our architectural clarity and rigor discipline, stocked with their craft material. I'd estimate absorbing the high-priority items above gets us from `v0.1` stub quality to something closer to `v0.3` working quality with about a day of focused work.
