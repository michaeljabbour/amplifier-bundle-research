# Architecture

Four layers, each thin. The bundle's value is in the composition, not in any single layer.

```
┌──────────────────────────────────────────────────────────────────┐
│                         Recipes (YAML)                            │
│  patent-brief · policy-brief · white-paper · empirical-paper ·   │
│  lit-review · grant · replication-study                           │
└─────────────────────────────┬────────────────────────────────────┘
                              │  composes
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Modes (user-facing verbs)                      │
│   /question → /plan → /execute → /critique → /draft → /publish   │
└─────────────────────────────┬────────────────────────────────────┘
                              │  invokes
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Agents (thin wrappers)                         │
│  hypothesis-designer · methodologist · preregistration-reviewer  │
│  statistician · honest-critic · technical-writer                 │
│  figure-designer · venue-formatter                                │
└─────────────────────────────┬────────────────────────────────────┘
                              │  wraps
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Skills (K-Dense, upstream)                     │
│  hypothesis-generation · scientific-critical-thinking            │
│  statistical-analysis · peer-review · scholar-evaluation         │
│  scientific-writing · scientific-schematics                      │
│  citation-management · venue-templates · scientific-brainstorming│
└──────────────────────────────────────────────────────────────────┘

         Behaviors run silently across all modes:
         honest-pivot · exploratory-labeling
```

## Why this layering

**Recipes are replaceable.** A user who wants a new output type copies an existing recipe, edits the template and defaults, and it works. No code change.

**Modes are stable.** The six verbs are the UX contract. They never change. Upgrades to agents or skills don't break user muscle memory.

**Agents are thin wrappers.** ~30 lines each. They set role, tone, and output contract, then reference the skill file. Upgrading the skill upstream (K-Dense releases v2.40 tomorrow) needs no bundle change.

**Skills are upstream.** Single source of truth. The bundle doesn't fork or vendor skills. It references them.

## Data flow — a worked example

Patent brief, persona A (patent attorney, no science training).

```
USER INPUT
 ▼
"Rolling-ROI control — closed-loop governance system that
 adjusts per-session AI agent compute based on realized value."
 ▼
┌─────────────┐
│ /question   │  hypothesis-designer tightens to:
└─────────────┘  "Does closed-loop compute governance reduce wasted
                  inference spend vs. static budgets, measured as
                  tokens-per-resolved-task on [benchmark]?"
 ▼
┌─────────────┐
│ /plan       │  methodologist + preregistration-reviewer produce:
└─────────────┘  - claims table (novelty / non-obviousness / utility)
                  - prior-art search strategy
                  - enablement experiments outline
                  - preregistration.yaml with locked predictions
 ▼
┌─────────────┐
│ /execute    │  recipe-specific sub-tools:
└─────────────┘  - prior-art search (USPTO, Google Patents, arXiv)
                  - claim-chart build
                  - enablement demo run (if code available)
 ▼
┌─────────────┐
│ /critique   │  honest-critic applies:
└─────────────┘  - novelty stress test (has this been done?)
                  - enablement stress test (could a PHOSITA build it?)
                  - overclaim flags
                  - scholar-evaluation scoring
 ▼
┌─────────────┐
│ /draft      │  technical-writer produces:
└─────────────┘  - background / problem
                  - summary of invention
                  - detailed description
                  - claims
                  - prior-art distinction table
                  - figure-designer generates architecture diagrams
 ▼
┌─────────────┐
│ /publish    │  venue-formatter produces:
└─────────────┘  - USPTO-formatted PDF + DOCX
                  - BibTeX bibliography
                  - cover sheet + abstract
```

Same sequence, same agents, same skills — but for `empirical-paper` the `/execute` step runs actual experiments and the `/publish` step emits ICML-compliant LaTeX.

## Layer boundaries (respected)

Following Amplifier's architectural rule: **runtime modules depend only on `amplifier-core`, never on `amplifier-foundation`**. This bundle contains no custom runtime modules. It's pure configuration — agents (markdown), modes (markdown), recipes (YAML), templates (markdown/tex/yaml), behaviors (markdown). All orchestration happens through Amplifier's standard agent-delegation mechanism.

This keeps the bundle portable: it works on any Amplifier install without pulling in foundation-specific dependencies.

## Comparison to related bundles

| Bundle | Layer it owns | This bundle's relationship |
|---|---|---|
| `amplifier-foundation` | Core tools, base agents | Depends on (via `includes: foundation`) |
| `amplifier-bundle-superpowers` | Software dev methodology | Sibling — same design pattern, different domain |
| `amplifier-bundle-stories` | Narrative writing | Sibling — same install ergonomics as our target |
| `amplifier-bundle-recipes` | Recipe runtime | Depends on (for recipe execution) |
| K-Dense `scientific-agent-skills` | Skill library | Depends on (skills stay upstream) |

## Non-architectural notes

The bundle intentionally does not ship its own LLM provider routing, session management, or tool execution. These are Amplifier-core responsibilities. The bundle is a configuration package only.
