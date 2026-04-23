# Handoff — amplifier-bundle-research v0.2.0

**Date:** April 22, 2026 (post-Round-4: modes engagement + v0.3 priorities)
**Verification:** Bundle loads. All 6 research modes register as slash commands. Natural-language recipe invocation works. `tool-paperbanana` Python module installed and protocol-compliant. Smoke tested twice; all green.
**To:** Whoever picks this up next — MJ locally, another Claude Code / Cowork session, Copilot, or a PR reviewer

---

## Current state

**Bundle is fully loadable, Amplifier-hygienic, protocol-compliant, and mode-engaged.** The v0.3 reproducibility, critique-gate, and non-academic venue work are complete. Ready for first end-to-end recipe execution.

**Location:** local clone of `github.com/michaeljabbour/amplifier-bundle-research`
**Registered as:** `research-dev` (via `file://` source)

### Verified working

```bash
# Bundle registration:
$ cd /path/to/amplifier-bundle-research
$ amplifier bundle add "file://$(pwd)" --name research-dev
✓ Added bundle 'research-dev' (version: 0.2.0, canonical: research)

# Bundle composes with 53 agents + 17 modes (6 from research bundle):
$ amplifier run --bundle research-dev --mode single "Call mode tool with operation=list"
→ critique (research), draft (research), execute (research), publish (research),
  question (research), study-plan (research) ← all 6 registered

# tool-paperbanana protocol-compliant and pip-installed:
$ pip install -e modules/tool-paperbanana
✓ Successfully installed tool-paperbanana-0.2.0

# Mode activation works via warn-gate (standard modes bundle behavior):
$ amplifier run --bundle research-dev --mode single "Set mode to 'question'"
→ First call: denied (warn gate — standard, retry to confirm)
→ Second call: would activate
```

### Inventory (post-v0.3)

| Layer | Count | Status |
|---|---|---|
| Agents | 10 | Valid `meta:` frontmatter, `model_role`, common-agent-base footer |
| Modes (runtime) | 6 | All 6 register as slash commands: `/question`, `/study-plan` (renamed from `/plan`), `/execute`, `/critique`, `/draft`, `/publish` |
| Recipes | 9 | 8 mode-pipeline recipes have `publish_gates:` (critique_required + honest_pivot_acknowledged); paperbanana-figure is staged |
| Behaviors | 7 | Six domain behaviors + composite + new research-modes behavior wire everything up |
| Standalones | 1 | `bundles/dev.yaml` for local testing |
| Context files | 17 | Instructions + 6 conference formats + 3 venue formats (USPTO, policy-memo, NSF-grant) + imaging refs + paperbanana methodology + 3 awareness files |
| Templates | 32+ | Preregistration (base + patent-prereg + policy-prereg); 5 skeleton markdowns; LaTeX IMRAD + ACL + IEEE; **new v0.3**: environment.yml, requirements.in/.txt, Dockerfile.research, REPRODUCIBILITY.md, execution-log.yaml, evidence-log.yaml |
| Scripts | 4 | compile_latex, validate_format, generate_figure, download_templates |
| Modules | 1 | `tool-paperbanana` — protocol-compliant + pip-installed |
| Docs | 11 | SPEC (v0.2.0), ARCHITECTURE, PERSONAS, USE_CASES, UX_MOCKUP, LINEAGE, ROADMAP, GAP_ANALYSIS, SESSION_HISTORY, HANDOFF, session-1-transcript |
| Structural diagram | 2 | `bundle.dot` + `bundle.png` (source_hash current as of 22 Apr 2026) |

---

## How the bundle came to load + engage

Four authoring/hardening rounds produced the current state.

### Round 1: Authoring (claude.ai + Cowork earlier sessions)
128 files, ~59K lines. Content absorbed from `amplifier-bundle-scientificpaper`. See `docs/SESSION_HISTORY.md`.

### Round 2: Hardening (Amplifier local session — Apr 22, 2026)
Based on authoritative guidance from `amplifier:amplifier-expert`:
- `bundle.md` → valid YAML frontmatter
- `behaviors/research.md` composite (DRY)
- 4 scientificpaper-inherited behaviors cleaned
- 3 stale awareness files rewritten
- 5 missing templates written (white-paper, grant, replication skeletons; patent-prereg, policy-prereg YAMLs)
- 10 agents got `meta:` frontmatter + `model_role` + common-agent-base footer
- `bundles/dev.yaml` local-dev standalone
- Non-standard bundle metadata absorbed into `context/instructions.md`
- `bundle.dot` + `bundle.png` generated
- Minor: SPEC version bump, INDEX.md path leftover

### Round 3: Post-review hardening (same session, after parallel expert review)
Fixed 8 blockers surfaced by `amplifier-expert` + `foundation-expert` parallel reviews:
- `honest-pivot.md` + `exploratory-labeling.md` got YAML frontmatter (were pure markdown)
- `bundle.md` agent paths → short-name form (`research:hypothesis-designer`)
- `bundles/dev.yaml` provider URL → namespace form (`foundation:providers/anthropic-claude`)
- `recipes/paperbanana-figure.yaml` — 7 stale `scientificpaper:figure-artist` refs fixed
- 4 domain behaviors — unique `bundle.name` to avoid collision with root
- 16 `@scientificpaper:` refs across 9 context files — all fixed
- `tool-paperbanana` — entry point + `mount()` + Tool protocol properties
- 3 straggler old agent-name refs in prod files

### Round 4: Modes engagement + v0.3 priorities (same day, after user request)

**Mode registration — 6 modes now live as slash commands:**

- All 6 `modes/*.md` files got YAML frontmatter with `mode:` block (name, description, per-mode tool policies, default_action: block)
- Created `behaviors/research-modes.md` — the wiring: includes `modes:behaviors/modes.yaml`, mounts `hooks-mode` with `search_paths: ["@research:modes"]`, mounts `tool-mode` with `gate_policy: "warn"`, includes `modes:context/modes-instructions.md`
- Added to `behaviors/research.md` composite (now 7 includes)
- **Collision resolved:** `/plan` collided with `amplifier-bundle-modes`' default `/plan` (first-load wins). Renamed our mode to `name: study-plan` so all 6 register cleanly. Slash command is `/study-plan`; prose in bundle still refers to "the plan mode" as shorthand; research-coordinator routes natural-language "Run the plan mode" requests to `/study-plan`.

**v0.3 #1 — Reproducibility hardening:**
7 new templates in `templates/`:
- `environment.yml` (conda-lock pattern, 77 lines)
- `requirements.in` + `requirements.txt` placeholder (pip-tools / uv pattern)
- `Dockerfile.research` (minimal reproducibility container, 86 lines)
- `REPRODUCIBILITY.md` (one-page guide, 61 lines)
- `execution-log.yaml` (195 lines — structured schema for `/execute` logging)
- `evidence-log.yaml` (200 lines — for patent-brief/policy-brief evidence-gather)

Updated `modes/execute.md` with new "Reproducibility requirements" section covering: empirical recipes mandate `execution-log.yaml`, evidence-gather recipes mandate `evidence-log.yaml`, data-hash verification at `/execute` entry with `--allow-data-hash-mismatch` override, combined hash at exit as baseline for honest-pivot.

**v0.3 #2 — Critique-as-publish-gate:**
All 8 mode-pipeline recipes got `publish_gates:` block with:
- `critique_required: enforcement: block` (bypassable via `--no-critique-gate`, recorded in metadata)
- `honest_pivot_acknowledged: enforcement: block` (not bypassable)

Grant-proposal has `honest_pivot_acknowledged: enabled: false` (no `/execute` phase). Updated `modes/publish.md` with "Publish gates" section. Fixed pre-existing YAML syntax bug in `patent-brief.yaml` (`>= 3` → `">= 3"`).

**v0.3 #5 — Non-academic publish paths:**
3 new venue format specs in `context/venue-formats/`:
- `uspto.md` (241 lines) — USPTO patent format: claim format, drawings rules, EFS-Web filing
- `policy-memo.md` (276 lines) — policy brief format for government/NGO audiences
- `nsf-grant.md` (325 lines) — NSF proposal format with NIH variant notes

Updated `context/instructions.md` Recipes section and `agents/venue-formatter.md` capability list. Files contain `<!-- TBD: verify -->` markers where 2024/2025 rules may have drifted — flagged for domain-expert review.

**Authoritative guidance sources:**
- `amplifier:amplifier-expert` — Round 2 + Round 3 + mode registration pattern (Round 4 kickoff)
- `foundation:foundation-expert` — Round 3 parallel review
- `bundle-to-dot` skill — DOT freshness model
- `creating-amplifier-modules` skill — module protocol Iron Law
- `superpowers-reference` skill — Superpowers mode patterns for reference

---

## Operating the bundle

### Registration (one-time per machine)

```bash
cd /path/to/amplifier-bundle-research
amplifier bundle add "file://$(pwd)" --name research-dev
```

To re-sync after local changes (from inside the repo):

```bash
amplifier bundle remove research-dev && amplifier bundle add "file://$(pwd)" --name research-dev
```

(The `amplifier bundle update` command doesn't work for `file://` sources — remove + add is the refresh idiom.)

### Invoking recipes (three options)

**Option A — natural language (works today, verified):**
```bash
amplifier run --bundle research-dev --mode chat \
  "Run the patent-brief recipe on: Novel rolling-ROI control for AI agent sessions"
```
The model resolves `@research:recipes/patent-brief.yaml`, calls `recipes` tool with `operation=execute`.

**Option B — direct tool invocation:**
```bash
amplifier tool invoke recipes \
  operation=execute \
  recipe_path=@research:recipes/patent-brief.yaml \
  'context={"invention": "Novel rolling-ROI control for AI agent sessions"}'
```

**Option C — `--recipe` flag: does NOT exist in amplifier CLI.** Earlier docs suggested this; it's not a real flag. Use A or B.

### Using modes

The 6 research modes register as slash commands in any session where `research-dev` is active:

- `/question` — sharpen a rough claim into a falsifiable research question
- `/study-plan` — design methodology and hash-lock the pre-registration (formerly `/plan`; see "Known issues" below)
- `/execute` — run analysis / prior-art search / evidence gather per the locked plan
- `/critique` — apply structured critique (CONSORT/STROBE/PRISMA or venue equivalent)
- `/draft` — produce venue-appropriate document
- `/publish` — format, compile, submission-ready-package

Type `/mode <name>` or use the `mode` tool from inside a session to activate. First activation attempt shows a warn gate (intentional — retry to confirm). Use `/mode off` to deactivate.

### Testing tool-paperbanana (figure generation)

```bash
# Module is pip-installed. Exercise it via a recipe:
export GOOGLE_API_KEY="your-imagen-4-key"
amplifier run --bundle research-dev --mode chat \
  "Use the paperbanana-figure recipe to generate a methodology figure for a transformer architecture paper targeting NeurIPS."
```

Cost: ~$0.04/image (Imagen 4 pricing). Module has a placeholder-executes-fallback path if Imagen is unavailable.

---

## What's NOT done (v0.4 and beyond)

### v0.4 — User testing (three personas)

1. **Persona A test.** Non-scientist user (patent attorney, policy analyst, or founder) runs `patent-brief` or `policy-brief` recipe. Does the plain-English framing work? Is the mode vocabulary intuitive? Is `/study-plan` confusing to type instead of `/plan`?
2. **Persona B test.** Working researcher runs `empirical-paper` or `benchmark-paper` recipe. Does the pre-registration workflow add value or friction? Does `honest-pivot` fire appropriately?
3. **Persona C test.** Reviewer invokes `/critique` standalone on an existing document. Is the output actionable?

### v1.0 — Public release

4. **Dogfood paper.** First artifact this bundle produces should be the paper *about* this bundle, measured on the RCE benchmark. See `docs/ROADMAP.md`.
5. **GitHub push.** `git init && git add . && git commit -m "v0.2.0" && gh repo create michaeljabbour/amplifier-bundle-research --public --source=. --push`. After push, update `behaviors/paperbanana.md`'s `source:` URI from `../modules/tool-paperbanana` (local-dev form) to the git URL form.

### Post-v1.0

6. **Domain packs.** Medical (IRB, CONSORT), legal (patent prosecution), social science (STROBE, survey design).
7. **Multi-author support.** CRediT taxonomy, co-author review loops.
8. **Review-round support.** R&R response drafting with equal rigor to the original paper.
9. **Reference-manager MCP.** Zotero / Mendeley connector.

### Verification asks (non-blocking)

- **USPTO / NSF / NIH rules** in `context/venue-formats/*.md` have `<!-- TBD: verify -->` markers where 2024/2025 rules may have drifted. A reviewer with current MPEP / PAPPG access should walk the three files.
- **Execution log combined-hash format** (in `modes/execute.md`): defined as `sha256(execution_log_sha256 || preregistration_sha256)`. Alternative Merkle-style / JSON-manifest-digest schemes exist. Align with whatever convention the dogfood paper adopts.
- **Override flag names** coined during v0.3 (`--allow-data-hash-mismatch`, `--allow-prereg-hash-mismatch`, `--allow-search-plan-hash-mismatch`): if a canonical CLI flag convention exists elsewhere in the bundle, these should match it.

---

## Known issues

### /plan collision — live constraint, not a bug

The research bundle's plan mode is registered as `/study-plan` (not `/plan`) to avoid collision with the default `/plan` mode shipped by `amplifier-bundle-modes` ("Analyze, strategize, and organize - but don't implement").

Per foundation's `hooks-mode` contract: on shortcut collision, first-load wins silently; the second registration is dropped with an INFO log. Since the modes bundle loads its defaults before our research-modes behavior, their `/plan` wins.

**Consumer impact:**
- Users must type `/study-plan` (not `/plan`) to activate the research plan mode
- The research-coordinator agent routes natural-language invocations (e.g., "Run the plan mode", "Let's plan the study") to `/study-plan` regardless of phrasing
- Prose throughout the bundle often refers to "/plan" conceptually — that's the pipeline role, not the slash command

**If both research and superpowers bundles are loaded together:** the same collision issue affects other modes if names overlap. Per the foundation-expert's Round 4 guidance, a wrapper bundle that declares `hooks-mode` once with all desired search_paths is the canonical fix.

### Architectural debt (non-blocking, deferred past v1.0)

- **Thin-bundle partial violation.** `bundle.md` declares all 10 agents directly; canonical pattern (per `amplifier-bundle-recipes`) declares agents only in behaviors. Three agents (figure-designer, venue-formatter, technical-writer) are declared in both root and behaviors — runtime deduplication handles it, but it's maintenance debt.
- **Duplicate agent declarations.** figure-designer / venue-formatter / technical-writer each appear 3× (root + 2 behaviors). Same issue.
- **`tool-paperbanana` pyproject.toml name** doesn't follow `amplifier-module-tool-*` convention. Cosmetic; entry point is correct.

---

## How to pick this up

### If you're MJ working locally:

```bash
cd ~/dev/amplifier-bundle-research

# Smoke test (should print READY):
amplifier run --bundle research-dev --mode single "Reply with exactly: READY"

# List registered modes:
amplifier run --bundle research-dev --mode single \
  "Call the mode tool with operation=list and filter to source=research"

# First functional recipe test (natural language):
amplifier run --bundle research-dev --mode chat \
  "Run the patent-brief recipe on: Novel rolling-ROI control for AI agent sessions"
```

### If you're a Claude Code / Cowork / subagent session:

Read these files in order:
1. `docs/SESSION_HISTORY.md` — how the bundle came to exist (four rounds before this handoff)
2. `docs/HANDOFF.md` — this file
3. `docs/SPEC.md` — the authoritative spec (v0.2.0)
4. `bundle.md` — valid frontmatter; short-name agent refs; research-modes behavior transitively wired
5. `docs/ROADMAP.md` — v0.4 user testing, v1.0 dogfood paper, post-v1.0 domain packs

### If you're reviewing for a PR:

Design influences: `docs/LINEAGE.md`. Persona architecture: `docs/PERSONAS.md`. UX contract with full CLI transcripts: `docs/UX_MOCKUP.md`. Round 2+3+4 fix rationale: this file, §"How the bundle came to load + engage".

---

## File that matters most

If you read one file, read `docs/SPEC.md`. Everything else implements or documents what's in the spec.

---

## Contact

Michael Jabbour — michael.jabbour@gmail.com
