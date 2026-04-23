---
bundle:
  name: research-behaviors
  version: 0.2.0
  description: |
    Composite behavior bundle. Packages all seven research-bundle behaviors
    (honest-pivot, exploratory-labeling, paperbanana, figure-generation,
    latex-authoring, conference-styling, research-modes) so that consumers can pull them
    in as a single unit, and so that research/bundle.md stays DRY by
    referencing this one file instead of each behavior individually.

includes:
  - bundle: research:behaviors/honest-pivot.md
  - bundle: research:behaviors/exploratory-labeling.md
  - bundle: research:behaviors/paperbanana.md
  - bundle: research:behaviors/figure-generation.md
  - bundle: research:behaviors/latex-authoring.md
  - bundle: research:behaviors/conference-styling.md
  - bundle: research:behaviors/research-modes.md       # Registers /question, /study-plan, /execute, /critique, /draft, /publish as real slash commands
---

# Research Behaviors (Composite)

This is the canonical entry point for consuming research-bundle behaviors
from any other bundle. Including `research:behaviors/research.md` transitively
pulls in all seven behaviors with their default configurations.

## What's included

| Behavior | Default | Purpose |
|----------|---------|---------|
| `honest-pivot` | on | Surfaces any deviation between pre-registered plan and final output |
| `exploratory-labeling` | on | Tags unpredicted findings as `[EXPLORATORY]` through to publish |
| `paperbanana` | on | PaperBanana multi-agent figure generation (8 quality veto rules) |
| `figure-generation` | on | Tool selection matrix for figures (matplotlib, TikZ, Mermaid, Imagen) |
| `latex-authoring` | on | LaTeX compilation, conference formatting, structural planning |
| `conference-styling` | on | Per-venue formatting (NeurIPS, ICML, ACL, IEEE, ACM, arXiv) |
| `research-modes` | on | Registers /question, /study-plan, /execute, /critique, /draft, /publish as real slash commands |

## Selective inclusion

Consumers who only want a subset can skip this composite and include the
individual behavior files directly, for example:

```yaml
includes:
  - bundle: research:behaviors/honest-pivot.md
  - bundle: research:behaviors/exploratory-labeling.md
```
