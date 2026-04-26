---
bundle:
  name: research
  version: 0.6.0
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
#
# tool-experiment-resume: Experiment resume/repair capability.
#   When a sweep aborts mid-run, identify which items have clean records
#   (preserve), which need re-running (errored or never-started), and merge
#   preserved + new records into a unified result. Three subcommands:
#   plan → subset → merge.
#
# tool-experiment-power: Statistical power analysis capability.
#   Paired-binary (McNemar) and independent t-test power calculations.
#   Four subcommands: required-n → mde → post-hoc → sensitivity.
#   Pre-register sample sizes; compute MDE; build sensitivity tables.
#
# tool-experiment-stage-analyzer: Stage-trace empty-response root-cause analyzer.
#   Ingests stage_traces.jsonl (generator / critic / revert_decision) and
#   categorizes empty-final records by failure-mode origin (six categories).
#   Applies pre-registered H1a/H1b confirmation criteria (§2.3).
#   Two subcommands: analyze → Markdown report; hypothesis-test → JSON verdicts.
#
# tool-experiment-provenance-check: Pre-experiment data provenance auditor.
#   Parses experiment scripts with AST to find all data file references, then
#   checks each against git (TRACKED / UNTRACKED / MISSING / IN_GITIGNORE).
#   Prevents reproducibility gaps (e.g., hle_handcrafted.json, commit e189188).
#   Three subcommands: audit-script → Markdown report; check-files → exit codes;
#   pre-experiment-gate → hard launch gate (exits 1 if any untracked file).
# --------------------------------------------------------------------------
tools:
  - path: modules/tool-experiment-audit
    mount: amplifier_research_audit:mount
  - path: modules/tool-experiment-resume
    mount: amplifier_research_resume:mount
  - path: modules/tool-experiment-power
    mount: amplifier_research_power:mount
  - path: modules/tool-experiment-stage-analyzer
    mount: amplifier_research_stage_analyzer:mount
  - path: modules/tool-experiment-provenance-check
    mount: amplifier_research_provenance_check:mount
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

@research:context/experiment-resume-awareness.md

@research:context/experiment-power-awareness.md

@research:context/experiment-stage-analyzer-awareness.md

@research:context/experiment-provenance-awareness.md

---

@foundation:context/shared/common-system-base.md
