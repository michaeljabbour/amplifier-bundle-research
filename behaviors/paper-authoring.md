---
bundle:
  name: research-paper-authoring
  version: 0.1.0
  description: |
    Paper-authoring slice of the research bundle: LaTeX authoring and
    compilation, multi-conference formatting (NeurIPS, ICML, ACL, IEEE, ACM,
    arXiv), citation management, and figure generation (incl. the PaperBanana
    multi-agent pipeline). This is the "just write a paper" capability set,
    grouped so it can be composed without the research-rigor ceremony
    (pre-registration, honest-pivot, experiment tooling, research modes).

    Absorbs the former amplifier-bundle-scientificpaper, which was a strict
    subset of this bundle.

includes:
  - bundle: research:behaviors/latex-authoring.md
  - bundle: research:behaviors/conference-styling.md
  - bundle: research:behaviors/figure-generation.md
  - bundle: research:behaviors/paperbanana.md

agents:
  include:
    - research:research-paper-architect
    - research:research-citation-manager
---

# Paper Authoring (Composite)

Canonical entry point for the paper-authoring capabilities. Including
`research:behaviors/paper-authoring.md` transitively pulls in LaTeX authoring,
conference styling, figure generation, and the PaperBanana tool, plus the
paper-architect and citation-manager agents.
