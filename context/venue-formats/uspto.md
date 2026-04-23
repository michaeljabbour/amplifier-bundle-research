# USPTO Patent Filing Format Specification

**Venue:** United States Patent and Trademark Office (USPTO)
**Year:** 2024/2025 (current MPEP guidance)
**Official Site:** https://www.uspto.gov/
**Filing System:** EFS-Web / Patent Center

---

## Document Types

| Type | Purpose | Page Limit | Claims |
|------|---------|------------|--------|
| **Provisional (utility)** | Establish priority date, 12-month pendency, never examined | None | Not required (but recommended) |
| **Non-provisional utility** | Examined application; most common form | None (but claim-count fees apply) | Required; ≥1 independent |
| **Design patent** | Ornamental design of an article | Typically short | Single claim, drawing-driven |
| **Plant patent** | New distinct plant varieties | N/A | Single claim |
| **PCT international** | International priority under Patent Cooperation Treaty; later enters national phase | Varies | Required |
| **Continuation / CIP / Divisional** | Derivatives of a parent non-provisional | As parent | Required |

The three that this bundle most often targets are **provisional**, **non-provisional utility**, and **design**. Pick the document type explicitly in the preregistration (`patent_type` field in `templates/patent-prereg.yaml`).

---

## Document Format

### Paper Size
- **Size:** US Letter (8.5" × 11") — A4 (210 mm × 297 mm) also accepted for international/PCT filings
- **Orientation:** Portrait (drawings may be landscape)
- **Pages numbered:** Consecutively, centered at top or bottom

### Margins
Per 37 CFR 1.52(a)(1)(ii):
- **Top:** ≥ 2.0 cm (≈ 0.75")
- **Left:** ≥ 2.5 cm (≈ 1.0")
- **Right:** ≥ 2.0 cm (≈ 0.75")
- **Bottom:** ≥ 2.0 cm (≈ 0.75")

### Line Spacing
- **Body text:** 1.5 or double-spaced
- **Claims:** 1.5 spacing, each claim starts on a new line
- **Abstract:** Single paragraph, 1.5 spacing

### Font
- **Required:** Times New Roman 12pt (minimum). Arial 12pt acceptable.
- **Nonstandard fonts:** Not permitted for body text
- **Case:** Normal sentence case; ALL CAPS acceptable for section headings
- **Special characters:** Avoid unicode math — spell out symbols or include them in drawings

### Text Quality
- Black ink equivalent (no color text in the specification)
- Text must be selectable/searchable in the PDF — **scanned text-as-image will be rejected**

---

## Required Sections (Non-Provisional Utility)

In this exact order, per MPEP 608:

1. **Title of the Invention** — ≤ 500 characters, descriptive not marketing
2. **Cross-Reference to Related Applications** — Prior provisional, continuation, or PCT priority claims
3. **Statement Regarding Federally Sponsored Research** — Required if any federal funding (35 USC 202)
4. **Reference to a Sequence Listing / Table / Computer Program Listing** — If applicable
5. **Background of the Invention** — (a) Field of the invention, (b) Description of related art
6. **Brief Summary of the Invention** — What the invention is, at a high level; mirrors claims
7. **Brief Description of the Drawings** — One line per figure: "Fig. 1 is a block diagram of..."
8. **Detailed Description of the Invention** — The written-description bulk; must satisfy §112(a) written description, enablement, and best mode
9. **Claim(s)** — Numbered; see Claim Format below
10. **Abstract of the Disclosure** — ≤ 150 words, on a separate page

Supporting documents filed alongside:
- **Oath or Declaration** (inventor signature) — required per 37 CFR 1.63
- **Application Data Sheet (ADS)** — 37 CFR 1.76
- **Drawings** (see Drawings section)
- **Information Disclosure Statement (IDS)** — prior art the applicant is aware of
- **Fee transmittal / fee sheet**

---

## Claim Format

Claims are the legally operative portion. Format rules are strict:

### Structural Rules
- **Each claim is exactly one sentence**, beginning with a capital letter and ending with a period.
- Claim 1 (independent) typically reads: "**A** method of...", "**An** apparatus comprising...", "**A** system for..."
- Claims are numbered consecutively: `1.`, `2.`, `3.`, ... (no `2.1`, `2.2` — dependent claims get their own integer number, not sub-numbering)
- Dependent claims reference a prior claim: "The method of claim 1, further comprising..."
- Multiple dependency (e.g., "of claim 1 or claim 2") is allowed but incurs extra fees; avoid unless strategically needed.

### Independent vs Dependent
- **Independent claim:** Stands alone; defines the broadest version of the invention
- **Dependent claim:** Adds one or more limitations to a prior claim (narrower scope, used as fallback positions during prosecution)
- Typical structure: 1-3 independent claims + 15-20 dependent claims total, to stay within the base filing fee

### Claim Differentiation
Each claim should cover distinct subject matter — avoid claims that are word-for-word identical in scope. The doctrine of claim differentiation assumes each claim has independent meaning; redundancy wastes fees and weakens prosecution.

### Means-Plus-Function (§112(f))
- Claim elements written as "means for [function]" or "step for [function]" trigger 35 USC §112(f) interpretation
- Interpreted as covering **only** the corresponding structure disclosed in the specification + equivalents
- **Implication:** If you use "means for," the specification must explicitly disclose the structure/algorithm that performs the function, or the claim is indefinite under §112(b)
- Modern drafting often avoids "means for" for software/computer-implemented inventions — use "processor configured to..." instead

### Claim Style Conventions
- **Transitional phrase:** "comprising" (open-ended, preferred), "consisting of" (closed, narrow), "consisting essentially of" (semi-closed)
- **Antecedent basis:** Every "the [element]" must refer back to an earlier "a [element]" in the same claim chain
- **Markush groups:** "selected from the group consisting of A, B, and C" for chemistry/materials claims

---

## Drawings

Governed by 37 CFR 1.84. Drawings are mandatory when they aid understanding — which is nearly always for utility applications.

### Requirements
- **Ink:** Black ink on white background (color drawings require a petition + fee and are rare)
- **Lines:** Solid, durable, uniformly thick; no shading except in limited cases
- **Figures:** Numbered (Fig. 1, Fig. 2, ...). Multiple views on one sheet are allowed if labeled Fig. 1A, Fig. 1B
- **Reference numerals:** Every element referenced in the specification must have a numeral in the drawing; numerals must match between drawing and description verbatim
- **Sheet size:** 8.5" × 11" or A4 (match the application)
- **Margins on drawing sheets:** Top 2.5 cm, left 2.5 cm, right 1.5 cm, bottom 1.0 cm

### Restrictions
- **No photographs** in utility applications unless they are the only practical medium (e.g., histology, crystal structure) — requires petition
- **No shading** except for:
  - Sectional views (hatching per MPEP 608.02)
  - Surface shading to show curvature (design patents; utility by exception)
- **No color** unless petitioned and approved
- **No text inside figures** beyond reference numerals and short labels

### Informal Drawings
The USPTO will accept "informal" drawings at filing (for priority date purposes), but formal drawings meeting all rules must be submitted before allowance. Informal drawings at filing are a known cause of desk-reject if they fail to disclose the invention.

---

## Filing Format

### Electronic Filing (EFS-Web / Patent Center)
- **PDF required** for the specification, claims, abstract, and drawings
- **Text layer:** The PDF must be text-searchable — scanned images of typed pages are **rejected** unless OCR'd to a text layer
- **Bookmarks:** Desirable (not required) for each of the required sections
- **File size:** ≤ 25 MB per PDF file via EFS-Web (Patent Center supports larger) <!-- TBD: verify current 2025 limit; USPTO has raised limits periodically -->
- **Embedded fonts:** All fonts must be embedded
- **Encryption:** Not permitted — filings must be readable by examiners without passwords

### File naming conventions
USPTO does not mandate names, but common convention:
- `specification.pdf` — Title, cross-ref, background, summary, brief description, detailed description
- `claims.pdf` — Claims starting on their own page
- `abstract.pdf` — Abstract, separate page
- `drawings.pdf` — All figures
- `oath.pdf` — Inventor declaration
- `ADS.pdf` — Application Data Sheet

---

## Citation Format

### Prior-Art Patent References
Use the USPTO citation style:

```
US 10,123,456 B2 (Smith et al., 2019)
US 2021/0234567 A1 (Jones, 2021)          % published application
EP 3 456 789 B1 (García, 2018)
WO 2020/123456 A1 (Patel et al., 2020)    % PCT publication
```

Components:
- Country code (US, EP, WO, JP, CN, ...)
- Patent/publication number
- Kind code (B1/B2 = granted patent; A1/A2 = published application)
- Parenthetical: first inventor + "et al." if >1 + year

### Non-Patent Literature (NPL)
Standard academic citation is acceptable, but the IDS form (SB/08) requires:
- Author(s) (last name, first initial)
- Full title (no abbreviation)
- Journal/venue name, volume, issue, pages
- Publication date (month and year)
- Publisher if not obvious

Example:
```
Smith, J. A. and Jones, R. B., "A Novel Approach to Neural Quantization,"
Proceedings of NeurIPS 2023, vol. 36, pp. 1234–1256, Dec. 2023.
```

### Record Requirements
- Every cited reference must be disclosed on an **Information Disclosure Statement (IDS)** — form PTO/SB/08a or 08b
- Failure to disclose material prior art known to the inventor can result in **inequitable conduct** findings that invalidate the patent
- IDS must be filed within three months of filing or before the first office action to avoid fees

---

## Common Desk-Reject Reasons

| Reason | Mitigation |
|--------|------------|
| **Missing oath/declaration** | File 37 CFR 1.63 declaration with application or within grace period (requires surcharge) |
| **Informal drawings** | Replace with formal drawings before allowance; can delay prosecution |
| **Claim language issues** (no antecedent basis, indefinite terms, §112(b) violations) | Internal review against §112(b) checklist before filing |
| **Insufficient written description (§112(a))** | Detailed Description must show possession of the full scope of the claims |
| **Inadequate enablement (§112(a))** | Description must teach a person skilled in the art how to make and use without undue experimentation |
| **Missing required section** (e.g., no Background, no Brief Description of Drawings) | Run pre-file checklist against MPEP 608 |
| **Non-searchable PDF** | Ensure text layer present; no scanned pages |
| **Color drawings without petition** | Submit B&W, or file petition with $ fee |
| **Font/margin violations** | Use template that enforces 12pt Times New Roman + correct margins |
| **Missing Abstract or Abstract > 150 words** | Count words before filing |

---

## Template Location

- **Patent brief template:** `templates/patent-brief-template.md`
- **Patent preregistration schema:** `templates/patent-prereg.yaml`
- **USPTO official forms:** https://www.uspto.gov/patents/apply/forms

The `patent-brief-template.md` provides scaffolding for the narrative sections; `patent-prereg.yaml` captures the disclosure decisions (patent_type, claimed features, cited prior art, inventors, funding source) that need to be sealed before drafting.

---

## `venue-formatter` Integration

When `target_venue: uspto` is set in the preregistration, `venue-formatter` should: (1) load this spec; (2) apply US Letter page size, 12pt Times New Roman, 1.5 line spacing, and the margins in §"Margins" to the rendered PDF; (3) verify the document contains all ten required sections (Title through Abstract) in the correct order and flag any missing section as a desk-reject risk; (4) validate that each claim is a single sentence, claims are numerically ordered, and dependent claims contain a proper antecedent phrase ("The [apparatus/method/system] of claim N, ..."); (5) run the citation formatter over prior-art references to produce the `US 10,123,456 B2 (Smith et al., 2019)` form; (6) confirm the rendered PDF has a text layer (searchable) and all fonts are embedded; (7) emit a pre-filing checklist mirroring the Common Desk-Reject Reasons table so the user can confirm each item before submission. Drawings are handled separately by `figure-designer` but `venue-formatter` should verify every reference numeral in the description appears in at least one figure caption.

---

## Additional Resources

- **MPEP (Manual of Patent Examining Procedure):** https://www.uspto.gov/web/offices/pac/mpep/
- **37 CFR (patent regulations):** https://www.ecfr.gov/current/title-37
- **Patent Center (filing portal):** https://patentcenter.uspto.gov/
- **USPTO Fee Schedule:** https://www.uspto.gov/learning-and-resources/fees-and-payment

---

**Last Updated:** 2025
**Valid For:** USPTO filings under current MPEP guidance
**Verification notes:** <!-- TBD: verify EFS-Web vs Patent Center file-size limits for 2025; confirm current status of the DOCX filing option which USPTO has been transitioning applicants to. -->
