# Session History — amplifier-bundle-research

How this bundle came to exist, told chronologically across sessions.

---

## Session 1 — Claude Chat (claude.ai)

**Date:** April 22, 2026, 1:27 PM – 5:09 PM
**Platform:** Claude chat (claude.ai), model: Claude
**Chat ID:** `c31b5ecd-ff7e-4ccd-a4e6-989051dce0a1`
**Duration:** ~4 hours
**Operator:** MJ (Michael Jabbour)

### What happened

MJ opened with a deceptively simple question: "What are the absolutely essential 3 process steps required to write a scientifically sound paper? And what are the 3 most essential formatting in LaTeX steps?"

Claude answered with six essentials:

1. Lock the question and analysis plan before seeing the data
2. Make methods reproducible at the artifact level
3. Calibrate claims to evidence and report against yourself
4. Document class + correct package stack (LaTeX)
5. Structural scaffolding with labeled floats and cross-refs (LaTeX)
6. Bibliography via a `.bib` file, not inline (LaTeX)

MJ then pivoted: "Are there any skills out there that do all six?" He referenced the [K-Dense scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) bundle (134 skills) he'd already installed, noting he was actively using `scientific-writing` and `scientific-critical-thinking`.

### The gap discovery

Claude researched the landscape — K-Dense, [Denario](https://github.com/AstroPilot-AI/Denario) (Simons Foundation multi-agent research system), and [Sakana AI Scientist-v2](https://github.com/SakanaAI/AI-Scientist-v2) (published in Nature, March 2026). The finding: no single skill or bundle covered all six. K-Dense has the pieces but they're narrow and composable. Denario and AI Scientist are full autonomous pipelines, but they're "AI as primary author" — the opposite of what MJ needed.

MJ then asked the key question: "But nothing like `amplifier-bundle-superpowers` for hypothesis testing and paper writing?"

Claude audited the entire `microsoft/amplifier-bundle-*` namespace. The answer was no — superpowers (TDD/software engineering), stories (narrative writing), design-intelligence (UI/UX), attractor (DAG pipelines), various LSP bundles — none targeting research. **The gap was confirmed and named: `amplifier-bundle-research`.**

### The reframe

Claude's original "6 essentials" was uneven — 3 process steps + 3 LaTeX tactics. MJ pushed to revisit them as proper competencies. The reframe produced six lifecycle competencies that each fail independently:

1. **Question design** — formulate falsifiable, operationalized questions
2. **Methodology & pre-registration** — lock before data
3. **Execution & reproducibility** — deterministic pipelines
4. **Honest self-critique** — separate confirmatory from exploratory
5. **Clear technical writing** — IMRAD, figures, precise prose
6. **Venue-appropriate publication** — LaTeX, citations, format

These mapped 1:1 to six modes: `/question → /plan → /execute → /critique → /draft → /publish` — the Superpowers pattern exactly.

### The build

MJ asked Claude to restructure everything into a spec. Key design constraints:

- **Four influences:** K-Dense (skill layer), Denario (multi-agent topology), Superpowers (process discipline), Stories (install ergonomics)
- **Non-scientist users are primary:** Patent attorneys, policy analysts, founders — not just researchers
- **Three personas:** A (non-scientist), B (researcher), C (reviewer)
- **Output ladder:** Patent brief → policy brief → white paper → empirical paper → grant → replication study

Claude produced 36 files: full spec, architecture, personas, use cases, UX mockup, lineage, roadmap, bundle manifest, one canonical agent (hypothesis-designer), one canonical mode (question), one canonical recipe (patent-brief), one canonical behavior (honest-pivot), one canonical template (preregistration). The rest were stubs showing the pattern.

### The scientificpaper merge

MJ also had an earlier bundle — `amplifier-bundle-scientificpaper` — sitting in `~/dev/`. This was a substantially more implemented bundle (~20K lines) focused specifically on academic paper writing, with:

- 4 rich agents (paper-architect at 873 lines, figure-artist at 1720 lines, latex-expert at 390 lines, citation-manager at 1122 lines)
- PaperBanana multi-agent figure generation (arXiv 2601.23265) with 8 quality veto rules
- 6 conference format specs (NeurIPS, ICML, ACL, IEEE, ACM, arXiv)
- Actual LaTeX templates (ACL, IEEE style files)
- Python tool module for figure generation
- Utility scripts (compile, validate, download templates, generate figures)

Claude did a gap analysis. The merge strategy: keep research's architectural frame (modes, personas, output ladder, pre-registration discipline), absorb scientificpaper's content (agent craft knowledge, templates, scripts, context files).

A delta zip was produced with 22 files — the new additions and one modified file (LINEAGE.md with scientificpaper credits).

### Session 1 ended with:

- 36-file skeleton downloaded to `~/dev/amplifier-bundle-research/` (but flattened — directory structure lost during download)
- Delta zip downloaded to `~/Downloads/delta/` (never merged)
- `~/dev/amplifier-bundle-scientificpaper/` untouched
- Handoff instructions written for Copilot/Amplifier to execute the v0.1.1 and v0.2 work items from the GAP_ANALYSIS

### What went wrong in Session 1

1. The 36-file download lost the directory structure — all files ended up flat in the root, no `docs/`, `agents/`, `modes/` subdirectories
2. The delta was never merged into the main folder
3. The `present_files` call only highlighted 3 files, which MJ reasonably interpreted as "you want me to replace 51 files with 3" — a miscommunication
4. Claude couldn't write directly to MJ's filesystem from the chat sandbox
5. The handoff to Copilot was described but never executed

---

## Session 2 — Cowork (this session)

**Date:** April 22, 2026, evening
**Platform:** Cowork (Claude desktop app), model: Claude Opus 4.6
**Operator:** MJ

### What happened

MJ attached the full Session 1 transcript, exported from claude.ai as `Claude-Essential steps for writing scientific papers and LaTeX formatting.md` (named after the first message in that chat). This file contains the complete conversation — every prompt, every response, every web search result, and every thinking trace from Session 1. MJ asked the new Claude to read it end-to-end and pick up where things left off.

### Starting state

- `~/dev/amplifier-bundle-research/` — 14 flat files (no directory structure, no delta merged)
- `~/dev/amplifier-bundle-scientificpaper/` — the original experiment, untouched (~70 source files + LaTeX templates)
- `~/Downloads/delta/` — 16 files from Session 1's gap analysis, never applied

### What this session did

Unlike Session 1 (chat sandbox, no filesystem access), Cowork has direct read/write access to mounted folders. All three directories were mounted.

**Step 1 — Restructure.** Moved the 14 flat files into proper subdirectories: `docs/`, `agents/`, `modes/`, `behaviors/`, `recipes/`, `templates/`.

**Step 2 — Merge.** Copied content from both sources:
- From `delta/`: GAP_ANALYSIS.md, updated LINEAGE.md
- From `scientificpaper/`: all context files (conference formats, imaging refs, PaperBanana methodology), behaviors, recipes (paperbanana-figure), references (LaTeX style guides), scripts, modules (tool-paperbanana Python package), templates (ACL + IEEE LaTeX), .gitignore, LICENSE, requirements.txt

**Step 3 — Write all agents.** 10 agents, 4,951 total lines:
- 5 absorbed from scientificpaper with broadened scope: technical-writer (absorbed paper-architect), figure-designer (absorbed figure-artist), venue-formatter (absorbed latex-expert), citation-manager (absorbed citation-manager), honest-critic (new, wraps peer-review + scholar-evaluation)
- 4 entirely new: preregistration-reviewer, methodologist, statistician, research-coordinator
- 1 kept as-is: hypothesis-designer

**Step 4 — Write all modes.** 6 modes, 1,597 total lines:
- question (kept from Session 1)
- plan, execute, critique, draft, publish (all new, all persona-aware)

**Step 5 — Write all recipes.** 9 recipes, 1,147 total lines:
- patent-brief (kept from Session 1)
- paperbanana-figure (from scientificpaper)
- policy-brief, white-paper, empirical-paper, benchmark-paper, replication-study, grant-proposal, literature-review (all new)

**Step 6 — Write behaviors, templates, context.** Expanded exploratory-labeling from stub to full spec. Wrote IMRAD LaTeX skeleton, patent brief template, policy brief template. Rewrote context/instructions.md for the 10-agent research bundle.

**Step 7 — Update docs.** Bumped bundle.md to v0.2.0, added all new agents/recipes/behaviors to manifest, updated README with full inventory, fixed all template path references.

**Step 8 — Verify.** Every reference in bundle.md resolves to an actual file. 10/10 agents, 6/6 modes, 9/9 recipes, 6/6 behaviors, 4/4 templates. Zero orphans, zero broken paths.

### Ending state

128 files, ~59,000 lines. Fully specified and implemented v0.2.0 bundle in `~/dev/amplifier-bundle-research/`.

---

## Key decisions made across sessions

| Decision | Where made | Rationale |
|---|---|---|
| Name: `research` not `scientificpaper` | Session 1 | Broader — patent attorneys and policy analysts aren't writing "scientific papers" but are doing research |
| Six modes, not four or eight | Session 1 | 1:1 with Superpowers pattern; each can fail independently |
| Non-scientist as Persona A (primary) | Session 1 | The bundle's distinctive value — rigor without formal training |
| Keep humans as primary author | Session 1 | Opposite of Denario/AI Scientist's autonomy-heavy approach |
| Absorb scientificpaper content, keep research frame | Session 1 | Research has the right architecture; scientificpaper has the right content |
| honest-pivot on by default | Session 1 | Core value proposition — override requires explicit acknowledgment |
| K-Dense skills lazy-loaded | Session 1 | Zero context tax for browsing; agents pull on demand |
| 10 agents (split citation-manager out) | Session 2 | GAP_ANALYSIS recommended; cleaner separation of concerns |
| research-coordinator as orchestration agent | Session 2 | Needed for recipe execution and honest-pivot enforcement across modes |

---

## Source material locations

| What | Where |
|---|---|
| Session 1 transcript | `docs/session-1-transcript.md` (originally exported from claude.ai as `Claude-Essential steps for writing scientific papers and LaTeX formatting.md`, chat ID `c31b5ecd-ff7e-4ccd-a4e6-989051dce0a1`) |
| Original scientificpaper bundle | `~/dev/amplifier-bundle-scientificpaper/` |
| Delta from Session 1 | `~/Downloads/delta/` (now merged into research) |
| Final research bundle (v0.2.0) | `~/dev/amplifier-bundle-research/` |
| K-Dense scientific-agent-skills | [github.com/K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) |
| Denario | [github.com/AstroPilot-AI/Denario](https://github.com/AstroPilot-AI/Denario) |
| Superpowers | [github.com/microsoft/amplifier-bundle-superpowers](https://github.com/microsoft/amplifier-bundle-superpowers) |
| Stories | [github.com/michaeljabbour/amplifier-bundle-stories](https://github.com/michaeljabbour/amplifier-bundle-stories) |
