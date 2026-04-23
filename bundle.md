---
bundle:
  name: research
  version: 0.5.0
  description: |
    Superpowers for scientific rigor. From sharpened question to venue-ready
    output, with pre-registration discipline and honest-pivot defaults baked
    in. For anyone who needs to produce a defensible written artifact —
    patent brief, policy brief, white paper, grant application, or journal
    paper — regardless of formal research training.
  author: Michael Jabbour
  license: MIT
  homepage: https://github.com/michaeljabbour/amplifier-bundle-research

# --------------------------------------------------------------------------
# Dependencies — foundation provides providers, session, hooks, common tools.
# The recipes bundle provides the /recipes command and YAML workflow execution.
# Our own behavior package is composed in via research:behaviors/research.md.
# --------------------------------------------------------------------------
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-recipes@main
  - bundle: research:behaviors/research.md

# --------------------------------------------------------------------------
# Agents — ten specialized wrappers over K-Dense scientific-agent-skills
# plus one orchestration coordinator. Each is a context sink: it loads its
# K-Dense skill only when spawned, keeping the root session lean.
#
# Short-name form per foundation BUNDLE_GUIDE — the loader auto-prepends
# "agents/" and appends ".md". Do NOT include either in these entries.
# --------------------------------------------------------------------------
agents:
  include:
    - research:hypothesis-designer
    - research:methodologist
    - research:preregistration-reviewer
    - research:statistician
    - research:honest-critic
    - research:technical-writer
    - research:figure-designer
    - research:citation-manager
    - research:venue-formatter
    - research:research-coordinator

# --------------------------------------------------------------------------
# Tools — first-class capabilities with Python implementations.
#
# tool-experiment-audit: Integrity audit for experiment directories.
#   Detects HANDLER_ERROR cascades, response-quality issues, missing manifests,
#   and implausible statistics. Run before trusting any experiment's numbers.
# --------------------------------------------------------------------------
tools:
  - path: modules/tool-experiment-audit
    mount: amplifier_research_audit:mount
---

# Research Bundle

Superpowers for scientific rigor. Produces defensible written artifacts across
the research output ladder: patent brief → policy brief → white paper → grant
proposal → empirical paper → benchmark paper → replication study → literature
review.

The bundle enforces pre-registration discipline (`/plan` hash-locks the plan
before data is seen) and honest-by-default labeling (`honest-pivot` and
`exploratory-labeling` behaviors surface any deviation between plan and
output). Agents wrap K-Dense scientific-agent-skills; modes expose a
persona-aware workflow (`/question → /plan → /execute → /critique → /draft →
/publish`); recipes compose the whole pipeline per output type.

@research:context/instructions.md

@research:context/experiment-integrity-awareness.md

---

@foundation:context/shared/common-system-base.md
