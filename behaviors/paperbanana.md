---
bundle:
  name: research-paperbanana
  version: 0.4.0
  description: "PaperBanana multi-agent figure generation with quality veto rules. Based on arXiv 2601.23265 research, provides automated iterative refinement with 8 publication-ready quality checks."

tools:
  - module: tool-paperbanana
    source: ../modules/tool-paperbanana
    config:
      default_max_iterations: 3
      output_dir: "figures"
      default_quality_rules:
        - "no_low_quality_artifacts"
        - "professional_colors"
        - "no_black_backgrounds"
        - "modern_style"
        - "vector_preferred"
        - "appropriate_aspect_ratio"
        - "clear_labels"
        - "data_integrity"

agents:
  include:
    - research:figure-designer

context:
  include:
    - research:context/figure-generation/paperbanana-methodology.md
---

# PaperBanana Behavior

Multi-agent figure generation with quality veto rules based on arXiv 2601.23265 research. Provides automated iterative refinement with 8 publication-ready quality checks.

## Agent Delegation
All PaperBanana figure requests -> @figure-designer
