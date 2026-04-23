# NeurIPS LaTeX Style Guide

## Overview

This is a comprehensive reference guide for the Neural Information Processing Systems (NeurIPS) LaTeX formatting requirements. The NeurIPS style file ensures consistent formatting across all submissions and follows the official conference standards.

**Current Version**: NeurIPS 2025 (applicable to recent conferences)
**Style File**: `neurips_20XX.sty` (where XX is the conference year)
**LaTeX Version**: LaTeX 2ε only (LaTeX 2.09, Microsoft Word, and RTF are no longer supported)

---

## Style File Basics

### Installation

1. **Download Style Files**: Obtain the appropriate `neurips_20XX.sty` file from the NeurIPS website
2. **Place in Project**: Include the `.sty` file in your paper's root directory
3. **Load in Document**: Use `\usepackage{neurips_20XX}` with appropriate options

### File References

- **Official NeurIPS Style Files**: https://neurips.cc/Conferences/2024/PaperInformation/StyleFiles
- **GitHub Repositories**: https://github.com/ArmageddonKnight/NeurIPS/blob/main/neurips.sty
- **Overleaf Templates**: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh

---

## Document Class Setup

### Basic LaTeX Document Structure

```latex
\documentclass{article}
\usepackage{neurips_2024}  % or neurips_2025, etc.
```

### Package Options

The NeurIPS style file supports three optional arguments:

| Option | Purpose | Usage |
|--------|---------|-------|
| `final` | Creates camera-ready copy for accepted papers | **Do NOT use at submission time** |
| `preprint` | Formats for preprint servers (e.g., arXiv) | Use for preprint versions only |
| `nonatbib` | Suppresses automatic natbib loading (avoid package clashes) | Use if natbib conflicts with other packages |

### Option Examples

```latex
% For submission (anonymous, with line numbers)
\usepackage{neurips_2024}

% For accepted paper (camera-ready, no anonymization)
\usepackage[final]{neurips_2024}

% For arXiv preprint
\usepackage[preprint]{neurips_2024}

% If natbib clashes with another package
\usepackage[nonatbib]{neurips_2024}
```

### Important Notes

- **At submission time**: Omit both `final` and `preprint` options. This will anonymize your submission and add line numbers to aid review.
- **For accepted papers**: Use the `final` option to remove anonymization and line numbers.
- **Do NOT modify the style file**: Tweaking the neurips.sty file may be grounds for rejection.

---

## Required Packages

The neurips.sty file automatically loads several standard packages. Here are the common packages you'll typically need:

```latex
\usepackage[utf8]{inputenc}       % UTF-8 encoding
\usepackage[T1]{fontenc}          % Font encoding
\usepackage{hyperref}             % Hyperlinks in PDF
\usepackage{url}                  % Formatted URLs
\usepackage{booktabs}             % Professional tables
\usepackage{amsfonts}             % Math fonts
\usepackage{nicefrac}             % Nice fractions (e.g., 1/2)
\usepackage{microtype}            % Microtypography improvements
\usepackage{graphicx}             % Include graphics
\usepackage{natbib}               % Bibliography management (loaded automatically)
```

### Graphics Package

If using graphics, the style file automatically handles graphics inclusion:

```latex
\usepackage[pdftex]{graphicx}
```

Specify figure widths as a multiple of line width:
```latex
\includegraphics[width=0.5\linewidth]{figure.pdf}
```

---

## Citations and References

### Default Bibliography System

- **natbib** is loaded by default by the NeurIPS style file
- You can use `\citet` for inline citations: `\citet{key}` produces "Author (Year)"
- You can use `\citep` for parenthetical citations: `\citep{key}` produces "(Author, Year)"

### Citation Styles

Citations may be either:
- **Author/Year style**: "Author (Year)" format
- **Numeric style**: [1], [2], etc.

**Important**: Maintain internal consistency. Do not mix citation styles within your paper.

### Bibliography Example

Create a `.bib` file with your references:

```bibtex
@article{Smith2020,
  author = {Smith, John and Doe, Jane},
  title = {Important Research Title},
  journal = {Journal Name},
  year = {2020},
  volume = {10},
  pages = {1--20}
}
```

Then include in your document:

```latex
\bibliographystyle{abbrvnat}  % or another natbib style
\bibliography{references}      % references.bib file
```

### Reference List Formatting

- Use unnumbered first-level heading for references: `\section*{References}`
- It is permissible to reduce font size to 9 point when listing references
- Any consistent reference style is acceptable (e.g., abbrvnat, plainnat, etc.)

---

## Page Layout and Margins

### Page Dimensions

| Dimension | Specification |
|-----------|---------------|
| **Text Width** | 5.5 inches (33 picas) |
| **Text Height** | 9 inches (54 picas) |
| **Left Margin** | 1.5 inches (9 picas) |

### Page Limit Requirements

- **Maximum content pages**: 9 pages (including figures and tables)
- **Additional pages allowed** (do not count toward limit):
  - Acknowledgments
  - References
  - Appendices (technical content)
  - Author checklist

**Important**: Papers exceeding the 9-page limit will not be reviewed.

### Default Typography

- **Font**: Times New Roman (selected automatically)
- **Font Size**: 10 point
- **Line Spacing**: 11 points (vertical spacing/leading)
- **Paragraph Spacing**: 5.5pt space between paragraphs
- **Paragraph Indentation**: No indentation (set to zero)

---

## Formatting Rules

### Section Headings

| Level | Font Size | Notes |
|-------|-----------|-------|
| First | 12 point | e.g., `\section{Introduction}` |
| Second | 10 point | e.g., `\subsection{Background}` |
| Third | 10 point | e.g., `\subsubsection{Details}` |

The style file applies custom spacing and formatting for headings automatically.

### Heading Syntax

```latex
\section{Main Section}
\subsection{Subsection}
\subsubsection{Subsubsection}
```

### Footnotes and Marginal Notes

- Footnotes should be used sparingly
- Configure with automatic spacing adjustments via the style file
- Avoid citations in footnotes when possible

---

## Figures and Tables

### General Requirements

- **All figures and tables must be centered**
- All figures and tables must be neat, clean, and legible
- Figures and tables count toward the 9-page limit
- Include descriptive captions for all figures and tables

### Figure Captions

```latex
\begin{figure}
  \centering
  \includegraphics[width=0.8\linewidth]{my_figure.pdf}
  \caption{Descriptive caption explaining the figure content.}
  \label{fig:my_label}
\end{figure}
```

### Table Requirements

- **Publication-quality tables** do NOT contain vertical rules
- Use horizontal rules for clarity (booktabs package is recommended)
- Tables should be professionally formatted and easy to read

### Table Example

```latex
\begin{table}
  \centering
  \begin{tabular}{lcc}
    \toprule
    Method & Accuracy & Runtime \\
    \midrule
    Baseline & 85\% & 10s \\
    Proposed & 92\% & 12s \\
    \bottomrule
  \end{tabular}
  \caption{Comparison of methods.}
  \label{table:results}
\end{table}
```

### Error Bars and Uncertainty

If error bars are reported in tables or plots:
- Explain in the text how they were calculated
- Reference the corresponding figures or tables in the text
- Ensure clarity on whether bars represent standard deviation, confidence intervals, etc.

---

## Author Information and Anonymity

### Author Declaration

At submission time:

```latex
\author{Anonymous submission}
```

In the final camera-ready version (after acceptance):

```latex
\author{
  Author One\thanks{Funding information} \\
  Institution One \\
  \texttt{email1@institution1.edu}
  \and
  Author Two \\
  Institution Two \\
  \texttt{email2@institution2.edu}
}

\date{Month Year}
```

### OpenReview Profile Requirements

Before the full paper deadline, **every co-author** must:
1. Create or update an OpenReview profile
2. Profile information is used for conflict resolution
3. Add all email addresses
4. Include affiliations under "Education & Career History"
5. For researchers without extensive publication records: fill in available information in DBLP and papers fields

### Anonymity

- Use the `\ack` environment provided in the style file for acknowledgments section
- This environment automatically hides acknowledgments in the anonymized submission
- Acknowledgments appear only in the final paper

---

## Acknowledgments and Declarations

### Acknowledgments Section

```latex
\begin{ack}
We thank [names/institutions]. This work was supported by [funding sources].
\end{ack}
```

Alternatively, use:

```latex
\section*{Acknowledgments}
Text of acknowledgments...
```

### Required Declarations

You **must declare**:

1. **Funding**: All financial activities supporting the submitted work
2. **Competing Interests**: Related financial activities outside the submitted work

### Placement

- Acknowledgments and declarations appear **before** the reference list
- Do **NOT** include in the anonymized submission (use `\ack` environment for automatic hiding)
- Include only in the final camera-ready version

### Example

```latex
\begin{ack}
We acknowledge funding from [Grant information].
The authors declare no competing interests.
\end{ack}
```

---

## Special Environments and Commands

### Checklist Environment

The style file includes a color-coded response system for paper checklists:

```latex
\begin{checklist}
    \item[Yes] Is the code available?
    \item[No] Did we discuss limitations?
    \item[NA] Does this work involve human subjects?
\end{checklist}
```

Color codes:
- **Blue**: Yes
- **Orange**: No
- **Gray**: NA (Not Applicable)

### Mathematical Typography

The style file automatically configures mathematical fonts. Use:

```latex
\usepackage{amsfonts}    % For math fonts (loaded)
\usepackage{amssymb}     % For additional math symbols
\usepackage{amsmath}     % For advanced math environments
```

---

## Common LaTeX Preamble for NeurIPS

Here's a typical complete preamble for a NeurIPS submission:

```latex
\documentclass{article}

% Packages
\usepackage{neurips_2024}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{url}
\usepackage{booktabs}
\usepackage{amsfonts}
\usepackage{nicefrac}
\usepackage{microtype}
\usepackage{graphicx}

% Title and Author
\title{Your Paper Title}
\author{Anonymous submission}

% If using natbib
\usepackage{natbib}

\begin{document}

\maketitle

\begin{abstract}
Abstract text here (150-250 words).
\end{abstract}

% Your content
\section{Introduction}
...

\section*{Acknowledgments}
[Include only in final version]

\begin{thebibliography}{99}
% References or use \bibliographystyle and \bibliography
\end{thebibliography}

\end{document}
```

---

## Download Links for Style Files

### Official NeurIPS Locations

- **NeurIPS 2024 Style Files**: https://neurips.cc/Conferences/2024/PaperInformation/StyleFiles
- **NeurIPS 2023 Style Files**: https://neurips.cc/Conferences/2023/PaperInformation/StyleFiles
- **NeurIPS 2025 Style Files**: https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles
- **Media Server**: https://media.neurips.cc/Conferences/

### GitHub Repository

- **Maintained Repository**: https://github.com/ArmageddonKnight/NeurIPS

### Overleaf Templates

- **NeurIPS 2024 Template**: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh
- **NeurIPS 2025 Ready Templates**: Available on Overleaf (search for "NeurIPS 2025")

---

## Formatting Instructions Documents

Complete formatting instructions are provided in official PDF documents:

- **NeurIPS 2024**: https://media.neurips.cc/Conferences/NeurIPS2024/Styles/neurips_2024.pdf
- **NeurIPS 2023**: https://media.neurips.cc/Conferences/NeurIPS2023/Styles/neurips_2023.pdf
- **NeurIPS 2025**: Check the official website for current year files

---

## Key Restrictions and Important Notes

### What NOT to Do

1. **Do NOT** use the `final` option at submission time
2. **Do NOT** modify the neurips.sty file (grounds for rejection)
3. **Do NOT** exceed 9 pages of content (excluding references/appendices)
4. **Do NOT** mix citation styles within your paper
5. **Do NOT** include author information in the main submission
6. **Do NOT** include competing interests or funding in the anonymized submission

### Submission Checklist

- [ ] Using current neurips.sty file (not older versions)
- [ ] Paper is 9 pages or less (excluding references)
- [ ] All authors have OpenReview profiles
- [ ] Using author/year OR numeric citations consistently
- [ ] Figures and tables are centered and legible
- [ ] References are properly formatted
- [ ] No author information visible (submission is anonymous)
- [ ] Style file not modified

---

## Additional Resources

### FAQ and Author Information

- **NeurIPS 2024 FAQ**: https://neurips.cc/Conferences/2024/PaperInformation/NeurIPS-FAQ
- **NeurIPS 2025 FAQ**: https://neurips.cc/Conferences/2025/PaperInformation/NeurIPS-FAQ
- **Submission Guide**: https://neurips.cc/

### Related Documentation

- **NeurIPS Call for Papers**: https://neurips.cc/Conferences/2025/CallForPapers
- **Author Instructions Archive**: https://neurips.cc/Conferences/2015/PaperInformation/AuthorSubmissionInstructions

---

## Version History

| Version | Year | LaTeX Version | Notes |
|---------|------|---------------|-------|
| neurips_2025.sty | 2025 | LaTeX 2ε | Current version |
| neurips_2024.sty | 2024 | LaTeX 2ε | Rewritten for LaTeX 2ε |
| neurips_2023.sty | 2023 | LaTeX 2ε | Last major update |
| Older versions | Pre-2023 | Various | No longer supported |

**Important**: Always use the current year's style file. Using outdated style files may lead to formatting issues or rejection.

---

## Quick Reference

### At Submission Time

```latex
\usepackage{neurips_2024}
\author{Anonymous submission}
```

### For Camera-Ready (Accepted) Version

```latex
\usepackage[final]{neurips_2024}
\author{%
  Author Names \\
  Institutions \\
  \texttt{emails}
}
```

### For ArXiv Preprint

```latex
\usepackage[preprint]{neurips_2024}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| natbib conflicts | Use `\usepackage[nonatbib]{neurips_2024}` and load natbib yourself with options |
| Old style file | Download the current neurips_20XX.sty for your submission year |
| Page limit exceeded | Reduce content, move details to appendix (appendix doesn't count toward limit) |
| Formatting changed | Do not modify neurips.sty; report issues to NeurIPS organizers |
| Missing citations | Use `\citet{key}` or `\citep{key}` from natbib |

---

## Final Notes

The NeurIPS style file is designed to ensure consistent, professional formatting across all submissions. Following these guidelines ensures your paper meets conference standards and presents your work in the best possible format.

**For the most up-to-date information**, always check the official NeurIPS website for the current year's submission guidelines and style files.

Last Updated: February 2024
Document Version: 1.0
