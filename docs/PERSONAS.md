# Personas

Three users, different starting points, same destination: a defensible written artifact.

## Persona A — The non-scientist with a claim to defend

**Representative users:** patent attorney, policy analyst, product manager, technical founder, investigative journalist, due-diligence analyst, standards committee member.

**Starting state:** Has a claim they believe is true. Has never written IMRAD. Has possibly never heard of pre-registration. Uses the word "proven" loosely. Writes in paragraphs without explicit methodology. Cites sources inconsistently. Does not know what a p-value can and can't tell them.

**What they need:** The bundle translates their ordinary intent into rigorous scaffolding without condescending or demanding upfront literacy. They type their claim in plain English. The bundle asks clarifying questions that quietly serve as operationalization ("What specifically would count as success? What would count as failure?"). By the end, they have a document that survives scrutiny from a trained reader.

**Example journeys:**

- A patent attorney sketches an invention in a paragraph. Leaves with a USPTO-formatted brief that includes a defensible novelty claim, a prior-art table, and enablement-level detail.
- A policy analyst has a position on municipal AI guidance. Leaves with an evidence-based brief that cites real sources, separates "established" from "emerging," and names its own limitations.
- A technical founder has a pitch-deck claim about product ROI. Leaves with a white paper that either backs the claim with proper methodology or flags the claim as overreaching and suggests the defensible version.

**What the bundle does *not* do for this persona:** Make them a scientist. It makes the artifact defensible; it does not credential the author.

---

## Persona B — The working researcher

**Representative users:** ML researcher drafting a workshop paper, PI drafting a grant, staff engineer writing a technical report, PhD student drafting their first journal submission.

**Starting state:** Fluent in IMRAD. Has written papers before. Knows what pre-registration is in theory, may or may not practice it rigorously. Has strong domain intuitions and therefore at risk of letting shortcuts leak through — skipping power analysis, post-hoc rationalizing exploratory findings as confirmatory, forgetting to report null results.

**What they need:** Superpowers-style discipline enforcement. The bundle acts as a rigor co-pilot that refuses to let them skip steps they know they should take. Pre-registration gets a proper hash-locked artifact. The `honest-pivot` behavior flags the moment their analysis diverges from the plan. The `honest-critic` agent pushes back on weak limitations sections.

**Example journeys:**

- ML researcher with a working experiment runs `/critique` on their own draft and gets a structured list of the overclaims and missing ablations. Fixes before submission.
- PI drafting a grant uses `/question` → `/plan` → `/draft` to produce a methodologically tight Specific Aims section with pre-registered go/no-go criteria.
- PhD student writes the paper they thought they wrote — then the bundle's `scholar-eval` score at `/critique` time reveals the Methods section is underspecified, saving them from a desk reject.

---

## Persona C — The research-adjacent reviewer

**Representative users:** due-diligence partner, policy adviser, standards editor, patent examiner, grant reviewer, editorial board member.

**Starting state:** Doesn't generate claims. Evaluates them. Needs to read incoming artifacts quickly and identify the load-bearing claims, the methodology quality, and the gaps.

**What they need:** `/critique` as a standalone tool. Point it at an incoming document. Get back a structured evaluation: confirmatory vs exploratory separation, named limitations the original author missed, overclaim flags, CONSORT/STROBE/PRISMA checklist results, scholar-evaluation scores across rigor dimensions.

**Example journeys:**

- Due-diligence analyst receives a target company's technical white paper. Runs `/critique --input whitepaper.pdf`. Gets a memo identifying the three claims that need verification and the four that are clearly speculative.
- Grant reviewer receives a 12-page proposal. Runs `/critique --recipe grant-review`. Gets a structured evaluation that maps to the funder's scoring rubric.
- Patent examiner receives a brief. Runs `/critique --recipe prior-art-stress-test`. Gets the novelty argument stress-tested against public prior art the examiner can then verify.

---

## What's common across all three

All three personas share one trait: they need their artifact to survive scrutiny from someone smarter than them on the specific topic. The bundle's value is **pre-emptive defense** — running the scrutiny before the artifact leaves the author's hands.

The difference is only where they enter the pipeline. Persona A starts at `/question`. Persona B enters anywhere in the sequence depending on what they've already done. Persona C uses `/critique` standalone.

## What's explicitly not a persona

- **The autonomous researcher who wants to be hands-off.** That's Denario's persona. This bundle requires human judgment at every mode transition.
- **The student looking to have homework done for them.** The bundle refuses to be a homework engine. Recipes require the user to commit to claims; the bundle enforces honesty about whether those claims are supported.
