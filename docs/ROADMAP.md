# Roadmap

Versioning follows semver. Each milestone has a shipping definition — what must be true for the version to be called done — not a date.

---

## v0.1.0 — Spec and skeleton (current)

**Shipping definition:**
- Full specification written (`docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/PERSONAS.md`, `docs/USE_CASES.md`, `docs/UX_MOCKUP.md`, `docs/LINEAGE.md`)
- `bundle.md` manifest populated and validates against Amplifier's bundle schema
- One agent fully written as canonical thin-wrapper example (`agents/hypothesis-designer.md`)
- One mode fully written as canonical mode example (`modes/question.md`)
- One recipe fully written as canonical example (`recipes/patent-brief.yaml`)
- Other agents, modes, recipes stubbed with TODO markers
- README matches the install ease target (one command)

**Not in scope:** executing recipes, skill integration testing, eval against RCE.

---

## v0.2.0 — Working skeleton

**Shipping definition:**
- All eight agents fully written
- All six modes fully written
- Three recipes working end-to-end: `patent-brief`, `policy-brief`, `empirical-paper`
- K-Dense skills actually registered and loadable (not just referenced)
- Both behaviors (`honest-pivot`, `exploratory-labeling`) implemented
- Manual validation: one full end-to-end run of each working recipe, producing real artifacts
- Bundle installs cleanly on a fresh Amplifier install

---

## v0.3.0 — Full recipe set

**Shipping definition:**
- All seven recipes working: `patent-brief`, `policy-brief`, `white-paper`, `lit-review`, `empirical-paper`, `grant`, `replication-study`
- Venue pack: templates for USPTO, NSF, NIH, NeurIPS, ICML, ICLR, Nature, Science, plus generic policy-brief and white-paper formats
- RCE eval harness integrated — bundle can be scored automatically on its reflection-discipline properties

---

## v0.4.0 — User-tested

**Shipping definition:**
- Persona A validation: ≥ 3 patent attorneys use `patent-brief` on real invention disclosures. ≥ 2 of 3 rate defensibility ≥ 4/5.
- Persona B validation: ≥ 3 working researchers use `empirical-paper` on a real submission. ≥ 2 of 3 say the bundle caught a real issue they would have missed.
- Persona C validation: ≥ 3 reviewers use `/critique` standalone on incoming artifacts. ≥ 2 of 3 rate the output "useful and correct."
- Dogfooding: the paper *about* this bundle is drafted using this bundle, and passes its own `/critique`.

---

## v1.0.0 — Public release

**Shipping definition:**
- All v0.4 validation criteria met
- The dogfooded paper is accepted at a workshop or journal
- RCE benchmark score clears a predefined threshold (to be set in v0.3)
- Documentation covers onboarding, customization, and recipe authoring
- Public announcement, with link to the dogfooded paper as primary evidence

---

## Post-v1.0 directions (not yet scheduled)

- **Domain packs.** Add opt-in K-Dense skills for specific fields (genomics, chemistry, astrophysics, clinical trials). Each pack adjusts the `methodologist` agent's critique emphasis.
- **Multi-author collaboration.** Support co-authoring where multiple humans can edit at different modes.
- **Review-round support.** Explicit mode for responding to peer-review comments with the same rigor as the original draft.
- **Eval-as-a-service.** `/critique` exposed as an MCP server so reviewers can integrate it into their existing tooling.
- **Regulatory packs.** Templates and critique emphasis for FDA submissions, EU regulatory filings, safety-critical systems documentation.

---

## Explicit non-items

These will not be added even if requested:

- Autonomous mode ("run the whole thing, tell me when it's done"). Use Denario for that.
- Writing-assistant mode with the rigor turned off. The bundle's value is the rigor; removing it removes the point.
- Domain-specific experiment execution (running the actual experiments). That belongs in domain code, not a general research bundle.
