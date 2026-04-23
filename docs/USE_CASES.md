# Use Cases

Concrete examples of what the bundle produces, shaped to five representative output types. Each shows input, output structure, and which modes do the heavy lifting.

---

## 1. Patent brief

**Input:** An inventor or patent attorney with a rough invention description.

**Example trigger:**
```bash
amplifier run --recipe patent-brief \
  "Rolling-ROI control — a closed-loop runtime governance system
   that adjusts per-session AI agent compute based on realized
   task value, using a feedback loop between a session-level
   value estimator and a compute allocator."
```

**What happens:**

| Mode | What the bundle produces |
|---|---|
| `/question` | Sharpens invention to a set of falsifiable claims — what problem does it solve, what is novel, what is non-obvious |
| `/plan` | Pre-registration of: prior-art search strategy, enablement experiments (if any), claim chart structure |
| `/execute` | Prior-art search across USPTO, Google Patents, arXiv; candidate references in a claim-by-claim matrix |
| `/critique` | Novelty stress test, enablement stress test (could a person having ordinary skill in the art build it from the description?), overclaim detection |
| `/draft` | USPTO-style structure: Field of Invention / Background / Summary / Detailed Description / Claims / Abstract + architecture diagrams |
| `/publish` | USPTO-ready DOCX and PDF with proper formatting, drawings folder, claim numbering |

**Defensibility check:** The brief must survive `/critique` with zero overclaim flags on the independent claims before `/publish` produces final output.

---

## 2. Policy brief

**Input:** A policy analyst with a position to defend.

**Example trigger:**
```bash
amplifier run --recipe policy-brief \
  "Municipal guidance on generative AI in K-12 classrooms
   should default to teacher-mediated use rather than student
   direct access, through end of middle school."
```

**What happens:**

| Mode | What the bundle produces |
|---|---|
| `/question` | Separates the position into load-bearing claims: developmental appropriateness, teacher capacity, equity implications, measurable outcomes |
| `/plan` | Evidence-gathering strategy: research base, comparable policies, stakeholder input categories. Commits to what counts as disconfirming evidence |
| `/execute` | Systematic evidence gather: peer-reviewed sources on developmental psychology, ed-tech policy, classroom AI studies; organized by claim |
| `/critique` | Flags claims supported by weak evidence, names counter-positions fairly, identifies where the analyst's position goes beyond what evidence supports |
| `/draft` | Structure: Executive summary / Context / Recommendation / Evidence base / Counter-arguments considered / Implementation / Limitations |
| `/publish` | Policy-brief format: 2-page executive, 6-page full, citations in footnotes, plain language for non-specialist reader |

**Defensibility check:** Draft includes an explicit Counter-Arguments section that the original analyst did not write; `honest-critic` scores it as fair representation, not strawman.

---

## 3. White paper

**Input:** A founder or principal engineer with a technical thesis.

**Example trigger:**
```bash
amplifier run --recipe white-paper \
  "Return on Inference: when does spending more on model calls
   actually pay back? A framework for measuring the break-even
   point for AI-assisted work."
```

**What happens:**

Same six-mode sequence; `/execute` runs analysis or benchmarks if data is available; `/draft` uses a technical-white-paper skeleton rather than IMRAD; `/publish` produces a properly typeset PDF with figures and a reference list.

**Differentiation from marketing content:** The bundle's `honest-critic` refuses to let the paper make claims without evidence. The white paper either says what its evidence supports or says "we hypothesize X and would test Y." Marketing departments that want aspirational claims will not like this bundle; that is intentional.

---

## 4. Empirical research paper

**Input:** A researcher with a hypothesis, a dataset or experimental plan, and a target venue.

**Example trigger:**
```bash
amplifier run --recipe empirical-paper --venue neurips \
  "Reflection tokens, when inserted at trained intervals during
   long-horizon generation, improve task-completion rates
   relative to standard decoding."
```

**What happens:**

The canonical full lifecycle. Pre-registration at `/plan` is hash-locked with SHA256; the `preregistration-reviewer` agent refuses to let the user proceed until predictions and analysis tests are specific enough to be falsifiable. `honest-pivot` fires if the analysis diverges from the plan. `/publish` emits venue-compliant LaTeX (NeurIPS, ICML, ICLR, Nature, etc.).

**Differentiation from Denario:** The researcher runs the experiment — the bundle doesn't try to. The bundle's job is the methodology, the analysis rigor, the draft, and the venue formatting.

---

## 5. Replication study

**Input:** A researcher or reviewer trying to reproduce a prior paper's results.

**Example trigger:**
```bash
amplifier run --recipe replication-study \
  --source-paper "https://arxiv.org/abs/2501.xxxxx" \
  --data "./our-replication-data/"
```

**What happens:**

Enters at `/plan`, not `/question` — the question is borrowed from the source paper. The bundle extracts the original's claims, predictions, and analysis plan; locks a pre-registration that matches (or deliberately deviates with documented reasons); runs the analysis; and produces a replication report that uses the same structure as the original for comparability.

**Defensibility check:** The report either replicates the original's findings with honest confidence intervals, or fails to replicate — and the bundle refuses to let the author soften the null. `honest-pivot` is at its strongest here.

---

## 6. Grant application

**Input:** A PI with an idea and a funder.

**Example trigger:**
```bash
amplifier run --recipe grant --funder nsf-cise \
  "Functional agency in human-AI collaboration: a causal study"
```

**What happens:**

Enters at `/question`. `/plan` produces pre-registered go/no-go criteria for each specific aim. `/execute` in grant mode is the literature and feasibility review. `/critique` runs the proposal through the funder's published scoring rubric. `/draft` produces the full application in the funder's structure. `/publish` formats to the funder's template (NSF, NIH, DARPA, DoD, EU Horizon).

**Differentiation from "grant-writing AI" tools:** The bundle does not optimize for scoring well; it optimizes for proposing defensible, methodologically sound science. Reviewers can tell the difference.

---

## What ties these together

Six modes. Eight agents. Ten skills. The recipe picks the template and the emphasis. The discipline is identical.

This is the bundle's core thesis: **rigor is one capability, not six.** A patent examiner and a physics PI both need the same underlying discipline — precise questions, locked methods, honest critique, proper sourcing, appropriate venue format. The bundle serves both by being stable where it should be and configurable where it must be.
