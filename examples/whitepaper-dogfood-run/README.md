# Dogfood Run — White Paper on the Bundle, Written with the Bundle

**Recipe:** `white-paper.yaml`
**Audience:** Patent attorneys (Persona A)
**Bundle version at run time:** v0.4.0 (commit `d528196`)
**Run date:** 2026-04-23
**Session id:** `e623279d-44ef-458d-b7b7-ddc8f73e105c`

This directory captures a full end-to-end run of the research bundle
producing a white paper about the research bundle itself. It is the
first dogfood artifact against the v1.0 milestone named in
[`docs/HANDOFF.md`](../../docs/HANDOFF.md): *"paper about this bundle,
written with this bundle."*

## What to read first

| File | Role | What it demonstrates |
|---|---|---|
| [`06-whitepaper-v2.pdf`](06-whitepaper-v2.pdf) | **The final artifact** | 16-page LaTeX-compiled white paper with four embedded DOT diagrams, natbib references, compiled via `pdflatex`. |
| [`05-draft.tex`](05-draft.tex) | LaTeX source | Plain `article` class; honors every BLOCK finding from the /critique pass; stop-slop-clean. |
| [`05-draft.md`](05-draft.md) | Markdown draft (v1) | First-pass Markdown version produced before the LaTeX rewrite. Preserved for comparison. |
| [`06-whitepaper.pdf`](06-whitepaper.pdf) | Markdown→pandoc PDF (v1) | 16 pages from the Markdown draft via `pandoc --pdf-engine=xelatex`. Preserved for contrast with the LaTeX-authored v2. |

## The mode chain (what the pipeline actually ran)

| Mode | Artifact | Agents invoked | What the bundle caught or produced |
|---|---|---|---|
| `/question` | [`01-question.yaml`](01-question.yaml) | hypothesis-designer | Sharpened rough thesis into four falsifiable predictions (P1–P4) with disconfirmation criteria and a four-class novelty note. |
| `/study-plan` | [`02-study-plan.yaml`](02-study-plan.yaml) | methodologist, preregistration-reviewer, statistician | Hash-locked the evidence plan, competitive-comparator rules, baselines, draft constraints, abandonment criteria, honest-pivot clause. |
| `/execute` | [`03-execute-evidence-log.yaml`](03-execute-evidence-log.yaml) | research-coordinator, statistician | Gathered four evidence classes (discipline gap, competitive, case studies, risks) and bundle-internal facts. Logged one honest-pivot softening P4 from comparative to operational claim. |
| `/critique` (pass 1) | [`04-critique.yaml`](04-critique.yaml) | honest-critic | Produced 14 findings: **4 BLOCK**, **6 WARN**, **4 NOTE**, plus 4 named alternative explanations. Verdict: `CONDITIONAL_PROCEED`. |
| `/critique` (pass 2, stop-slop) | [`04b-critique-v2-stop-slop.yaml`](04b-critique-v2-stop-slop.yaml) | honest-critic + [`stop-slop` behavior](../../behaviors/stop-slop.md) | Grep-swept the LaTeX draft for AI-tell patterns. Zero rendering em-dashes, zero adverb crutches, zero throat-clearing openers, zero binary contrasts, zero vague declaratives. Three NOTE-severity items logged (three-item list density, calibrated use of "significant", rhythm in exec summary). (The artifact YAML references the skill form that was later migrated to a behavior; see capability-migration note below.) |
| `/draft` | [`05-draft.tex`](05-draft.tex) and [`05-draft.md`](05-draft.md) | technical-writer, figure-designer, citation-manager | LaTeX `article`-class draft honoring every BLOCK resolution: first-person capability disclosure in front matter, no comparative-time claims, L1 "no real-attorney validation" as headline limitation, mechanism-specific language replacing "same as scientists" framing, four named alternative explanations. |
| `/publish` | [`06-whitepaper-v2.pdf`](06-whitepaper-v2.pdf) | venue-formatter | Two-pass `pdflatex` compile. All publish gates pass (critique_required PASS, honest_pivot_acknowledged PASS, thesis_clarity PASS, overclaim_detection PASS, competitive_analysis PASS; evidence_coverage WARN carried as exploratory label). |

## Capabilities exercised

### Bundle-native capabilities

- **Six-mode pipeline** (all six modes fired in order). See [`figures/fig-six-mode-pipeline.dot`](figures/fig-six-mode-pipeline.dot) for the topology diagram generated for the paper.
- **All ten specialist agents** routed through `research-coordinator`. See [`figures/fig-agent-composition.dot`](figures/fig-agent-composition.dot).
- **Hash-locked preregistration** committed before any evidence gathering. See the `seal:` block in `02-study-plan.yaml`.
- **Honest-pivot enforcement** surfaced a divergence between the prereg and the evidence log (P4 comparative-time claim softened to operational walkthrough). Logged in the `honest_pivots:` section of `03-execute-evidence-log.yaml`.
- **Structured /critique with severity labels** produced 14 findings across BLOCK / WARN / NOTE (`04-critique.yaml`).
- **Four publish-gate checks** fired and all passed.
- **Venue-aware drafting**: the LaTeX build uses the same typographic conventions as `templates/imrad-skeleton.tex`; the final compile could equally target `scripts/compile_latex.py --format arxiv` for the arXiv venue.

### Capabilities added during this run

- **`stop-slop` behavior** (gene transfer from [`hardikpandya/stop-slop`](https://github.com/hardikpandya/stop-slop), MIT-licensed). Lives at [`behaviors/stop-slop.md`](../../behaviors/stop-slop.md); default-on; never user-invocable. Fires silently during `/draft` and `/critique` to remove AI-tell patterns. The rule catalog lives at [`context/prose-quality/`](../../context/prose-quality/) and is loaded on demand when the behavior triggers.
- **Four DOT diagrams** authored for this paper and compiled to both PDF (embedded in LaTeX) and PNG (for web/readme previews). See [`figures/`](figures/).
- **Seven research-bundle-specific before/after rewrites** in [`context/prose-quality/examples.md`](../../context/prose-quality/examples.md), drawn from this paper's own drafts. Future `/critique` passes use them as ground-truth examples of what the bundle's prose sounds like in AI-tell-clean form.

> **Note on the skill→behavior migration.** The initial gene transfer landed stop-slop as a user-invocable skill at `.amplifier/skills/stop-slop/` (visible in commit `e07f3b2`). A subsequent design pass moved it to the behavior form above. The v2 LaTeX draft preserved in this sample was produced before that migration; the session artifact `04b-critique-v2-stop-slop.yaml` still references the skill form. Everything the draft shows the bundle doing is now done automatically by the behavior without the agent needing to `load_skill` anything.

## Diagrams

| File | What it shows |
|---|---|
| [`figures/fig-six-mode-pipeline.pdf`](figures/fig-six-mode-pipeline.pdf) | The six-mode pipeline with the artifact each mode commits to disk. |
| [`figures/fig-agent-composition.pdf`](figures/fig-agent-composition.pdf) | The ten specialist agents grouped by invoking mode; research-coordinator on top. |
| [`figures/fig-artifact-chain.pdf`](figures/fig-artifact-chain.pdf) | The YAML/MD artifact chain the session produced, with the sha256 seal node marking `/publish`-gate enforcement. |
| [`figures/fig-critique-severity-flow.pdf`](figures/fig-critique-severity-flow.pdf) | How BLOCK/WARN/NOTE findings route through the publish gate back to the draft. |

Each figure has a matching `.dot` source file; `.png` and `.pdf` variants are produced by `dot -Tpdf` and `dot -Tpng -Gdpi=150`.

## What this run proved and did not prove

**Proved (capability evidence):**
- The bundle's mode sequence runs end-to-end on a non-trivial topic (a capability white paper about the bundle itself) without manual glue.
- Every mode produces an inspectable artifact. The artifact chain is reproducible.
- `/critique` with `honest-critic` catches load-bearing weaknesses (vendor-author conflict, unsupported time-cost claim, author-only case studies, "same as scientists" overclaim) and enforces their resolution at the BLOCK level before `/draft` proceeds.
- `/publish` gates block correctly (`critique_required` was satisfied; `overclaim_detection` was satisfied; `honest_pivot_acknowledged` was satisfied).

**Did not prove (outcome evidence):**
- Whether a real patent attorney would find the white paper useful. This remains the bundle's v1.0 milestone.
- Whether the bundle's methodology scaffolding improves filed-application quality. No data; see the paper's limitations section.

## Reproducing this run

```bash
cd amplifier-bundle-research
amplifier bundle use research
amplifier run --recipe white-paper \
  "Produce a capability white paper about amplifier-bundle-research
   v0.4.0 for a patent-attorney audience. Honest-pivot on.
   Exploratory-labeling on. Acknowledge the v0.4 real-attorney-UX
   gap as the headline limitation."
```

The six mode-artifacts land in `.amplifier/sessions/<session-id>/` by default. To recompile the LaTeX only:

```bash
cd examples/whitepaper-dogfood-run
pdflatex 05-draft.tex && pdflatex 05-draft.tex   # two passes for cross-refs
```

To regenerate figures after editing a `.dot` source:

```bash
cd examples/whitepaper-dogfood-run/figures
for f in *.dot; do
  dot -Tpdf "$f" -o "${f%.dot}.pdf"
  dot -Tpng -Gdpi=150 "$f" -o "${f%.dot}.png"
done
```

## File inventory

```
examples/whitepaper-dogfood-run/
├── README.md                          (this file)
├── 01-question.yaml                   sharpened thesis + predictions
├── 02-study-plan.yaml                 hash-locked methodology
├── 03-execute-evidence-log.yaml       4 evidence classes + honest-pivot log
├── 04-critique.yaml                   first critique pass (4B/6W/4N)
├── 04b-critique-v2-stop-slop.yaml     second critique pass with stop-slop
├── 05-draft.md                        markdown draft (v1)
├── 05-draft.tex                       LaTeX draft (v2, current)
├── 06-whitepaper.pdf                  v1 pandoc-compiled PDF (16 pp)
├── 06-whitepaper-v2.pdf               v2 pdflatex-compiled PDF (16 pp)
└── figures/
    ├── fig-six-mode-pipeline.{dot,pdf,png}
    ├── fig-agent-composition.{dot,pdf,png}
    ├── fig-artifact-chain.{dot,pdf,png}
    └── fig-critique-severity-flow.{dot,pdf,png}
```

## Related

- Bundle topology at the repo scale: [`bundle.dot`](../../bundle.dot) / [`bundle.png`](../../bundle.png) (auto-generated; covers the whole bundle, not just this recipe).
- The v1.0 dogfood paper plan: [`docs/HANDOFF.md`](../../docs/HANDOFF.md).
- The `stop-slop` behavior this run introduced: [`behaviors/stop-slop.md`](../../behaviors/stop-slop.md) (current form) / rule catalogs at [`context/prose-quality/`](../../context/prose-quality/).
- Skill provenance: [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop) (MIT, adapted).
