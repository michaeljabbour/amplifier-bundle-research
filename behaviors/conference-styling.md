---
bundle:
  name: research-conference-styling
  version: 0.2.0
  description: "Multi-conference format support and conversion. Provides awareness of supported conference formats through context files."

context:
  include:
    - research:context/conference-styling-awareness.md
---

# Conference Styling Behavior

Applies correct formatting for major scientific conferences.

## Supported Conferences
- NeurIPS - 8 pages, Times 10pt
- ICML - 8 pages, two-column
- ACL - A4 only, natbib
- IEEE - Letter/A4, numbered citations
- ACM - Single-column review
- arXiv - TeX recommended

## Agent Delegation
- Format application -> @venue-formatter
- Citation styling -> @citation-manager
