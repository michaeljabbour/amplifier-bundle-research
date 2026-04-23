# LaTeX Authoring Capability

This bundle includes specialized agents for LaTeX compilation, venue formatting, document structure, and references.

## Available Agents

### venue-formatter

**When to delegate:** LaTeX compilation, venue/format application, format conversion, error debugging

Use the venue-formatter agent when:
- Compiling LaTeX documents (pdflatex, bibtex, latexmk)
- Applying venue-specific formatting (academic or non-academic)
- Converting between venue formats (e.g., NeurIPS → ICML, or academic → USPTO brief)
- Debugging LaTeX compilation errors
- Validating that output meets venue requirements (page limits, margins, anonymization)

Covers both academic venues (NeurIPS, ICML, ACL, IEEE, ACM, arXiv) and non-academic output formats (USPTO patent briefs, policy memos, white papers).

### technical-writer

**When to delegate:** Document structure, outline creation, section organization, persona-aware prose

Use the technical-writer agent when:
- Planning document structure (IMRAD, patent-brief, policy-paper layouts)
- Organizing sections and crafting section-level outlines
- Writing abstracts, executive summaries, and contribution statements
- Adapting tone for the target persona (patent attorney, policy analyst, researcher)
- Structuring arguments and evidence flow

### citation-manager

**When to delegate:** BibTeX, reference accuracy, venue-specific citation styles

Use the citation-manager agent when:
- Building or cleaning BibTeX files
- Resolving DOIs and verifying reference metadata
- Detecting duplicate entries or inconsistent citation keys
- Converting between citation styles (natbib author-year, IEEE numeric, APA, patent prior-art format)

## Examples

<example>
user: 'Compile my paper for NeurIPS'
assistant: 'I'll delegate to venue-formatter to compile with NeurIPS formatting.'
<commentary>Venue-specific compilation requires the venue-formatter's template knowledge.</commentary>
</example>

<example>
user: 'Help me structure a paper on neural architecture search'
assistant: 'I'll delegate to technical-writer to design the IMRAD outline and contribution statement.'
<commentary>Structural planning and persona-aware prose is the technical-writer's domain.</commentary>
</example>

<example>
user: 'I'm getting a LaTeX error about an undefined control sequence'
assistant: 'I'll delegate to venue-formatter to diagnose and fix the compilation error.'
<commentary>Error debugging lives with the agent that owns the compile pipeline.</commentary>
</example>

<example>
user: 'My bibliography has duplicate entries and some missing DOIs'
assistant: 'I'll delegate to citation-manager to deduplicate and resolve the metadata.'
<commentary>Reference hygiene is the citation-manager's responsibility.</commentary>
</example>

## Implementation

These agents are context sinks that load heavy documentation only when spawned. This keeps root sessions lean while providing full expertise on demand. Venue specs live in `context/conference-formats/`; templates live in `templates/`.
