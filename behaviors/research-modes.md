---
bundle:
  name: research-modes-behavior
  version: 0.4.0
  description: |
    Wires the research bundle's 6 interactive modes (/question, /study-plan,
    /execute, /critique, /draft, /publish) as real slash commands via the
    modes hook system. Without this behavior, the modes/*.md files are inert
    documentation. Note: `/study-plan` is the slash command for the research
    bundle's plan mode — renamed from `/plan` to avoid collision with the
    default `/plan` mode shipped by amplifier-bundle-modes.

# Include the modes BEHAVIOR (NOT the full modes bundle — full bundle
# would override session.orchestrator). Pattern from superpowers-methodology.yaml.
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=behaviors/modes.yaml

# hooks-mode scans search_paths for mode files and registers them as slash commands
hooks:
  - module: hooks-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/hooks-mode
    config:
      search_paths:
        - "@research:modes"

# tool-mode lets agents request mode transitions (e.g., /question auto-transitioning to /study-plan)
tools:
  - module: tool-mode
    source: git+https://github.com/microsoft/amplifier-bundle-modes@main#subdirectory=modules/tool-mode
    config:
      gate_policy: "warn"

# Inject mode-system understanding into session context
context:
  include:
    - modes:context/modes-instructions.md
---

# Research Modes Behavior

This behavior turns `research:modes/*.md` into real slash commands. When active,
users can type `/question`, `/study-plan`, `/execute`, `/critique`, `/draft`, and
`/publish` in any session where the research bundle is loaded.

## Why `/study-plan` instead of `/plan`?

The `amplifier-bundle-modes` runtime ships a built-in `/plan` mode ("Analyze,
strategize, and organize — but don't implement"). When two bundles register
the same shortcut, `hooks-mode` uses first-load-wins — the second bundle's
registration is silently dropped with an INFO log. Since the modes bundle
loads its defaults before our research-modes behavior, their `/plan` always
wins.

We renamed our mode's `name` to `study-plan` so all 6 research modes register
cleanly. The `research-coordinator` agent routes natural-language invocations
(e.g., "Let's plan the study", "Run the plan mode") to `/study-plan`
regardless of which phrasing the user uses, so Persona A users rarely need to
remember the exact slash name.

## Cross-bundle caveat

If a consumer loads this bundle alongside another bundle that also mounts
`hooks-mode` with its own `search_paths` (e.g., `amplifier-bundle-superpowers`),
the deep-merge implementation replaces lists rather than concatenating them —
one bundle's modes will win and the other's will be silently dropped. The fix
is a wrapper bundle that declares `hooks-mode` once with all desired
`search_paths` listed together. See the parallax-discovery bundle for the
canonical example of this collision warning.
