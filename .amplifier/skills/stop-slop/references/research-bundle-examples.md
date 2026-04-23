# Research Bundle — Dogfood Before/After Examples

Before/after rewrites from the research bundle's own `/draft` outputs
(session `e623279d`, the patent-attorney white paper). These are the
slop patterns stop-slop caught on a real bundle-produced draft.

---

## Example 1: Vague declarative in a capability claim

**Before:**
> "The implications of this methodology layer are significant for the patent-prosecution community."

**After:**
> "Second attorneys can reproduce the search scope from the audit log; opposing counsel can read the same log during litigation."

**Changes:** Named two specific implications instead of announcing their importance. The original sentence survives /critique as a WARN ("vague declarative") until a named consequence replaces the word "significant."

---

## Example 2: False agency in limitations

**Before:**
> "The trade-secret risk persists until the on-prem deployment mode is validated."

**After:**
> "You should not use the default hosted-LLM configuration on trade-secret-sensitive matters until an on-prem deployment mode exists that you have validated against your firm's confidentiality obligations."

**Changes:** Named the actor (the attorney reader). Named the human-judgment step (validation against firm obligations, not abstract "is validated"). Limitations sections carry the sharpest stop-slop requirement in the bundle — the attorney is the one holding the bag, so the attorney must be the grammatical subject.

---

## Example 3: Throat-clearing opener in an executive summary

**Before:**
> "Here's what the bundle does: it imposes a six-step sequence over the drafting work."

**After:**
> "The bundle imposes a six-step sequence over the drafting work."

**Changes:** Dropped three words. The sentence does not need a preview. Any executive-summary sentence that begins with "Here's" is a /critique finding.

---

## Example 4: Binary contrast in a novelty note

**Before:**
> "The bundle isn't a drafting robot. It's a methodology scaffold."

**After:**
> "The bundle is a methodology scaffold. It does not emit filing-ready prose autonomously."

**Changes:** State the positive claim first. Attach the negation as a separate, specific sentence. The "not X, Y" form reads as manufactured and defensive; two factual sentences read as an attorney speaking.

---

## Example 5: Adverb pile-up in a risk statement

**Before:**
> "The bundle really does fundamentally change how attorneys approach first-draft work, and it genuinely reduces overclaiming."

**After:**
> "The bundle changes how attorneys approach first-draft work. It catches three classes of overclaim (superlatives, unsupported quantifications, unstated enablement assumptions) at the /critique pass."

**Changes:** Removed "really," "fundamentally," "genuinely." Replaced the unqualified "reduces overclaiming" with a numbered, named claim that can be tested. Adverbs are the single most common /critique WARN in bundle-produced drafts.

---

## Example 6: Em-dash cluster in a limitations paragraph

**Before:**
> "v0.4 is the current state — no real attorneys have used the bundle yet — which is the headline limitation this paper acknowledges."

**After:**
> "v0.4 is the current state. No real attorneys have used the bundle yet. This is the headline limitation."

**Changes:** Em-dashes split one sentence into three complete ones. Three facts, three sentences, no ambiguity about emphasis.

---

## Example 7: Narrator-from-a-distance in the problem statement

**Before:**
> "Patent attorneys everywhere struggle with the same discipline-leakage problem when they adopt AI tools."

**After:**
> "If you are a prosecution attorney who has tried drafting a specification with ChatGPT or Claude, you have probably already caught yourself excluding a prior-art reference that did not fit the claim set you wanted."

**Changes:** Put the reader in the seat. Named the concrete behavior. Dropped the lazy extreme ("everywhere"). The rewrite doubles in length and halves in condescension.
