---
bundle:
  name: research-stop-slop
  version: 0.5.0
  description: |
    Silent prose-discipline behavior. Removes AI-tell patterns (adverb
    piles, binary contrasts, em-dashes, vague declaratives, false agency,
    throat-clearing openers) from /draft output and flags survivors during
    /critique. Default-on; never user-invocable. The user should not know
    this behavior exists unless they override it with --no-stop-slop.
---

# Behavior: stop-slop

**Default:** on
**Overridable:** yes, with explicit `--no-stop-slop` flag (logged in audit trail)
**User-visible:** no — fires silently as part of /draft and /critique
**Applies to:** /draft (while prose is being written) and /critique (while prose is being evaluated)

---

## What it does

Applies prose-quality rules to every draft the bundle produces, and
surfaces survivors during /critique. The rules cover the predictable
signatures of machine-generated prose: adverb crutches, throat-clearing
openers, binary contrasts, em-dashes, vague declaratives, false agency,
narrator-from-a-distance voice, and passive constructions.

The behavior does not ask the user's permission, does not produce a
"slop report" artifact in the session directory, does not appear as a
/stop-slop slash command. It operates as a guiding force on the prose
the bundle commits to disk. The only visible effect is that the drafts
read cleaner.

## Why it's a behavior, not a skill

Prose-discipline is not a tool a user reaches for; it is a standard the
bundle holds its own output to. Other rigor behaviors in this bundle
(honest-pivot, exploratory-labeling) follow the same pattern: default-on,
cross-cutting, silent unless overridden. stop-slop joins them.

The earlier skill form (removed in v0.5.0) was the wrong abstraction.
Making stop-slop user-invocable via `/stop-slop` or
`load_skill("stop-slop")` pushed the discipline-enforcement burden onto
the user. The behavior form shifts that burden back onto the bundle
where it belongs.

## Triggers

The behavior fires at two points in every session:

1. **/draft** — technical-writer consults the rules (see
   [`context/prose-quality/phrases.md`](../context/prose-quality/phrases.md)
   and [`structures.md`](../context/prose-quality/structures.md)) while
   composing the draft. Rules are constraints on production, not
   post-hoc filters.
2. **/critique** — honest-critic grep-sweeps the draft for rule
   violations and adds `findings_stop_slop:` to the critique artifact.
   Findings map onto the existing severity vocabulary:

   | Pattern | Default severity |
   |---|---|
   | Filler phrase / adverb in body paragraph | `NOTE` |
   | Filler phrase / adverb in thesis or executive summary | `WARN` |
   | Binary contrast in a load-bearing claim | `WARN` |
   | False agency in the limitations section | `BLOCK` (limitations must name the human holding the bag) |
   | Em-dash in body prose | `NOTE` |
   | Vague declarative without a named specific | `WARN` |

## Response

On a /critique finding:

1. **NOTE-severity findings** are logged in `critique.yaml` but do not
   gate /publish. They surface so the author can clean them up on the
   next pass.
2. **WARN-severity findings** are logged and surfaced in the draft's
   limitations section as acknowledged prose-quality debt.
3. **BLOCK-severity findings** (false agency in limitations is the only
   pre-defined one) gate /publish until the flagged text is rewritten
   to name the human actor.

The /draft phase's behavior is stricter: rules are active constraints.
If technical-writer would have produced a binary contrast or an adverb
crutch, the behavior rewrites the construction before the draft is
committed to disk. The author never sees the slop version.

## Rules catalog

The active rule set lives in two context files so that agents can load
them on demand without carrying them as permanent context:

- [`context/prose-quality/phrases.md`](../context/prose-quality/phrases.md)
  — phrase blacklist (throat-clearing, adverbs, business jargon,
  meta-commentary, performative emphasis, telling-not-showing, vague
  declaratives).
- [`context/prose-quality/structures.md`](../context/prose-quality/structures.md)
  — structural patterns to avoid (binary contrasts, negative listings,
  dramatic fragmentation, rhetorical setups, false agency,
  narrator-from-a-distance, passive voice, Wh- starters, rhythm
  patterns).

A third file, [`context/prose-quality/examples.md`](../context/prose-quality/examples.md),
carries before/after rewrites including cases drawn from this bundle's
own drafts.

## Lineage

Adapted from [hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)
(MIT) for Amplifier. The original was a single SKILL.md for Claude Code.
The bundle re-architects the same rule set as a silent, default-on
behavior to match the rigor-behaviors pattern the rest of this bundle
uses. Content of the rule catalogs is a faithful port of the original,
with additional examples drawn from this bundle's drafts.

## Interaction with other behaviors

- **honest-pivot** — both fire default-on. honest-pivot catches logical
  divergence from the pre-registered plan; stop-slop catches prose
  divergence from disciplined writing standards. One catches *what*
  changes, the other catches *how it reads*.
- **exploratory-labeling** — if a passage is labeled EXPLORATORY,
  stop-slop still applies. Exploratory findings are allowed to be
  tentative, but they still have to be well-written.

## Example — white-paper recipe

```
[ stop-slop: ON ]

/draft produces an executive summary. Inside the draft phase,
technical-writer would have written "Here's the thing: attorneys
really struggle with discipline-leakage in AI drafts." stop-slop
rewrites the construction before the sentence commits:
"Attorneys struggle with discipline-leakage in AI drafts."

/critique then grep-sweeps the committed draft:
  • zero adverb crutches           PASS
  • zero throat-clearing openers   PASS
  • zero rendering em-dashes       PASS
  • zero binary contrasts          PASS
  • zero vague declaratives        PASS
  • false-agency check on L3       PASS (attorney named as actor)

Three NOTE-severity items logged for author awareness; none gate
/publish.
```

The user sees only the clean final draft. The behavior is invisible to
them unless they ask why the prose reads as it does.
