---
bundle:
  name: research-figure-generation
  version: 0.2.0
  description: "AI-assisted scientific figure creation with quality veto rules. Composes figure-designer agent for publication-ready visualizations."

agents:
  include:
    - research:figure-designer

context:
  include:
    - research:context/figure-generation-awareness.md
---

# Figure Generation Behavior

Enables creation of publication-quality scientific figures.

## Supported Figure Types
- Mathematical plots and charts
- Architecture and flow diagrams
- Neural network visualizations
- Statistical graphics
- Schematic illustrations

## Tool Selection Matrix
| Type | Primary | Alternative |
|------|---------|-------------|
| Plots | Matplotlib | PGFPlots |
| Diagrams | Mermaid | Graphviz |
| Math | TikZ | SVG |
| Complex | Gemini API | - |

## Agent Delegation
All figure requests -> @figure-designer
