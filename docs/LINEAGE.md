# Lineage

This bundle stands on four other people's work. Naming them explicitly, because the design is deliberate borrowing.

---

## [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)

**What we take:** The skill library itself. Ten of the 134 skills — `hypothesis-generation`, `scientific-critical-thinking`, `statistical-analysis`, `peer-review`, `scholar-evaluation`, `scientific-writing`, `scientific-schematics`, `citation-management`, `venue-templates`, `scientific-brainstorming` — cover the full paper lifecycle from question formulation to venue formatting. The bundle does not fork or vendor these; it references them upstream.

**What we add:** Orchestration. K-Dense's 134 skills are narrow and unopinionated by design — that's the right call for a skill library. A working researcher still has to know *which* skills to compose, in *which* order, with *which* defaults. The bundle does that composition.

**Credit:** K-Dense Inc. License of upstream skills applies.

---

## [Denario](https://github.com/AstroPilot-AI/Denario)

**What we take:** The multi-agent topology. Denario's modules (idea → literature → plan → execute → paper → review) map almost 1:1 to our modes, because the underlying lifecycle is the same. The insight that a research system benefits from specialized agents per phase — rather than one generalist agent — is Denario's and is correct.

**What we do differently:** Denario targets *autonomous* research where AI is the primary author. This bundle explicitly keeps the human as primary author. Denario produces a paper from a problem statement; this bundle produces a paper *with the human making the substantive calls* at each mode transition.

**Credit:** Pablo Villanueva-Domingo, Francisco Villaescusa-Navarro, Boris Bolliet. GPL-3 / Apache 2 as applicable to any code we borrow (none yet — we borrow design only).

---

## [Superpowers](https://github.com/obra/superpowers) + [amplifier-bundle-superpowers](https://github.com/microsoft/amplifier-bundle-superpowers)

**What we take:** The process-discipline pattern. Superpowers enforces `/brainstorm → /write-plan → /execute-plan → /verify → /finish` for software development. This bundle applies the same pattern — *design before execution, lock the plan, verify against the plan, report honestly* — to scientific research. The structure transfers cleanly because the underlying virtue is the same: disciplined workflow beats improvisation.

**What we do differently:** Different domain, different agents, different verification criteria. Software verification means tests pass; research verification means the analysis matches the pre-registration.

**Credit:** Jesse Vincent (Superpowers methodology). Microsoft Amplifier team (bundle packaging). The inspiration for this bundle's existence, especially the mode-driven UX.

---

## [amplifier-bundle-stories](https://github.com/michaeljabbour/amplifier-bundle-stories)

**What we take:** The UX bar. Install is one command. First run requires zero configuration. Recipes handle the 80% case out of the box. A non-expert can produce an artifact in their first session without reading docs.

**What we match:** File layout, bundle.md conventions, README structure, recipe YAML shape.

**Credit:** Michael Jabbour (author). This bundle targets the same user ease as stories; if we land meaningfully above or below that bar, it's a bug.

---

## `amplifier-bundle-scientificpaper` (Michael Jabbour, 2025)

**What we take:** Craft material. The earlier bundle is a substantially more implemented piece of work on the narrow problem of academic-paper production. We absorb its content:

- Six conference format specifications (NeurIPS, ICML, ACL, IEEE, ACM, arXiv) — now in `references/conference-formats/`
- Matplotlib-scientific and TikZ/PGFPlots reference material — now in `references/imaging/`
- PaperBanana figure-generation methodology (arXiv 2601.23265) — now in `references/figure-generation/`
- Python scripts for deterministic operations (LaTeX compilation, format validation) — now in `scripts/`
- Writing-craft content from the `paper-architect` agent: 5-component abstract framework, section flow principles, active-voice and precision-of-claim patterns — absorbed into our `technical-writer` agent
- The `approval_required` / `approval_prompt` pattern from their `paperbanana-figure.yaml` recipe — adopted for our recipe schema at mode boundaries

**What we do differently:**

- Broader scope. Their bundle targets academic-paper production; ours covers patent briefs, policy briefs, white papers, replication studies, grants, and more alongside papers.
- Three-persona framing (non-scientist / researcher / reviewer) rather than an implicit researcher audience.
- Mode-based UX (`/question`, `/plan`, `/execute`, `/critique`, `/draft`, `/publish`) rather than keyword-triggered agent routing.
- Pre-registration discipline (hash-locked preregistration, `honest-pivot` behavior, `exploratory-labeling`) — core differentiator not present in the earlier bundle.
- Methodology critique via GRADE / Cochrane ROB / CONSORT / STROBE / PRISMA — the earlier bundle's critique is structural-only.

**Credit:** Michael Jabbour (author). The earlier bundle is the direct ancestor of this one. The content in `references/` was written for that bundle and is reused here under the same license. See `docs/GAP_ANALYSIS.md` for the full merge analysis.

**PaperBanana acknowledgment:** The figure-generation methodology cited in `references/figure-generation/paperbanana-methodology.md` is original research by Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister, and Jinsung Yoon (Peking University / Google Cloud AI Research), published at arXiv 2601.23265. Their work is credited as the source of the 8 quality veto rules and the 5-agent multi-stage refinement architecture.

---

## Amplifier itself

**What we rely on:** The runtime, module system, session management, provider routing, agent-delegation mechanism, and bundle loader. This bundle is pure configuration on top of Amplifier; it ships no runtime modules of its own.

**Credit:** Microsoft Amplifier team. The bundle would not exist without the host.

---

## The broader ecosystem

Papers, tools, and ideas that shaped the thinking:

- **The AI Scientist / AI Scientist-v2** (Sakana, UBC, Oxford) — published in *Nature*, 2026. Demonstrated that end-to-end autonomous paper generation is possible. Sharpened our thinking about what *not* to automate: the substantive judgment calls.
- **CONSORT, STROBE, PRISMA** reporting guidelines — the baseline for methodology transparency. `honest-critic` references these directly.
- **GRADE, Cochrane Risk of Bias** — evidence-quality frameworks, embedded in `methodologist` and `honest-critic`.
- **OSF pre-registration** standards — the model for our pre-registration artifact.
- **Reflection Tokens, ROI on Inference, and the RCE benchmark** — in-progress research programs by the author whose methodology discipline this bundle codifies and generalizes; the RCE benchmark is this bundle's planned primary evaluation target.

---

## What's original here

The bundle's contribution is not any single layer. It's the composition:

- A specific ten-skill subset (not all 134)
- Mapped to eight agents (not one, not one-per-skill)
- Behind six modes (not the raw agent list)
- Composed into seven recipes (not an open-ended recipe space)
- With two honesty-enforcing behaviors (novel — not present in Denario or Superpowers)
- Packaged for one-command install (matching stories)
- Sized for non-expert users as primary audience (distinct from Denario and Superpowers)

Everything else is borrowed, credited, and better for it.
