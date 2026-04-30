---
bundle:
  name: research-behaviors
  version: 0.5.0
  description: |
    Composite behavior bundle. Packages all ten research-bundle behaviors
    (honest-pivot, exploratory-labeling, paperbanana, figure-generation,
    latex-authoring, conference-styling, research-modes, stop-slop,
    cache-only-verification, cross-vendor-judge) so that consumers can pull them
    in as a single unit, and so that research/bundle.md stays DRY by
    referencing this one file instead of each behavior individually.

includes:
  - bundle: research:behaviors/honest-pivot.md
  - bundle: research:behaviors/exploratory-labeling.md
  - bundle: research:behaviors/stop-slop.md
  - bundle: research:behaviors/paperbanana.md
  - bundle: research:behaviors/figure-generation.md
  - bundle: research:behaviors/latex-authoring.md
  - bundle: research:behaviors/conference-styling.md
  - bundle: research:behaviors/research-modes.md       # Registers /question, /study-plan, /execute, /critique, /draft, /publish as real slash commands
  # v0.8.0 additions (audit closure):
  - bundle: research:behaviors/cache-only-verification.md  # `--from-cache` committee-audit pattern
  - bundle: research:behaviors/cross-vendor-judge.md       # codifies provider_preferences class enforcement
---

# Research Behaviors (Composite)

This is the canonical entry point for consuming research-bundle behaviors
from any other bundle. Including `research:behaviors/research.md` transitively
pulls in all ten behaviors with their default configurations.

## What's included

| Behavior | Default | Purpose |
|----------|---------|---------|
| `honest-pivot` | on | Surfaces any deviation between pre-registered plan and final output |
| `exploratory-labeling` | on | Tags unpredicted findings as `[EXPLORATORY]` through to publish |
| `stop-slop` | on | Silent prose-discipline: removes AI-tell patterns (adverb piles, binary contrasts, em-dashes, false agency, throat-clearing openers) during /draft and /critique |
| `paperbanana` | on | PaperBanana multi-agent figure generation (8 quality veto rules) |
| `figure-generation` | on | Tool selection matrix for figures (matplotlib, TikZ, Mermaid, Imagen) |
| `latex-authoring` | on | LaTeX compilation, conference formatting, structural planning |
| `conference-styling` | on | Per-venue formatting (NeurIPS, ICML, ACL, IEEE, ACM, arXiv) |
| `research-modes` | on | Registers /question, /study-plan, /execute, /critique, /draft, /publish as real slash commands |
| `cache-only-verification` | opt-in | Committee-audit re-verification path (--from-cache mode for validation scripts; no API keys) |
| `cross-vendor-judge`      | opt-in | Codifies cross-vendor LLM-judge enforcement to mitigate v3 paper's reflexivity-hazard #1 |

## Selective inclusion

Consumers who only want a subset can skip this composite and include the
individual behavior files directly, for example:

```yaml
includes:
  - bundle: research:behaviors/honest-pivot.md
  - bundle: research:behaviors/exploratory-labeling.md
```
