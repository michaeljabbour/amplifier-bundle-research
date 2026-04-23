---
name: stop-slop
description: |
  Remove AI-tell writing patterns from prose. Use when drafting, editing,
  or reviewing text for predictable AI signatures — filler openers,
  binary contrasts, em-dashes, adverb piles, passive voice, false agency,
  narrator-from-a-distance voice, formulaic "not X, Y" reveals,
  vague declaratives. Loaded by honest-critic during /critique passes
  and by technical-writer during /draft passes.
  Trigger phrases: "clean up the prose", "remove AI tells", "slop check",
  "stop-slop pass", "tighten the writing", "sounds too AI".
model_role: critique
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit_file
  - grep
  - glob
  - delegate
context: inline
disable-model-invocation: false
metadata:
  source: Adapted from hardikpandya/stop-slop (MIT) — https://github.com/hardikpandya/stop-slop
  original_author: Hardik Pandya (https://hvpandya.com)
  adaptation: amplifier-bundle-research, Apr 2026
  adapted_by: Michael Jabbour
  license: MIT (source) / MIT (adaptation matches source)
---

# Stop Slop

Eliminate predictable AI writing patterns from prose.

## When to use

Run this skill at two points in the research bundle's workflow:

1. **During `/draft` (technical-writer).** Pass the drafted prose through the eight core rules below before emitting the `/critique`-ready draft.
2. **During `/critique` (honest-critic).** Treat slop-detection findings as WARN-severity by default; promote to BLOCK when a flagged pattern survives in a load-bearing claim (executive summary, thesis sentence, limitations section).

Outside the bundle, the skill is user-invocable via `/stop-slop` against any text the user supplies.

## Core rules

1. **Cut filler phrases.** Remove throat-clearing openers, emphasis crutches, and all adverbs. Full list in `references/phrases.md`.

2. **Break formulaic structures.** Avoid binary contrasts, negative listings, dramatic fragmentation, rhetorical setups, false agency. Full list in `references/structures.md`.

3. **Use active voice.** Every sentence needs a human subject doing something. No passive constructions. No inanimate objects performing human actions ("the complaint becomes a fix").

4. **Be specific.** No vague declaratives ("The reasons are structural"). Name the specific thing. No lazy extremes ("every", "always", "never") doing vague work.

5. **Put the reader in the room.** No narrator-from-a-distance voice. "You" beats "People". Specifics beat abstractions.

6. **Vary rhythm.** Mix sentence lengths. Two items beat three. End paragraphs differently. No em-dashes.

7. **Trust readers.** State facts directly. Skip softening, justification, hand-holding.

8. **Cut quotables.** If it sounds like a pull-quote, rewrite it.

## Quick checks

Before delivering prose, grep for these and fix any hit:

- Any adverbs? Kill them.
- Any passive voice? Find the actor, make them the subject.
- Inanimate thing doing a human verb ("the decision emerges")? Name the person.
- Sentence starts with a Wh- word? Restructure it.
- Any "here's what/this/that" throat-clearing? Cut to the point.
- Any "not X, it's Y" contrasts? State Y directly.
- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash anywhere? Remove it.
- Vague declarative ("The implications are significant")? Name the specific implication.
- Narrator-from-a-distance ("Nobody designed this")? Put the reader in the scene.
- Meta-joiners ("The rest of this essay...")? Delete. Let the essay move.

A concrete grep sweep for a Markdown draft:

```bash
# AI-tell signatures — every hit should get reviewed
grep -nE '\b(really|just|literally|genuinely|honestly|simply|actually|deeply|truly|fundamentally|inherently|inevitably|interestingly|importantly|crucially)\b' draft.md
grep -nE "Here's (the thing|what|this|that|why|the problem)" draft.md
grep -nE '—' draft.md          # em-dashes
grep -nE "^(What|When|Where|Which|Who|Why|How)\b" draft.md   # Wh- starters
grep -nE "isn't X.*it's Y|not because.*because|not X.*but Y" draft.md   # binary contrasts
grep -nE "\b(navigate|unpack|lean into|landscape|game-changer|double down|deep dive|circle back)\b" draft.md   # jargon
```

## Scoring

Rate the prose 1–10 on each dimension. A draft scoring below 35/50 needs revision before delivery.

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |

## Amplifier integration

When invoked from `/critique` via `honest-critic`, this skill's findings map onto the bundle's severity vocabulary:

| Slop pattern | Default severity |
|---|---|
| Filler phrase / adverb in body paragraph | `NOTE` |
| Filler phrase / adverb in thesis or exec summary | `WARN` |
| Binary contrast in a load-bearing claim | `WARN` |
| False agency in the limitations section | `BLOCK` (limitations must name the human holding the bag) |
| Em-dash anywhere in the draft | `NOTE` |
| Vague declarative ("implications are significant") without named implication | `WARN` |

Findings enter the session `critique.yaml` under a `findings_stop_slop:` block alongside `findings_block`, `findings_warn`, `findings_note`.

## References

- [references/phrases.md](references/phrases.md) — complete phrase blacklist with business-jargon substitutions
- [references/structures.md](references/structures.md) — structural patterns to avoid
- [references/examples.md](references/examples.md) — generic before/after rewrites
- [references/research-bundle-examples.md](references/research-bundle-examples.md) — before/after rewrites from this bundle's own /draft outputs

## License

MIT (adaptation matches source).
