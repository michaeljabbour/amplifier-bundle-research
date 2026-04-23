# IEEE LaTeX Style Guide Documentation

## Overview

IEEEtran is the official LaTeX document class for IEEE transactions journals, conferences, and correspondence. Version 1.8b (August 26, 2015) is the current standard, distributed under the LaTeX Project Public License (LPPL) v1.3.

The IEEEtran class produces officially-correct output for IEEE publications with improved interword spacing that requires less hyphenation and creates more pleasant text, especially for two-column layouts.

---

## IEEEtran.cls Usage

### Basic Document Structure

IEEEtran is loaded as a document class with various options:

```latex
\documentclass[<options>]{IEEEtran}
```

### Class Options Overview

IEEEtran provides five major modes encompassing different publication types:

1. **Conference Mode** - For IEEE conference papers
2. **Journal Mode** (default) - For IEEE journal articles
3. **Technote Mode** - For correspondence and short papers
4. **Peerreview Mode** - For peer review submissions
5. **Final Mode** (default) - For final camera-ready papers

---

## Conference vs. Journal Options

### Basic Document Type Options

| Mode | Option | Usage |
|------|--------|-------|
| Conference | `conference` | `\documentclass[conference]{IEEEtran}` |
| Journal | `journal` | `\documentclass[journal]{IEEEtran}` (default) |
| Technical Note | `technote` | `\documentclass[technote]{IEEEtran}` |
| Peer Review | `peerreview` | `\documentclass[peerreview]{IEEEtran}` |
| Peer Review CA | `peerreviewca` | Implies `peerreview` mode |

### Key Differences

**Conference Papers:**
- Typically use two-column format
- Compact spacing for page limits
- Example: `\documentclass[conference]{IEEEtran}`

**Journal Papers:**
- Can use one or two columns depending on journal
- More generous spacing for readability
- Example: `\documentclass[journal]{IEEEtran}`
- Example with Computer Society: `\documentclass[journal,compsoc]{IEEEtran}`

---

## Society Format Options

IEEE publications use different formatting standards by society:

### Format Options

| Society | Option | Requirements |
|---------|--------|--------------|
| IEEE Communications Society | `comsoc` | Requires Times math font (newtxmath v1.451+) |
| IEEE Computer Society | `compsoc` | Standard formatting |
| IEEE Transactions on Magnetics | `transmag` | Specialized layout |

### Important Distinction

- **`comsoc`** = IEEE Communications Society (requires Times math font)
- **`compsoc`** = IEEE Computer Society (standard)
- These are mutually exclusive options

Example usage:
```latex
\documentclass[conference,compsoc]{IEEEtran}    % Computer Society conference
\documentclass[journal,comsoc]{IEEEtran}        % Communications Society journal
```

---

## Two-Column Specifications

### Column Format Options

| Option | Description |
|--------|-------------|
| `twocolumn` | Two-column layout (default) |
| `onecolumn` | Single-column layout |

### Default Settings

The default document configuration is:
- US Letter paper (8.5" x 11")
- 10pt font size
- **Two-column layout** (twocolumn)
- One-sided printing
- Final mode
- Journal mode

### Page Dimensions

For US Letter format:
- **Minimum margins:** 0.625" left, 0.625" right, 1" top, 0.75" bottom
- **Text region:** No more than 7.25" wide x 9.25" tall
- **Alternative:** 1" margins all around (if individual margin setting is difficult)

### Column Width and Spacing

Two-column format specifications:
- Each column is roughly 3.5 inches wide with appropriate gutter spacing
- Large figures and tables may span both columns
- Figures and tables may not extend into page margins

---

## Font Size Options

IEEEtran supports four font sizes:

| Size | Description |
|------|-------------|
| 9pt | Smaller font option |
| 10pt | **Standard and most common** |
| 11pt | Larger font option |
| 12pt | Largest font option |

Default: **10pt** (used by vast majority of papers)

### Line Spacing

- Minimum line spacing: 10pt
- Margins and spacing can be larger than minimum
- IEEEtran automatically manages interword spacing for better text flow

---

## Numbered Citation Style

### Citation Format

IEEE uses **numbered citations in square brackets**, which is the standard and required format.

### In-Text Citation Rules

1. **Numbering:** Citations are numbered consecutively [1], [2], [3], etc. in the order they appear
2. **Brackets:** Always use square brackets [n], not parentheses or other formats
3. **Punctuation:** Sentence punctuation follows the citation bracket
   - Example: "The system uses TCP/IP protocols [1]."
   - Example: "See reference [2] for details."

4. **Multiple Citations:** Use comma-separated numbers [1], [2], [3] or ranges [1]–[3]

### Bibliography Organization

- References are **organized numerically**, not alphabetically
- Numbers appear in square brackets on the left of each entry
- Entries are indented consistently to separate from numbers
- Reference list appears at the end of the document

### BibTeX Configuration

To use IEEE citation format with BibTeX:

```latex
% In document preamble:
\usepackage[numbers]{natbib}

% In document body:
\cite{key}

% At end of document:
\bibliographystyle{IEEEtranN}
\bibliography{references}
```

### Citation Commands

- `\cite{key}` - Standard citation: [1]
- `\cite{key1,key2}` - Multiple citations: [1], [2]
- `\cite{key1,key2,key3}` - Consecutive citations: [1]–[3]

### BibTeX Style Options

The IEEEtran bibliography style comes in variants:
- `IEEEtran` - Standard IEEE format
- `IEEEtranN` - Normalized version
- `IEEEtranS` - Short format
- `IEEEtranSA` - Short format with aliases

---

## Figure and Table Formatting

### Figure Specifications

**Caption Placement:**
- Figure captions must be **below the figures**
- Caption format: "Fig. 1." (abbreviated with period)
- Two spaces after the figure number before the caption text
- Example: "Fig. 1  Block diagram of the system."

**Figure Guidelines:**
- Do not place borders or frames around figures
- Use the abbreviation "Fig." even at the beginning of a sentence
- Large figures may span both columns but cannot extend into margins
- Avoid colored figures unless necessary (print constraints)

**Placement Rules:**
- IEEE journals favor **top-of-page placement** for figures
- Avoid bottom-of-page floats (rarely used in IEEE publications)
- **Never place figures in the first column of the first page**
- Rarely place figures in the second column of the first page (avoid if possible)
- Use top floats (preferred) rather than bottom floats

### Table Specifications

**Caption Placement:**
- Table captions must be **above the tables**
- Caption format: "TABLE I." or "Table I." (using Roman numerals or Arabic numerals)
- Example: "TABLE I  Performance Metrics of the Proposed Algorithm"

**Table Guidelines:**
- Keep table captions concise and descriptive
- Use professional formatting without excess decorative lines
- Align content consistently within cells
- Use horizontal lines sparingly (top, bottom, and header separation)
- Avoid vertical lines within tables when possible

**Formatting Conventions:**
- Use clear column headers
- Provide units for numerical values
- Number tables consecutively: Table I, Table II, etc.
- Use footnotes for supplementary information

**Placement Rules:**
- Same as figures: top-of-page preferred
- Can span both columns if necessary
- Cannot extend into page margins

---

## Section Heading Numbering

### Default (Non-compsoc) Modes

Section numbering varies by level:

1. **Level 1 (Section):** Upper case Roman numerals (I, II, III, IV, V, etc.)
2. **Level 2 (Subsection):** Upper case letters (A, B, C, D, etc.)
3. **Level 3 (Subsubsection):** Arabic numerals (1, 2, 3, 4, etc.)
4. **Level 4 (Paragraph):** Lower case letters (a, b, c, d, etc.)

Example structure:
```
I. INTRODUCTION
   A. Overview
      1. Background
         a) Historical context
```

### LaTeX Commands

```latex
\section{Introduction}        % Level 1: Upper Roman
\subsection{Overview}         % Level 2: Upper letters
\subsubsection{Background}    % Level 3: Arabic numbers
\paragraph{Detail}            % Level 4: Lower letters
```

**Note:** Section headings should not be indented. The first paragraph after a section heading typically is not indented.

---

## Abstract and Keywords

### Abstract Requirements

**Length:**
- Regular papers: **100-200 words**
- Correspondence/short papers: **No more than 50 words**
- Comments: **No more than 50 words**

**Content Guidelines:**
- Clearly state the nature and significance of the paper
- Must NOT include mathematical expressions
- Must NOT include bibliographic references
- Summarize purpose, methods, and key findings
- Provide scope of work without excessive detail

### Keywords and Index Terms

**Number of Keywords:** 3-5 keywords or phrases recommended

**Keyword Guidelines:**
- Describe the research topic accurately
- Use terminology from IEEE taxonomy when available
- Clearly define any abbreviations
- Help readers locate the article in databases
- Optimally characterize the paper's content
- Should closely reflect the paper's topic

### LaTeX Implementation

```latex
\begin{abstract}
   Your 100-200 word abstract text here...
\end{abstract}

\begin{IEEEkeywords}
   keyword1, keyword2, keyword3, keyword4, keyword5
\end{IEEEkeywords}
```

---

## Document Modes and Variants

### Version Information

- **Current Version:** 1.8b (August 26, 2015)
- **Previous Major Version:** 1.7 (introduced Computer Society support)
- **License:** LaTeX Project Public License (LPPL) v1.3

### Additional Mode Options

**Draft and Review Modes:**

| Option | Description |
|--------|-------------|
| `draft` | Draft mode for manuscript submission |
| `draftcls` | Implied by `draft` option |
| `final` | Final camera-ready version (default) |
| `nofonttune` | Disables automatic font spacing adjustments |

### Font Management

**Important Note:** Do NOT adjust fonts or use packages that alter fonts with IEEEtran v1.6 and later, unless specifically requested by the target journal or conference.

The `nofonttune` option can disable IEEEtran's automatic font spacing optimization if needed.

---

## Common Document Configurations

### Conference Paper Template

```latex
\documentclass[conference]{IEEEtran}
\usepackage[numbers]{natbib}

\title{Your Paper Title}
\author{Author Names}

\begin{document}

\maketitle

\begin{abstract}
   Abstract text...
\end{abstract}

\begin{IEEEkeywords}
   keywords
\end{IEEEkeywords}

\section{Introduction}
   % Content

\section{Methodology}
   % Content

% ... additional sections

\bibliographystyle{IEEEtranN}
\bibliography{references}

\end{document}
```

### Journal Paper Template

```latex
\documentclass[journal]{IEEEtran}
\usepackage[numbers]{natbib}

\title{Your Article Title}
\author{Author Names \\ Organization}

\begin{document}

\maketitle

\begin{abstract}
   Abstract text...
\end{abstract}

\begin{IEEEkeywords}
   keywords
\end{IEEEkeywords}

\section{Introduction}
   % Content

\section{Analysis}
   % Content

% ... additional sections

\bibliographystyle{IEEEtranN}
\bibliography{references}

\end{document}
```

### Computer Society Conference

```latex
\documentclass[conference,compsoc]{IEEEtran}
```

---

## Official Template Links

### Primary Resources

1. **IEEE Template Selector** (Official)
   - URL: https://template-selector.ieee.org/
   - Most up-to-date LaTeX and Word templates
   - Recommended for finding current conference/journal templates

2. **IEEE Conference Templates**
   - Official IEEE page: https://www.ieee.org/conferences/publishing/templates
   - Direct conference submission templates

3. **Overleaf Templates** (Collaborative Editor)
   - IEEE Conference Template: https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn
   - IEEE Bare Demo Template: https://www.overleaf.com/latex/templates/ieee-bare-demo-template-for-conferences/ypypvwjmvtdf
   - IEEE Journal Template: https://www.overleaf.com/latex/templates/ieee-journal-paper-template/jbbbdkztwxrd
   - IEEE Demo for Computer Society: https://www.overleaf.com/latex/templates/ieee-demo-template-for-computer-society-conferences/hzzszpqfkqky
   - Overleaf IEEE Gallery: https://www.overleaf.com/gallery/tagged/ieee-official

4. **CTAN (Comprehensive TeX Archive Network)**
   - IEEEtran Package: https://ctan.org/pkg/ieeetran
   - Complete package with documentation

5. **GitHub Resources**
   - IEEE Template Repository: https://github.com/uefs/ieee-template-latex
   - IEEE Transactions Template: https://github.com/bardsoftware/template-ieee-transactions
   - IEEE Conference Template: https://github.com/DanySK/Template-LaTeX-IEEE-Conference-Proceedings

### Documentation

6. **IEEEtran HOWTO** (Main Reference Document)
   - Comprehensive user manual for IEEEtran class
   - Version 1.8b reference
   - Available from official sources and GitHub repositories

7. **IEEE Author Center**
   - Structure Your Article: https://journals.ieeeauthorcenter.ieee.org/
   - IEEE Reference Guide for citations
   - Formatting guidelines for different publication types

---

## Key Formatting Rules Summary

### Do's

- **DO** use the standard `\documentclass[conference]{IEEEtran}` or `[journal]` options
- **DO** place figure captions below figures with "Fig." abbreviation
- **DO** place table captions above tables
- **DO** use numbered citations in square brackets [1], [2], etc.
- **DO** number citations consecutively in order of appearance
- **DO** use two-column format (default)
- **DO** limit abstract to 100-200 words (regular papers)
- **DO** include 3-5 keywords
- **DO** use Times-compatible fonts with `comsoc` mode
- **DO** favor top-of-page placement for figures and tables
- **DO** use provided class options rather than manual formatting
- **DO** follow section numbering: I, II, III (upper Roman) for level 1

### Don'ts

- **DON'T** adjust fonts or use font-altering packages without cause
- **DON'T** place figures in first column of first page
- **DON'T** use bottom-of-page floats (avoid placement)
- **DON'T** put borders around figures
- **DON'T** manually adjust margins or paper size
- **DON'T** use alphabetical reference ordering (must be numerical)
- **DON'T** extend figures/tables into page margins
- **DON'T** confuse `comsoc` (Communications Society) with `compsoc` (Computer Society)
- **DON'T** include mathematical expressions or references in abstract
- **DON'T** use parenthetical citations (use square brackets only)

---

## Additional Notes

### Version History

- **IEEEtran v1.8b** (Current, August 2015)
  - comsoc mode for Communications Society
  - Enhanced column specifications
  - Index macros for glossaries support
  - Page header improvements
  - Spacing control hooks
  - IEEEnoauxwrite command

- **IEEEtran v1.7**
  - New `compsoc` option for Computer Society
  - Backward compatibility improvements
  - Enhanced LaTeX package integration

### Obtaining Latest Version

- **CTAN (Comprehensive TeX Archive Network):** https://ctan.org/pkg/ieeetran
- **IEEE Computer Society:** Official distribution site
- **Overleaf:** Integrated templates with latest version
- **GitHub:** Community repositories with examples

### Support and Compatibility

- Works with standard LaTeX distributions (MiKTeX, TeX Live, MacTeX)
- Compatible with BibTeX for bibliography management
- Supports XeLaTeX and LuaLaTeX
- Works with major editors: Overleaf, TeXShop, WinEdt, VS Code, etc.

---

## References for This Guide

This documentation was compiled from:

- IEEE Official Template Selector
- IEEEtran HOWTO Documentation (v1.8b)
- Official IEEE Author Center Guidelines
- GitHub IEEEtran Repositories
- IEEE Conference and Journal Submission Guides
- Overleaf IEEE Template Collections
- CTAN IEEEtran Package Documentation
