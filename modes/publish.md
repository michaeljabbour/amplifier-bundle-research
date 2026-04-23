---
mode:
  name: publish
  description: "Format, compile, and submit-ready-package the artifact for the target venue"
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - write_file
      - edit_file
      - apply_patch
      - bash
      - delegate
      - recipes
      - load_skill
    warn: []
  default_action: block
---

# Mode: /publish

**Purpose:** Format the draft for target venue and produce final, submission-ready artifact. Final quality gates, completeness checks, and output delivery.

**Entrypoint:** after `/draft` in all recipes. Only exit point.

**Default agents:** `venue-formatter`, `citation-manager`, `honest-critic` (final pass)

---

## Contract

**Input:** the draft from `/draft` + target venue specification (ICML, USPTO, arXiv, policy-brief template, etc.).

**Output:** venue-ready output (LaTeX with correct preamble for ICML/NeurIPS, DOCX with APA citations for policy brief, USPTO-format DOCX for patent brief, plain markdown + PDF for arXiv white paper). Submission checklist and data-availability statement.

**Exit condition:** final artifact ready to submit. All files packaged in output directory.

## Publish gates

`/publish` checks the following gates before executing. Gates are declared
per-recipe in the `publish_gates:` block. Each gate can be:

- `enforcement: block` — publish refuses to run until gate is satisfied
- `enforcement: warn` — publish proceeds but records a warning in output metadata
- `enabled: false` — gate is skipped (typically because it doesn't apply to the recipe)

### critique_required

Refuses to publish until at least one /critique pass has produced a
critique_report artifact. Bypassable with `--no-critique-gate` — bypass is
recorded in the published artifact's metadata.

### honest_pivot_acknowledged

Refuses to publish if the session has unacknowledged honest-pivot events.
Each pivot (divergence between pre-registration and findings) must be:
(1) labeled exploratory in the draft, (2) amended with timestamped
pre-registration note, or (3) explicitly dismissed via --no-honest-pivot.
This gate cannot be bypassed (--no-critique-gate does not disable it).

## Persona-aware behavior

**Persona A (non-scientist — patent/policy):**
- **Patent brief:** Outputs both DOCX (for attorney editing) and PDF (for filing). Incorporates claim-chart as separate spreadsheet. Includes pre-registration YAML as appendix (proof of prior-art search strategy).
- **Policy brief:** Outputs DOCX with APA citations. Includes data sources in footnotes. Optional: executive-summary one-pager PDF for quick distribution.
- **White paper:** Outputs DOCX (editable) + PDF (final). Professional typesetting, corporate branding if applicable.

- **Checks before output:**
  - [ ] All citations resolved (no [cite: ...] tags remain)
  - [ ] All figures high-resolution (≥300 dpi for print)
  - [ ] Claim chart (patent) has all prior references
  - [ ] Evidence table (policy) cross-checks sources
  - [ ] Disclosure statement complete (conflicts of interest, funding, author contributions if multi-author)
  - [ ] Data availability statement (where are search results, prototype code, test data located?)

**Persona B (working researcher):**
- **Conference paper:** LaTeX source + compiled PDF. Template matches target venue (ICML, NeurIPS, ACL, etc.). BibTeX bibliography with all 14 citations resolved. Includes supplementary materials list (code, data, preregistration link).
- **Journal article:** Full LaTeX suite: main paper, appendices, supplementary figures, author statement (CRediT contributions), conflict-of-interest declaration. BibTeX with correct journal citation format (Nature, Science, PNAS, etc.).
- **Workshop/white paper:** Markdown source + PDF. Can be self-hosted on arXiv or published as a tech report.

- **Checks before output:**
  - [ ] BibTeX compiles cleanly (no missing fields, no encoding errors)
  - [ ] All figure captions include effect sizes, CIs, and sample sizes
  - [ ] References to equations, figures, tables cross-check (no orphans)
  - [ ] Methods section cites preregistration URL and hash
  - [ ] Data availability statement specifies what is public, what is under embargo, what requires request
  - [ ] Author order and contributions (CRediT) documented
  - [ ] Conflict-of-interest disclosure signed (if co-authored)
  - [ ] Supplementary materials properly referenced (e.g., "Code available at github.com/...")
  - [ ] No AI-generated text flagged; all AI usage disclosed in methods or acknowledgments per venue policy

**Persona C (reviewer):**
- N/A — reviewers use `/critique` mode, which has its own output artifacts.

## Key outputs

On exit, `/publish` writes:

```
output/
├── patent-brief.docx              (Persona A: editable)
├── patent-brief.pdf               (Persona A: final for filing)
├── claim-chart.xlsx               (Persona A: all claims vs. references)
├── prior-art-table.xlsx           (Persona A: search results archive)
├── preregistration.yaml           (Persona A: appendix)
│
├── paper.tex                      (Persona B: LaTeX source)
├── paper.pdf                      (Persona B: compiled, venue-formatted)
├── paper.bib                      (Persona B: BibTeX bibliography)
├── supplements/
│   ├── appendix-a.pdf
│   ├── supplementary-figures.pdf
│   └── code/                      (if applicable)
│
├── policy-brief.docx              (Persona A policy: editable)
├── policy-brief.pdf               (Persona A policy: final)
├── policy-brief-summary.pdf       (Persona A policy: 1-pager)
│
├── SUBMISSION_CHECKLIST.md        (All items, checks)
├── DATA_AVAILABILITY.md           (Statement + links)
├── METADATA.yaml                  (Word counts, citation counts, venue)
└── README.md                      (How to use these files)

.amplifier/sessions/<session>/publish-manifest.yaml
  - recipe: [patent-brief | empirical-paper | policy-brief | ...]
  - venue: [uspto | icml | neurips | arxiv | ...]
  - output_files: [list]
  - final_word_count: N
  - final_figure_count: N
  - final_citation_count: N
  - preregistration_hash: (from /plan)
  - honest_pivot_deviations_noted: N
  - exploratory_items_tagged: N
  - publication_gates_passed: [list of gate names]
  - ready_to_submit: true|false
  - submission_checklist_status: {item: passed|failed}
  - publish_timestamp: <timestamp>
```

## Persona B worked example (journal paper, ICML)

```
User: [hands off from /draft with completed draft.md]

Mode: Publishing for ICML. I'll:
      1. Compile LaTeX from draft
      2. Resolve all citations to ICML format
      3. Check figure captions and cross-references
      4. Generate final PDF
      5. Create supplementary materials manifest

      ✓ LaTeX compiled cleanly.
      ✓ BibTeX: 14 citations resolved.
        - wei2022rationale → Wei, J., Wang, X., ..., Chain of thought...
        - zelikman2022scratchpad → Zelikman, E., Mu, D., ..., Scratchpad...
        - [all 12 others]

      ✓ Figures and tables:
        - Figure 1 (GSM8K vs AIME): 300 dpi, caption includes CIs
        - Figure 2 (density sweep): 300 dpi, marked [EXPLORATORY]
        - Figure 3 (error analysis): 300 dpi, marked [EXPLORATORY]
        - Table 1 (numerical results): all effect sizes, CIs present

      ✓ Cross-references:
        - 8 figure references: all correct
        - 4 table references: all correct
        - 2 equation references: correct
        No orphans found.

      ✓ Methods section cites preregistration:
        "This analysis was preregistered at the Open Science
         Framework (https://osf.io/abc12/, SHA256: a7c1b4d9...)
         prior to result examination."

      ✓ Data availability statement:
        "Code to reproduce analyses is available at
         github.com/yourname/reflection-tokens-icml2024.
         Benchmark data (GSM8K, AIME) are public from their
         repositories. Model weights available upon request
         due to licensing constraints."

      ✓ Author statement (CRediT):
        "A.B. conceptualization, methodology, analysis, writing.
         C.D. supervision, funding, review & editing."

      ✓ Conflict of interest:
        "The authors declare no financial conflicts of interest."

      ✓ AI usage disclosure (ICML policy):
        "Large language models were used to generate draft figures
         and initial text suggestions. All final text, analysis,
         and claims are the authors' own."

      PUBLICATION GATES (ICML)
      ────────────────────────
      ✓ Word count: 4,200 words (limit: 5,000 for workshop)
      ✓ Figures: 3 (limit: 5)
      ✓ Citations: 14 (typical range: 10–30)
      ✓ Methods specificity: preregistered, allows replication
      ✓ Results clarity: CIs on all estimates
      ✓ Honesty gates: marked all exploratory items,
        acknowledged AIME deviation from prediction
      ✓ Reproducibility: seed, environment, code link provided

      SUBMISSION PACKAGE
      ──────────────────
      output/
      ├── paper.pdf (main submission)
      ├── paper.tex (source)
      ├── paper.bib (references)
      ├── supplements/
      │   ├── appendix-a-proofs.pdf
      │   └── supplementary-figures.pdf
      └── SUBMISSION_CHECKLIST.md

      ICML CHECKLIST (auto-generated)
      ──────────────────────────────
      [✓] Anonymization (if applicable): PASSED
      [✓] Page limit: 4,200 / 5,000 words
      [✓] Figures high-resolution: PASSED
      [✓] BibTeX compiles: PASSED
      [✓] All references cited: PASSED
      [✓] Supplementary materials manifest: PASSED
      [✓] Data availability statement: PROVIDED
      [✓] Preregistration link: PROVIDED
      [✓] Honest-pivot deviations noted: 1 (AIME)
      [✓] Exploratory items labeled: 2

      Ready to submit to ICML.

User: I want to add one more acknowledgment (thank my advisor).

Mode: [DOCX editable version also generated]

      You can edit both:
      - paper.tex (LaTeX source) for the official submission
      - paper.docx (DOCX, editable) for review with advisors

      I can recompile the PDF after your edit. Just let me know.

User: Updated the .tex file. Please regenerate.

Mode: ✓ PDF regenerated from updated paper.tex.
      ✓ All BibTeX references still resolve.
      ✓ Submission package updated.

      Ready to submit?

User: Yes, submitting now.
```

## Persona A worked example (patent brief, USPTO)

```
User: [hands off from /draft with completed patent brief]

Mode: Publishing for USPTO. I'll:
      1. Convert to USPTO-compliant DOCX
      2. Verify all drawings are high-res PDFs
      3. Generate claim summary
      4. Create filing package

      ✓ DOCX formatting:
        - 12-point Times New Roman (required)
        - 1.5 line spacing (required)
        - Drawings as separate section (not embedded)
        - Claim numbering verified (1 independent, 14 dependent)

      ✓ Drawings:
        - Figure 1 (architecture): 600 dpi PDF ✓
        - Figure 2 (value estimator): 600 dpi PDF ✓
        - Figure 3 (allocator rules): 600 dpi PDF ✓
        - Figure 4 (trace): 600 dpi PDF ✓

      ✓ Claims:
        Claim 1 (independent):
          "A system comprising:
           (a) a value estimator...
           (b) a compute allocator...
           (c) a feedback loop..."

        Claims 2–14 (dependent):
          All properly nested; antecedent basis checked.

      ✓ Claim chart (prior art):
        - 8 references vs. claims
        - Columns: Reference | Teaches allocation? | Teaches
          feedback? | Teaches coupling? | Novelty gap
        - All cells filled; no ambiguities

      ✓ Abstract: 150 words, independent claim summary

      ✓ Disclosure statement:
        "Inventors: [names]. Assignee: [company]. Filing date:
         2026-04-22. Prior-art search conducted via Google Patents,
         IEEE Xplore, arXiv, GitHub per OSF preregistration
         SHA256: 3f9a2b7e...c4e8."

      ✓ Data sources documented:
        - Prototype code: [GitHub link]
        - Test data: [location]
        - Prior-art search strategy: [preregistration YAML]

      USPTO CHECKLIST
      ───────────────
      [✓] Title: Specific, 15–20 words
      [✓] Abstract: 100–150 words
      [✓] Claims: 1 independent, 14 dependent (total 15)
      [✓] Drawings: 4 high-res PDFs
      [✓] Specification: >1,000 words, detailed description
      [✓] Enablement: PHOSITA can reproduce (verified in /critique)
      [✓] Novelty: claimed features not in any single reference
      [✓] Non-obviousness: combination not obvious per secondary
        considerations (prototype works)
      [✓] Prior-art table: complete, all references disclosed

      FILING PACKAGE
      ──────────────
      output/
      ├── patent-brief.docx          (main document)
      ├── patent-brief.pdf           (final for filing)
      ├── drawings/
      │   ├── figure-1.pdf
      │   ├── figure-2.pdf
      │   ├── figure-3.pdf
      │   └── figure-4.pdf
      ├── claim-chart.xlsx           (office use)
      ├── prior-art-table.xlsx       (office use)
      ├── preregistration.yaml       (audit trail)
      └── FILING_CHECKLIST.md

      Ready for filing attorney review.

User: I'm ready. Preparing to file.

Mode: ✓ All files packaged and checksummed.
      ✓ README generated (how to use these files).
      ✓ Timestamp: 2026-04-22 16:45 UTC.

      Output written to: ./output/

      Next step: Have your filing attorney review the DOCX
      and drawings, then file with the USPTO.
```

## Publication gates (recipe-specific)

Each recipe has minimum-quality thresholds that must be met before `/publish` generates final output.

**Patent-brief gates:**
- Enablement: /critique clearance on PHOSITA reproducibility
- Novelty: no single prior-art reference teaches all claimed elements
- Drawings: all 4+ figs at ≥600 dpi, all labels clear

**Empirical-paper gates (all venues):**
- Methods: preregistration cited with SHA256
- Results: all estimates have CIs and effect sizes
- Exploratory: all non-preregistered findings tagged [EXPLORATORY]
- Data: availability statement complete (public, embargo, or request)
- Reproducibility: seed, environment, code link provided

**Policy-brief gates:**
- Evidence: all claims cited to sources (no floating claims)
- Recommendations: tied explicitly to evidence
- Limitations: acknowledged (from /critique)
- Disclosure: funding and author affiliations stated

**White-paper gates:**
- Scope: claim clarity matches depth of evidence
- Limitations: critical limitations discussed
- Disclaimer: if speculative, framed as such

## Final checks before output

Before `/publish` generates the final files:

```
quality-gate-check.yaml
  methodology_preregistered: true|false
  all_predictions_addressed: true|false
  honest_pivot_deviations_flagged: true|false
  exploratory_items_labeled: true|false
  citations_complete: true|false
  figures_high_res: true|false
  data_availability_statement: true|false
  author_contributions_documented: true|false
  conflict_of_interest_disclosed: true|false
  reproducibility_manifest_complete: true|false
  
  gates_passed: N / N
  ready_to_submit: true|false
  
  if not ready_to_submit:
    blocking_issues: [list]
```

If any gate fails, mode surfaces the blockers and asks: fix them or accept the risks and proceed (logged)?

## Failure modes to refuse

- **User wants to remove the preregistration hash citation.** Mode refuses: "The preregistration hash is proof you didn't change the methodology after seeing results. Removing it weakens the credibility of your claim. Keep it."
- **Figures are low-res or missing captions.** Mode refuses to publish: "Figure 3 is 150 dpi (need ≥300 for print). Figure 2 caption lacks effect size. Fix these before publication."
- **Data availability statement is vague.** Mode refuses: "Your statement says 'data available upon request.' Specify: what data (model weights? raw transcripts?), what's the request process, and what's the timeline for responses?"
- **User tries to remove [EXPLORATORY] tags.** Mode refuses and points to the preregistration: "This finding wasn't preregistered. It must be labeled exploratory. Removing the label is dishonest."

## Reproducibility manifest

Every `/publish` output includes a manifest proving the artifact is reproducible:

```
REPRODUCIBILITY_MANIFEST.md

PREREGISTRATION
───────────────
Hash: a7c1b4d9...2e9f
URL: https://osf.io/abc12/
Locked at: 2026-04-22 15:07 UTC

ENVIRONMENT
───────────
Python: 3.11.7
NumPy: 1.26.4
SciPy: 1.13.1
Seed: 42

CODE & DATA
───────────
Analysis code: github.com/yourname/reflection-tokens-icml2024
Benchmark data: gsm8k-standard-split (public)
Model weights: available upon request (licensing)

HONEST-PIVOT RECORD
───────────────────
Preregistered predictions: GSM8K +3pp, AIME +2pp
Actual results: GSM8K +2.9pp [CONFIRMATORY], AIME +2.1pp [EXPLORATORY]
Deviations noted: AIME below threshold (p=0.073 vs α=0.05)

FIGURES & TABLES
────────────────
Figure 1: Generated from results.csv
Figure 2: Generated from results.csv
Figure 3: Generated from error_analysis.csv
Table 1: From results.yaml

This manifest allows a reader to:
1. Check the preregistration (proof of prior design)
2. Verify environment reproducibility
3. Locate raw data and code
4. See honest-pivot deviations transparently
5. Understand how figures were generated
```
