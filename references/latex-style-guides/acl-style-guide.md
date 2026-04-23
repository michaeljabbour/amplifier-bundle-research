# ACL LaTeX Style Guide

## Official Resources

- **GitHub Repository**: https://github.com/acl-org/acl-style-files
- **Formatting Guidelines**: https://acl-org.github.io/ACLPUB/formatting.html
- **Detailed Style Guide**: https://acl-org.github.io/ACLPUB/style.html
- **Overleaf Template**: https://www.overleaf.com/latex/templates/association-for-computational-linguistics-acl-conference/jvxskxpnznfj

---

## Paper Format Requirements

### A4 Paper Size (CRITICAL)

- **Paper dimensions**: 21 cm × 29.7 cm (A4 size)
- All papers must use A4 paper format
- Papers must look good both when printed at A4 size and when viewed onscreen as PDF (zoomable to any size)
- This is a mandatory requirement for all *ACL conference submissions

### Page Limits

**Review Versions:**
- Long papers: up to 8 pages of content + unlimited pages for references

**Final Versions (after acceptance):**
- Long papers: up to 9 pages of content + unlimited pages for acknowledgments and references

---

## LaTeX Style File Usage

### ACL Style Package

The official ACL LaTeX style file is called **acl.sty** and must be used for all submissions to *ACL conferences.

#### Loading the Style File

For the **review version** (during submission):
```latex
\documentclass{article}
\usepackage[review]{acl}
```

For the **final version** (after acceptance):
```latex
\documentclass{article}
\usepackage{acl}
```

The main difference is the `[review]` option, which should be included during the review process and omitted in the final version.

### Official Style Files Package

The ACL provides a complete package of style files available at https://github.com/acl-org/acl-style-files

The package includes:
- **acl.sty** - Main LaTeX style file for formatting
- **acl_latex.tex** - LaTeX source template document
- **acl_natbib.bst** - ACL bibliography style for natbib
- **custom.bib** - Example bibliography file
- **anthology.bib** - ACL Anthology bibliography reference

---

## Citation and Bibliography Setup

### Using natbib

ACL papers use the **natbib** package for managing citations and bibliography.

#### Loading natbib with ACL

```latex
\usepackage[sort]{natbib}
```

The `[sort]` option sorts citations by author name and year.

#### ACL Bibliography Style

Use the official ACL bibliography style file:
```latex
\bibliographystyle{acl_natbib}
```

This bibliography style must be paired with the acl.sty style file.

#### Citation Formats

Common natbib citation commands:
- `\citep{key}` - Parenthetical citation: (Author, Year)
- `\citet{key}` - Textual citation: Author (Year)
- `\cite{key}` - Standard citation

#### Bibliography Compilation

Standard BibTeX workflow:
1. Run LaTeX to generate .aux file
2. Run BibTeX to generate formatted bibliography
3. Run LaTeX twice more to resolve references

---

## Two-Column Format Specifications

### Column Layout

ACL papers use a **two-column format** by default with acl.sty.

#### Column Parameters

- **Number of columns**: 2
- **Column width**: Automatic (acl.sty handles spacing)
- **Column separation**: Standard spacing maintained by acl.sty

#### Starting with Two Columns

The two-column format is automatically applied when using acl.sty. No additional commands are needed.

### Title and Author Information

- **Title placement**: Centered at the top of the first page
- **Title formatting**: 15-point bold font
- **Title position**: 2.5 cm from the top of the page
- **Author names and affiliations**: Centered across both columns

#### Title and Author Example

```latex
\title{Your Paper Title Here}

\author{Author Name \\
        Affiliation / University \\
        Email address}

\date{}

\maketitle
```

### Column Spanning

For elements that need to span both columns:
- Use `\twocolumn` or `\onecolumn` commands as needed
- Abstract typically spans both columns
- Main text is in two-column format

#### Abstract and Keywords

- **Abstract location**: Typically spans both columns at the beginning
- **Abstract box**: May be formatted in a special box using acl.sty
- **Keywords**: Listed after abstract if required

---

## Font and Typography

### Font Requirements

- **Main text font**: Computer Modern (default TeX font) or similar proportional serif font
- **Font size**: 10 points for main text (set by acl.sty)
- **Line spacing**: Single spacing (set by acl.sty)

### Section Headings

- **Heading hierarchy**: Automatic formatting by acl.sty
- **Capitalization**: Title case for main headings
- **Formatting**: Bold headings with consistent spacing

---

## Margin Requirements

ACL style file sets margins automatically:
- Top margin: 2.5 cm
- Bottom margin: Standard
- Left margin: Standard
- Right margin: Standard

All margins are handled by acl.sty, ensuring compliance with ACL formatting standards.

---

## Graphics and Figures

### Figure Inclusion

```latex
\begin{figure}
  \centering
  \includegraphics[width=0.45\textwidth]{figure_name.pdf}
  \caption{Figure caption goes here}
  \label{fig:label}
\end{figure}
```

### Figure Placement

- Figures should be embedded in the document
- Placement: At top or bottom of columns when possible
- Width: Use `width=0.45\textwidth` or similar for single-column figures

---

## Tables

### Table Format

```latex
\begin{table}
  \centering
  \begin{tabular}{lll}
    \hline
    Column 1 & Column 2 & Column 3 \\
    \hline
    Data 1 & Data 2 & Data 3 \\
    \hline
  \end{tabular}
  \caption{Table caption}
  \label{tab:label}
\end{table}
```

### Table Guidelines

- Keep tables simple and readable
- Avoid excessive lines
- Ensure readability within column width

---

## Common Packages to Use with ACL

```latex
\usepackage[review]{acl}      % ACL style file
\usepackage[sort]{natbib}     % Bibliography management
\usepackage{graphicx}         % Graphics support
\usepackage{amsmath}          % Mathematical symbols
\usepackage{amssymb}          % Additional math symbols
\usepackage{url}              % URL formatting
```

---

## Document Template Example

```latex
\documentclass{article}
\usepackage[review]{acl}
\usepackage[sort]{natbib}

\title{Your Paper Title}
\author{Author Name \\ University \\ email@example.com}
\date{}

\begin{document}

\maketitle

\begin{abstract}
Your abstract here.
\end{abstract}

\section{Introduction}
Introduction text here.

\section{Method}
Method description here.

\section{Experiments}
Experiments and results here.

\section{Conclusions}
Conclusions here.

\bibliographystyle{acl_natbib}
\bibliography{custom}

\end{document}
```

---

## Key Compliance Checklist

- [ ] Using `\usepackage[review]{acl}` for submission (or `\usepackage{acl}` for final)
- [ ] Paper size is A4 (21 cm × 29.7 cm)
- [ ] Bibliography style is set to `acl_natbib`
- [ ] Using natbib for citations (`\citep` or `\citet`)
- [ ] Two-column layout is active (automatic with acl.sty)
- [ ] Content within page limits (8 pages for review + refs)
- [ ] Title is 15-point bold and 2.5 cm from top
- [ ] Author names and affiliations centered across both columns
- [ ] All figures and tables have captions
- [ ] No manual formatting overrides that conflict with acl.sty

---

## Additional Resources

- **ACL Official Website**: https://www.aclweb.org/
- **ACL Submissions and Style**: https://acl-org.github.io/ACLPUB/
- **GitHub Style Files Repository**: https://github.com/acl-org/acl-style-files
- **ACLPUB Detailed Style**: https://acl-org.github.io/ACLPUB/style.html

---

*Last Updated: February 2026*
