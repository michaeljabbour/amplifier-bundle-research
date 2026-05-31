# Case Study: "Do Language Models Need Sleep?" — a dogfooded study with this bundle

A worked example of running the research bundle's full workflow end-to-end on a
real question: porting *Language Models Need Sleep* (arXiv:2605.26099) — "when
context fills, run an offline consolidation pass" — to Amplifier agent context
management. It is preserved here because the **methodology and its failure modes**
are reusable, even though the headline finding is a (well-earned) negative result.

Full harness + raw history live in the `amplifier-research-sleep` project; this is
the distilled, transferable record.

---

## The workflow that ran

`/question` (hypothesis-designer) → `/study-plan` hash-locked pre-registration
(methodologist + statistician) → `/execute` → `/critique` (honest-critic) →
corrected re-run → `/draft`. Three study generations:

1. **Set-coverage proxy** — 6+ context strategies under a fixed token budget.
2. **Real mechanism** — actual LLM consolidation (N recurrent passes,
   query-agnostic), real multi-hop reasoning, `gpt-5` wake (oracle = 1.00 at all
   depths, capability precondition verified), `gpt-4.1` consolidator, deterministic
   gold grading, paired McNemar + seed-cluster bootstrap.

## The headline flipped TWICE — that is the point

| Stage | Claim it produced | Why it was wrong / corrected |
|---|---|---|
| Dogfood | "consolidation retains early facts 5/5" | artifact: facts were clustered at the start |
| Proxy v1 | "RAG dominates; sleep fails" | **tautology** — the retriever was an exact-match oracle |
| Real v3 (pre-critique) | "dumb retention beats LLM consolidation" | **format confound** — verbatim used sentences, LLM used triples |
| Real v3 (corrected) | "faithful consolidation == verbatim; format + filler-stripping are the levers" | survives adversarial review |

The adversary (`honest-critic`) earned its keep three times: it caught the RAG
tautology, the format confound, and **two genuine code bugs** (a dead distractor
parameter; a first-vs-last answer-extraction bug). Each correction changed a
conclusion. Without it, a wrong causal claim ships.

## Corrected findings (real mechanism, n=192 paired)

- Faithful LLM "sleep" consolidation is **statistically equivalent** to dumb verbatim
  retention for atomic facts (delta ~= 0, p=0.69-1.0). The LLM step adds nothing.
- "Creative" reorganize/derive consolidation **HURTS** (-28pp; fabricates ~50-75%
  of facts; a faithfulness probe counted ~106 fabricated edges/stream).
- The paper's signature "more sleep helps" is **null** (CI [-5.7, +4.7]).
- The real levers are **filler-stripping** (+19pp vs recency, no LLM) and
  **representation format** (natural-language sentences beat terse triples ~19pp,
  p<1e-6).

Net: a general-purpose LLM summarizer cannot replicate the paper's *learned*
fast-weight rule; for atomic facts it is neutral at best, fabricating at worst.

## Reusable methodology (the transferable value)

Patterns any future context-/memory-strategy study should reuse:

1. **The arms template.** Always include: a recency-truncation baseline, a
   verbatim-retain control, and the candidate consolidator — AND **control
   representation format as its own arm**. The format confound (natural language
   vs symbolic triples = ~19pp) is the trap that nearly invalidated this study.
2. **The faithfulness / hallucination probe.** Before trusting any LLM consolidator,
   measure fabrication directly: parse the consolidated output and count edges/facts
   that are NOT in the ground truth. Creative prompts fabricated ~50-75%.
3. **Capability precondition (GO/NO-GO).** Verify the wake model solves the task at
   full context (oracle ~= 1.0 at every depth) before attributing failures to the
   strategy rather than raw capability.
4. **Paired stats, pure-python.** McNemar exact (binomial) + seed-cluster bootstrap
   (resample streams, not items) for paired binary outcomes — no scipy required.
5. **Query-agnostic by construction.** Build the consolidated memory BEFORE the query
   is sampled, structurally (not by promise), so "the consolidator just answered the
   question" is impossible.
6. **Honest-pivot discipline.** A pre-registered primary that disconfirms, a tautology
   exposed by an adversary, a negative result reported as a negative result — these
   are successes of the process, not failures of the study.

## Outcome artifacts

- Reference Context module `context-sleep` shipped (opt-in) to `amplifier-bundle-memory`.
- Integration recommendation: keep opt-in, do not default-promote (evidence doesn't
  support a reasoning win); the complementary value is a MemPalace bridge.
