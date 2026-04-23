# Handoff — amplifier-bundle-research v0.4.0

**Date:** April 22, 2026 (v0.3 verification + v0.4 simulated persona acceptance)
**Published:** https://github.com/michaeljabbour/amplifier-bundle-research
**Verified:** Bundle loads from git URL. All 6 modes register as slash commands. Five v0.3 programmatic tests PASS. Three v0.4 simulated persona acceptance tests PASS. Ready for real-user testing (post-v0.4) and the v1.0 dogfood paper.

---

## Current state

**Bundle is published, loadable from git, and has passed both v0.3 programmatic verification and v0.4 simulated persona acceptance.** Real human-in-the-loop validation is the next milestone (tracked as post-v0.4).

**Public install:**
```bash
amplifier bundle add --app git+https://github.com/michaeljabbour/amplifier-bundle-research@main
amplifier bundle use research
amplifier
```

**Local development** (from a clone):
```bash
git clone https://github.com/michaeljabbour/amplifier-bundle-research.git
cd amplifier-bundle-research
amplifier bundle add "file://$(pwd)" --name research-dev
amplifier run --bundle research-dev --mode chat "your prompt here"
```

### Inventory (v0.4.0)

| Layer | Count | Status |
|---|---|---|
| Agents | 10 | Valid `meta:` frontmatter, `model_role`, common-agent-base footer |
| Modes (runtime) | 6 | All register as slash commands: `/question`, `/study-plan`, `/execute`, `/critique`, `/draft`, `/publish` |
| Recipes | 9 | 8 mode-pipeline recipes have `publish_gates:`; paperbanana-figure is staged |
| Behaviors | 7 | Six domain + composite + research-modes wiring |
| Standalones | 1 | `bundles/dev.yaml` |
| Context files | 17 | Instructions + 6 conference formats + 3 venue formats + imaging + paperbanana + awareness files |
| Templates | 32+ | Including Round 4 reproducibility stack: `environment.yml`, `requirements.in/.txt`, `Dockerfile.research`, `REPRODUCIBILITY.md`, `execution-log.yaml`, `evidence-log.yaml` |
| Scripts | 4 | `compile_latex.py` (arxiv default, compiles cleanly), `validate_format.py`, `generate_figure.py`, `download_templates.py` (ACL + IEEE + ACM via CTAN; NeurIPS + ICML manual-download-instructed) |
| Modules | 1 | `tool-paperbanana` — protocol-compliant (all 8 checklist boxes), pip-installable, import-verified |
| Docs | 11 | SPEC (v0.4.0), ARCHITECTURE, PERSONAS, USE_CASES, UX_MOCKUP, LINEAGE, ROADMAP, GAP_ANALYSIS, SESSION_HISTORY, HANDOFF, session-1-transcript |
| Structural diagram | 2 | `bundle.dot` + `bundle.png` (source_hash tracks v0.4.0) |

---

## Release history

| Tag | Commit | Date | Scope |
|---|---|---|---|
| v0.2.0 | `fc8ba42` | Apr 22, 2026 | Initial public release (Rounds 1–4) |
| (fix) | `e581cd2` | Apr 22, 2026 | v0.3 verification fixes for LaTeX compile + template download |
| v0.4.0 | (this) | Apr 22, 2026 | v0.3 + v0.4 closeout: programmatic verification + simulated persona acceptance |

---

## How the bundle came to load + engage + ship

Six rounds produced v0.4.0.

### Round 1: Authoring
Two earlier sessions (claude.ai + Cowork). 128 files, ~59K lines. Content absorbed from `amplifier-bundle-scientificpaper`. See `docs/SESSION_HISTORY.md`.

### Round 2: Hardening
`amplifier-expert` guidance applied. `bundle.md` → valid frontmatter; behaviors composite created; 4 scientificpaper-inherited behaviors cleaned; 3 stale awareness files rewritten; 5 missing templates written; 10 agents got `meta:` frontmatter + `model_role` + common-agent-base footer; `bundles/dev.yaml` standalone; metadata absorbed into `context/instructions.md`; `bundle.dot` + `bundle.png` generated; SPEC version bumped.

### Round 3: Post-review blocker fixes
8 items surfaced by parallel `amplifier-expert` + `foundation-expert` reviews. `honest-pivot.md` + `exploratory-labeling.md` got frontmatter; `bundle.md` agent paths → short-name form; `bundles/dev.yaml` provider URL → namespace form; recipes/paperbanana-figure.yaml 7 stale refs fixed; 4 domain behaviors got unique `bundle.name`; 16 `@scientificpaper:` refs across 9 context files fixed; `tool-paperbanana` protocol-compliant; 3 straggler old agent-name refs fixed.

### Round 4: Modes engagement + v0.3 priorities
Mode registration wired per `amplifier-expert` guidance: 6 mode files got `mode:` frontmatter; `behaviors/research-modes.md` created with `hooks-mode` + `tool-mode`; `/plan` renamed to `/study-plan` (collision with `modes` bundle's `/plan`). v0.3 priority work: reproducibility hardening (7 templates), critique-as-publish-gate (8 recipes), non-academic publish paths (USPTO, policy-memo, NSF/NIH grant specs). Pre-push cleanup: PII sweep clean, README rewritten, `.gitignore` hardened. Published to GitHub as v0.2.0.

### Round 5: v0.3 verification + bug fixes
Five programmatic tests run:

| Test | Result |
|---|---|
| `tool-paperbanana.mount()` returns Tool-protocol-compliant tool | ✅ PASS (`name`, `description`, `input_schema`, `execute()` all verified) |
| `scripts/compile_latex.py templates/imrad-skeleton.tex` | ❌→✅ `bug-hunter` fixed: `%TITLE%` placeholders were LaTeX comment-eaters; default format swapped to `arxiv`; `\bibliography` commented until user has `.bib`. Now produces 82KB PDF. |
| `scripts/download_templates.py --all` | ⚠→✅ `bug-hunter` fixed: NeurIPS 403 (Cloudflare) downgraded to manual-download-required; ACM 403 swapped to CTAN mirror; `manual_fallback` field added per source. |
| Bundle smoke test (`/question` + sharpened_question output) | ✅ PASS (97-line sharpened_question YAML with claim frame, predictions, disconfirmation, scope, 4-class novelty note) |
| Bundle `/study-plan` smoke test (Persona A patent-brief) | ✅ PASS (57-line preregistration YAML with prior-art search plan, enablement demo, honest-pivot clause, abandonment criteria) |

Round 5 bug fixes committed and pushed as `e581cd2`.

### Round 6: v0.4 simulated persona acceptance tests

Three bounded simulations, each exercising one persona archetype end-to-end:

**Persona A — Patent attorney (non-scientist):** `/question` + `/study-plan` on a rolling-ROI patent claim. Produced plain-language sharpened question + patent-schema preregistration with prior-art search plan (USPTO + Google Patents + arXiv with specific CPC classes), enablement demo (SWE-bench-lite baseline comparisons), honest-pivot clause (three narrowing branches), disconfirmation/abandonment criteria. Proactively flagged two clarifications before proceeding. **✅ PASS** — Persona A entry path usable.

**Persona B — ML researcher (discipline terminology):** `/question` on a reflection-tokens empirical claim. Used correct statistical vocabulary throughout (pass@1, McNemar test, BH-FDR, TOST equivalence, mixed-effects logistic regression, KV-cache, stride ablation). Produced 50-line sharpened YAML with 3 operationalized predictions including item-level paired design, filler-matched baseline, horizon×condition interaction. 5-criterion disconfirmation with multiplicity control. Scope with explicit non-applicability to multi-pass/agentic/RAG settings. Novelty note distinguishing from Reflexion/Self-Refine at the token-schedule vs trajectory-control axis. Methodologist advisory folded 5 residual risks into the frame. Proactively asked about the fixed-interval trigger rule (token stride vs sentence boundary). **✅ PASS** — Persona B methodological rigor delivered.

**Persona C — Peer reviewer (standalone /critique):** `/critique` on a deliberately-flawed reflection-tokens draft with overclaiming, missing methodology, no stats, and generic limitations. Produced critique YAML with severity-labeled findings, scholar-eval scores (methodology 1/5, evidence 1/5, clarity 2/5, novelty 2/5), REFORMS-ML checklist (8/8 MISSING), CONSORT-AI analog (outcome pre-specification + sample size + blinding all MISSING). Correctly identified PRISMA/STROBE as non-applicable and chose REFORMS as the right framework. 3 concrete remediation asks (effort + rationale). Summary verdict: WEAK. Correctly refused forward progress with 4 BLOCK items. **✅ PASS** — Persona C evaluator path usable.

**All three personas delivered outputs genuinely useful to their target users.** The bundle's persona-aware behavior routed correctly without prompting; `honest-critic` and `preregistration-reviewer` activated appropriately; the mode contract held (no premature /execute; no auto-handoff without confirmation).

---

## Operating the bundle

### Invoking recipes (natural language works best)

```bash
# The research-coordinator handles natural-language invocation:
amplifier run --bundle research --mode chat \
  "Run the patent-brief recipe on: Novel rolling-ROI control for AI agent sessions"

# Or direct recipe tool invocation:
amplifier tool invoke recipes operation=execute \
  recipe_path=@research:recipes/patent-brief.yaml \
  'context={"invention": "Novel rolling-ROI control for AI agent sessions"}'

# `--recipe <name>` flag does NOT exist in amplifier CLI. Use above forms.
```

### The 6 slash commands

- `/question` — sharpen a rough claim into a falsifiable research question
- `/study-plan` — design methodology + hash-lock the pre-registration (renamed from `/plan` to avoid collision with `amplifier-bundle-modes` default)
- `/execute` — run analysis / prior-art search / evidence gather per the locked plan
- `/critique` — structured critique (CONSORT/STROBE/PRISMA/REFORMS as appropriate)
- `/draft` — venue-appropriate document
- `/publish` — format, compile, submission-ready-package (blocks until `/critique` passes and honest-pivots acknowledged)

First mode activation hits a warn gate (standard modes-bundle behavior) — retry to confirm. Use `/mode off` to deactivate.

### tool-paperbanana (figure generation)

Install once:
```bash
cd modules/tool-paperbanana && pip install -e .
```

Requires `GOOGLE_API_KEY` with Imagen 4 access (~$0.04/image). Protocol-compliant; `mount()` verified; execute path uses the 5-stage PaperBanana pipeline (arXiv 2601.23265).

### Scripts

```bash
# Compile a LaTeX paper (defaults to arxiv; pass --format neurips / icml / acl / ieee / acm)
python scripts/compile_latex.py templates/imrad-skeleton.tex

# Download conference templates (ACL, IEEE, ACM via CTAN work automatically;
# NeurIPS and ICML print manual-download instructions)
python scripts/download_templates.py --all

# Validate a .tex against a venue before submission
python scripts/validate_format.py your-paper.tex --format neurips --strict

# Generate a publication-ready figure (matplotlib-based; not the paperbanana pipeline)
python scripts/generate_figure.py training
```

---

## What's NOT done

### Post-v0.4 — Real-user validation

The v0.4 persona tests were SIMULATED (one Amplifier session exercising each persona archetype with realistic inputs). They proved the bundle produces persona-appropriate outputs with correct structure. They did NOT prove:

- Whether a real patent attorney finds the `/study-plan` preregistration workflow intuitive or friction-heavy
- Whether a real working researcher would choose this bundle over writing a preregistration manually
- Whether a real peer reviewer's critique session converges faster/better with `/critique` vs without

These are empirical questions that require real humans with real work. Scheduled as:

1. **Persona A real-user test** — patent attorney + real invention. Measure: minutes-to-useful-sharpened-question, attorney's confidence rating of the output, whether the preregistration becomes the prior-art search plan or gets discarded.
2. **Persona B real-user test** — working ML researcher + real paper draft. Measure: does the preregistration survive peer review, does `honest-pivot` fire and get acknowledged, does the final paper compile correctly.
3. **Persona C real-user test** — peer reviewer + real submitted paper. Measure: does `/critique` output match what the human reviewer would have written; does applying REFORMS-ML/CONSORT-AI surface gaps the human missed.

### v1.0 — Dogfood paper + GitHub release tagging

- **Dogfood paper.** The first artifact this bundle produces should be the paper *about* this bundle, measured on the RCE benchmark. See `docs/ROADMAP.md`.
- **GitHub release.** Tag `v0.4.0` on the current commit. Tag `v1.0.0` after the dogfood paper is published.

### Post-v1.0 roadmap

1. **Domain packs.** Medical (IRB, CONSORT), legal (patent prosecution detail), social science (STROBE, survey design).
2. **Multi-author support.** CRediT taxonomy, co-author review loops.
3. **Review-round support.** R&R response drafting with equal rigor to the original paper.
4. **Reference-manager MCP.** Zotero / Mendeley connector.

### Verification asks (non-blocking)

- **USPTO / NSF / NIH rules** in `context/venue-formats/*.md` have `<!-- TBD: verify -->` markers where 2024/2025 rules may have drifted. A reviewer with current MPEP / PAPPG access should walk the three files.
- **Execution log combined-hash format** in `modes/execute.md` is defined as `sha256(execution_log_sha256 || preregistration_sha256)`. Confirm once dogfood paper commits to a specific convention.
- **Override flag names** (`--allow-data-hash-mismatch` etc.) coined during Round 4. Align with whatever Amplifier adopts canonically.
- **NeurIPS style-file URL rot** — `neurips.cc/Conferences/2024/PaperInformation/StyleFiles` 404s. Overleaf template URL is the more durable reference in the manual-download instructions.

---

## Known constraints (live, not bugs)

### /study-plan slash command (not /plan)

The research bundle's plan mode registers as `/study-plan` — not `/plan` — to avoid collision with the default `/plan` mode shipped by `amplifier-bundle-modes`. Per `hooks-mode`'s first-load-wins rule, the modes bundle wins. `research-coordinator` routes natural-language "plan" requests to `/study-plan` regardless. Prose throughout the bundle uses "the plan mode" as shorthand.

### Composition with other bundles

If a consumer loads `research` alongside another bundle that also mounts `hooks-mode` with its own `search_paths` (e.g., `amplifier-bundle-superpowers`), the deep-merge implementation replaces lists rather than concatenating. One bundle's modes will win, the other's will be silently dropped. Fix pattern: a wrapper bundle that declares `hooks-mode` once with all desired search_paths together. See parallax-discovery for the canonical example.

### Architectural debt (deferred, non-blocking)

- **Thin-bundle partial violation.** `bundle.md` declares all 10 agents directly; canonical pattern is behavior-only. 3 agents declared 3× (root + 2 behaviors).
- **`tool-paperbanana` pyproject.toml name** doesn't follow `amplifier-module-tool-*` convention. Cosmetic; entry point is correct.
- **Mode `plan.md` file is named `plan.md` on disk** but registers as `study-plan`. A cosmetic rename (`plan.md` → `study-plan.md`) would align filename with registered name. Deferred as non-urgent.

---

## How to pick this up

### If you're MJ continuing locally:

```bash
cd /path/to/amplifier-bundle-research

# Smoke test after a fresh clone:
amplifier bundle remove research 2>/dev/null
amplifier bundle add "file://$(pwd)" --name research-dev
amplifier run --bundle research-dev --mode single "Call mode tool operation=list and filter to source=research"
# → should show: critique, draft, execute, publish, question, study-plan

# Or use the public version:
amplifier bundle add "git+https://github.com/michaeljabbour/amplifier-bundle-research@main" --name research
```

### If you're reviewing for a PR or forking:

Read in order:
1. `README.md` — install + modes + recipes
2. `docs/HANDOFF.md` — this file
3. `docs/SPEC.md` — authoritative spec
4. `bundle.md` — valid frontmatter, short-name agent refs, research-modes transitively wired
5. `docs/ROADMAP.md` — post-v0.4 plan

### If you're a Claude Code / Cowork / subagent session:

The bundle is v0.4.0 and structurally stable. All architectural debt is documented. New work should focus on real-user validation (post-v0.4) or v1.0 dogfood paper. See `docs/ROADMAP.md`.

---

## File that matters most

If you read one file, read `docs/SPEC.md`. Everything else implements or documents what's in the spec.

---

## Contact

Michael Jabbour — michael.jabbour@gmail.com
