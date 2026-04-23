---
bundle:
  name: research-latex-authoring
  version: 0.4.0
  description: "LaTeX authoring, compilation, and conference formatting capabilities. Composes venue-formatter and technical-writer agents for comprehensive LaTeX workflow support."

agents:
  include:
    - research:venue-formatter
    - research:technical-writer

context:
  include:
    - research:context/latex-awareness.md
---

# LaTeX Authoring Behavior

Enables creation and compilation of LaTeX scientific documents.

## Capabilities
- Document structure creation
- Section and subsection management
- Table and figure environments
- Mathematical typesetting
- Bibliography integration

## Agent Delegation
- Structure planning -> @technical-writer
- Compilation and formatting -> @venue-formatter
