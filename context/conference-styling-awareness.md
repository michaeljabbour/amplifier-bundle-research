# Venue Styling Capability

This bundle supports multiple academic venue formats with official style files and conversion capabilities. Non-academic output (USPTO briefs, policy memos) is also handled by the same venue-formatter agent.

## Supported Academic Venues

Format specs live in `context/conference-formats/`:

- **NeurIPS** - Neural Information Processing Systems (`neurips.md`)
- **ICML** - International Conference on Machine Learning (`icml.md`)
- **ACL** - Association for Computational Linguistics (`acl.md`)
- **IEEE** - IEEE Transactions and Conferences (`ieee.md`)
- **ACM** - ACM SIGCHI and other ACM venues (`acm.md`)
- **arXiv** - arXiv preprint formatting (`arxiv.md`)

Non-academic output formats (USPTO patent brief, policy memo, white paper) are covered directly by the venue-formatter agent without a separate `conference-formats/` entry.

## When to Use Venue Formatting

Delegate to the **venue-formatter** agent when:
- Creating a new document in a specific venue format
- Converting an existing paper between venues (e.g., NeurIPS → ICML)
- Validating venue-specific requirements (page limits, anonymization, margins)
- Debugging format-related LaTeX compilation errors

For citation-style adjustments that accompany a venue change, delegate to **citation-manager** (natbib author-year, IEEE numeric, APA, patent prior-art).

## Key Format Differences

| Venue   | Paper Size   | Columns | Font Size  | Citation Style         |
|---------|--------------|---------|------------|------------------------|
| NeurIPS | US Letter    | Single  | 10pt Times | Flexible (natbib)      |
| ICML    | US Letter    | Two     | 10pt Times | Numbered or author-year|
| ACL     | **A4** ⚠️    | Two     | 11pt Times | Author-year (natbib)   |
| IEEE    | Letter or A4 | Two     | 10pt Times | Numbered [1]           |
| ACM     | US Letter    | Two     | 9pt Serif  | Numbered               |
| arXiv   | Flexible     | Varies  | Varies     | Venue-dependent        |

**Critical:** ACL requires A4 paper size (not US Letter)!

## Examples

<example>
user: 'Format this paper for NeurIPS submission'
assistant: 'I'll delegate to venue-formatter to apply NeurIPS formatting.'
<commentary>Venue formatting requires venue-formatter's template knowledge.</commentary>
</example>

<example>
user: 'Convert my NeurIPS paper to ICML format'
assistant: 'I'll delegate to venue-formatter to handle the format conversion.'
<commentary>Format conversion requires understanding of both venue specs.</commentary>
</example>

<example>
user: 'Turn this technical write-up into a USPTO patent brief'
assistant: 'I'll delegate to venue-formatter for layout, and loop in technical-writer for claim-focused prose.'
<commentary>Non-academic output formats share the same formatting pipeline.</commentary>
</example>

## Implementation

Venue format specifications are stored in `context/conference-formats/*.md` and loaded on-demand by the venue-formatter agent. Templates live in `templates/*/`.
