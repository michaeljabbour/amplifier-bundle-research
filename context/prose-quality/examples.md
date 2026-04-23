# Before/After Examples (stop-slop behavior)

This file is consulted by the `stop-slop` behavior during `/draft` and
`/critique` for concrete rewrite patterns. Generic examples are drawn
from the original stop-slop skill; research-bundle-specific examples
are drawn from this bundle's own drafts.

---

## Generic examples (adapted from hardikpandya/stop-slop, MIT)

### Example 1: Throat-clearing + binary contrast

**Before:**
> "Here's the thing: building products is hard. Not because the technology is complex. Because people are complex. Let that sink in."

**After:**
> "Building products is hard. Technology is manageable. People aren't."

**Changes:** Removed opener, binary contrast structure, and emphasis crutch. Direct statements.

### Example 2: Filler + unnecessary reassurance

**Before:**
> "It turns out that most teams struggle with alignment. The uncomfortable truth is that nobody wants to admit they're confused. And that's okay."

**After:**
> "Teams struggle with alignment. Nobody admits confusion."

**Changes:** Cut hedging ("most"), removed throat-clearing, deleted permission-granting ending.

### Example 3: Business jargon stack

**Before:**
> "In today's fast-paced landscape, we need to lean into discomfort and navigate uncertainty with clarity. This matters because your competition isn't waiting."

**After:**
> "Move faster. Your competition is."

**Changes:** Eliminated jargon entirely. Core message in six words.

### Example 4: Dramatic fragmentation

**Before:**
> "Speed. Quality. Cost. You can only pick two. That's it. That's the tradeoff."

**After:**
> "Speed, quality, cost: pick two."

**Changes:** Single sentence. No performative emphasis. (Use a colon rather than an em-dash.)

### Example 5: Rhetorical setup

**Before:**
> "What if I told you that the best teams don't optimize for productivity? Here's what I mean: they optimize for learning. Think about it."

**After:**
> "The best teams optimize for learning, not productivity."

**Changes:** Direct claim. No rhetorical scaffolding.

---

## Research-bundle-specific examples

Drawn from the bundle's own `/draft` outputs (session `e623279d`, the
patent-attorney white paper at `examples/whitepaper-dogfood-run/`).
These are the slop patterns stop-slop catches on a real bundle-produced
draft.

### Example A: Vague declarative in a capability claim

**Before:**
> "The implications of this methodology layer are significant for the patent-prosecution community."

**After:**
> "Second attorneys can reproduce the search scope from the audit log; opposing counsel can read the same log during litigation."

**Changes:** Named two specific implications instead of announcing their importance. The original sentence survives /critique as a WARN until a named consequence replaces the word "significant."

### Example B: False agency in limitations

**Before:**
> "The trade-secret risk persists until the on-prem deployment mode is validated."

**After:**
> "You should not use the default hosted-LLM configuration on trade-secret-sensitive matters until an on-prem deployment mode exists that you have validated against your firm's confidentiality obligations."

**Changes:** Named the actor (the attorney reader). Named the human-judgment step (validation against firm obligations, not abstract "is validated"). Limitations sections carry the sharpest stop-slop requirement in the bundle — the attorney is the one holding the bag, so the attorney must be the grammatical subject. This is the BLOCK-severity pattern.

### Example C: Throat-clearing opener in an executive summary

**Before:**
> "Here's what the bundle does: it imposes a six-step sequence over the drafting work."

**After:**
> "The bundle imposes a six-step sequence over the drafting work."

**Changes:** Dropped three words. The sentence does not need a preview. Any executive-summary sentence that begins with "Here's" is a /critique finding.

### Example D: Binary contrast in a novelty note

**Before:**
> "The bundle isn't a drafting robot. It's a methodology scaffold."

**After:**
> "The bundle is a methodology scaffold. It does not emit filing-ready prose autonomously."

**Changes:** State the positive claim first. Attach the negation as a separate, specific sentence. The "not X, Y" form reads as manufactured and defensive; two factual sentences read as an attorney speaking.

### Example E: Adverb pile-up in a risk statement

**Before:**
> "The bundle really does fundamentally change how attorneys approach first-draft work, and it genuinely reduces overclaiming."

**After:**
> "The bundle changes how attorneys approach first-draft work. It catches three classes of overclaim (superlatives, unsupported quantifications, unstated enablement assumptions) at the /critique pass."

**Changes:** Removed "really," "fundamentally," "genuinely." Replaced the unqualified "reduces overclaiming" with a numbered, named claim that can be tested. Adverbs are the single most common /critique WARN in bundle-produced drafts.

### Example F: Em-dash cluster in a limitations paragraph

**Before:**
> "v0.4 is the current state — no real attorneys have used the bundle yet — which is the headline limitation this paper acknowledges."

**After:**
> "v0.4 is the current state. No real attorneys have used the bundle yet. This is the headline limitation."

**Changes:** Em-dashes split one sentence into three complete ones. Three facts, three sentences, no ambiguity about emphasis.

### Example G: Narrator-from-a-distance in the problem statement

**Before:**
> "Patent attorneys everywhere struggle with the same discipline-leakage problem when they adopt AI tools."

**After:**
> "If you are a prosecution attorney who has tried drafting a specification with ChatGPT or Claude, you have probably already caught yourself excluding a prior-art reference that did not fit the claim set you wanted."

**Changes:** Put the reader in the seat. Named the concrete behavior. Dropped the lazy extreme ("everywhere"). The rewrite doubles in length and halves in condescension.
