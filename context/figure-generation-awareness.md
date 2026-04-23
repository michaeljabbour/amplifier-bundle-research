# Figure Generation Capability

This bundle includes the **figure-designer** agent for creating publication-ready figures for academic, patent, and policy documents.

## When to Delegate

Use the figure-designer agent when:
- Creating plots, charts, or data visualizations
- Generating architecture diagrams, flowcharts, or methodology diagrams
- Converting matplotlib plots to LaTeX-compatible formats (TikZ)
- Needing publication-quality vector graphics (SVG, PDF, TikZ)
- Creating neural network architecture diagrams
- Designing conceptual illustrations for complex methodology

## Capabilities

### Data Plots & Statistical Graphics
- **Matplotlib + SciencePlots** - Publication-quality plots with scientific styling
- **tikzplotlib** - Seamless Matplotlib → TikZ conversion for LaTeX
- **Seaborn** - Statistical graphics (violin, box, heatmaps, FacetGrid)

### Diagrams
- **Mermaid** - Flowcharts and process diagrams
- **TikZ / PGFPlots** - LaTeX-native math diagrams and plots
- **PlotNeuralNet** - Neural network architecture diagrams

### Complex Methodology Illustrations
- **PaperBanana methodology** - Quality-first illustration workflow
- **Gemini Imagen** - Conceptual/methodology imagery (requires API key)
  - ⚠️ Never for data plots or mathematical diagrams
  - Reserved for photorealistic or conceptual imagery

## Quality Veto Rules

The figure-designer applies **8 PaperBanana quality veto rules**. Any failure rejects the figure:
- ❌ Low-quality artifacts (blurry, distorted, pixelated)
- ❌ Unprofessional colors (neon, jarring combinations)
- ❌ Black backgrounds (unless specifically requested)
- ❌ Text too small to read at publication scale
- ❌ Colorblind-unsafe palettes (enforced; ColorBrewer/patterns required)
- ✅ Vector formats preferred (PDF, SVG, TikZ)
- ✅ 300 DPI minimum for raster images
- ✅ Tested against colorblind simulation before acceptance

## Examples

<example>
user: 'Create a plot showing training loss curves over epochs'
assistant: 'I'll delegate to figure-designer to create a publication-ready plot using matplotlib with scientific styling.'
<commentary>Data visualization requires the figure-designer's tool selection and quality control.</commentary>
</example>

<example>
user: 'Generate a transformer architecture diagram'
assistant: 'I'll delegate to figure-designer to design this diagram using PlotNeuralNet or TikZ.'
<commentary>Architecture diagrams require specialized tools and composition expertise.</commentary>
</example>

<example>
user: 'Convert this matplotlib code to TikZ for my LaTeX paper'
assistant: 'I'll delegate to figure-designer to handle the conversion using tikzplotlib.'
<commentary>Format conversion requires knowledge of both matplotlib and TikZ.</commentary>
</example>

## Implementation

The figure-designer agent is a context sink that loads heavy imaging documentation only when spawned — matplotlib guides, TikZ patterns, PaperBanana veto rules, and accessibility checks. This keeps root sessions lean while providing full expertise on demand.
