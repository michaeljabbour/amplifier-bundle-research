# ICML LaTeX Style Guide Documentation

## Overview

This document provides comprehensive formatting and style requirements for papers submitted to the International Conference on Machine Learning (ICML). The guidelines apply to ICML 2024, 2025, and 2026 submissions. All submissions must strictly adhere to these formatting standards, or papers will be automatically rejected.

**Key Point**: There is no support for any software other than LaTeX. All submissions must be in PDF format prepared using the official ICML LaTeX style files.

---

## Official Style Files and Downloads

### ICML 2025 Style Files
- **Download URL**: https://media.icml.cc/Conferences/ICML2025/Styles/icml2025.zip
- **Main Style File**: `icml2025.sty`
- **Bibliography Style**: `icml2025.bst`
- **Usage**: `\usepackage[accepted]{icml2025}` (use `[accepted]` option for camera-ready, omit for anonymous submission)

### ICML 2024 Style Files
- **Download URL**: https://media.icml.cc/Conferences/ICML2024/Styles/icml2024.zip
- **Main Style File**: `icml2024.sty`
- **Bibliography Style**: `icml2024.bst`

### Overleaf Templates
- **ICML 2025 Template**: https://www.overleaf.com/latex/templates/icml2025-template/dhxrkcgkvnkt
- **ICML 2024 Template**: https://www.overleaf.com/latex/templates/genlaw-icml-2024/dfnrrdnkqswy

---

## Paper Structure and Page Limits

### Submission Format
- **Main Body**: Up to 8 pages (automatically rejected if exceeded)
- **References**: Unlimited pages
- **Appendix**: Unlimited pages
- **File Format**: All content must be in a single PDF file
- **Final/Camera-Ready Version**: Up to 9 pages for main body allowed (1 extra page permitted for accepted papers)

**Important**: Upon acceptance, ICML publishes the complete submission including appendices and references as a whole document.

---

## Page Layout and Dimensions

### Overall Page Specifications
- **Page Size**: Standard letter (8.5" × 11")
- **Top Margin**: 1.0 inch (2.54 cm)
- **Left Margin**: 0.75 inches (1.91 cm)
- **Right Margin**: 0.75 inches (1.91 cm)
- **Bottom Margin**: Approximately 1.0 inch

### Two-Column Format
- **Number of Columns**: 2 columns
- **Column Width**: Approximately 3.25 inches each
- **Column Spacing**: 0.25 inches (between columns)
- **Total Text Width**: 6.75 inches
- **Text Height**: 9.0 inches

### Usage
The `icml2024.sty` (or `icml2025.sty`) file automatically implements the two-column layout. You can control the layout using:
- `\twocolumn` - Switch to two-column format
- `\onecolumn` - Switch to one-column format (typically used for appendices if preferred)

---

## Font and Typography Requirements

### Primary Font Requirements
- **Body Text Font**: **Times** (or Times New Roman)
- **Font Size**: **10 point**
- **Line Spacing**: **11 points** (vertical spacing)
- **Type-3 Fonts**: **AVOID** - Do not include Type-3 fonts in your PDF

### Heading Hierarchy

#### Title
- **Font Size**: 14 point
- **Weight**: Bold
- **Alignment**: Centered
- **Formatting**: Positioned between two horizontal rules (1 point thick)
- **Spacing**: 1.0 inch between top rule and top edge of page
- **Capitalization**: Capitalize first letter of content words, rest in lowercase

#### Abstract Heading
- **Font Size**: 11 point
- **Weight**: Bold
- **Alignment**: Centered
- **Spacing**: Single line

#### Abstract Body
- **Font Size**: 10 point
- **Line Spacing**: 11 points
- **Indentation**: 0.25 inches more than normal left and right margins
- **Length**: Keep abstracts concise and informative

#### Section Headings
- **Font Size**: Typically 11 point
- **Weight**: Bold
- **Alignment**: Flush left
- **Capitalization**: Capitalize first letter of first and last words, other important words

#### Subsection Headings
- **Font Size**: 10 point
- **Weight**: Bold or italic
- **Alignment**: Flush left

### Special Formatting Notes
- **Emphasis**: Use italic for emphasis, not bold
- **Small Caps**: May be used for author citations in first mention
- **References**: Use the bibliography style specified (see Citation Style section)

---

## Citation and Bibliography Style

### Citation Package
- **Package Required**: `natbib.sty` (included in style file package)
- **Bibliography Style File**: `icml2024.bst` or `icml2025.bst` (included in style file package)
- **Reference Format**: **APA style**

### Citation Format in Text

#### Author(s) in Text
If author names appear in the text, use:
```latex
\citet{key}  % Result: "Author (year)"
```

#### Names Not in Text
If citation is separate from the narrative:
```latex
\citep{key}  % Result: "(Author, year)"
```

#### Examples
- Correct: "Smith (2023) demonstrated..."
- Correct: "This was shown previously (Smith, 2023)."
- **Avoid**: "Smith, 2023 demonstrated..." (incorrect placement)

### Bibliography Entry Format
The `icml2024.bst` bibliography style file automatically formats references in APA style, including:
- Authors' last names and initials
- Publication year in parentheses
- Title in sentence case
- Journal/conference name in italics
- Volume and issue numbers
- Page numbers
- DOI (if available)

### Multiple Citations
- Use `\citep{key1,key2,key3}` for multiple citations: `(Author1, 2020; Author2, 2021)`
- Use `\citet{key1,key2}` for integrated citations: `Author1 (2020) and Author2 (2021)`

### Bibliography Compilation
```latex
\bibliographystyle{icml2024}  % or icml2025
\bibliography{your_references}  % points to .bib file
```

---

## Author Information and Double-Blind Review

### Anonymity Requirements
- **Review Process**: Double-blind review (authors and reviewers are anonymous)
- **Author Information**: Must NOT appear in submitted version
- **Anonymity Method**: Use `\icmlauthor{...}` command with appropriate style option

### Using Author Tags
```latex
\usepackage[accepted]{icml2024}  % Only renders authors at camera-ready stage
\icmlauthor{First Author}{Institution, Country}
\icmlauthor{Second Author}{Institution, Country}
```

When using `[accepted]` option, author information is rendered. Without this option (for anonymous submission), author names are hidden.

### Anonymity Best Practices
1. **Refer to own work in third person**: "Smith (2020) showed..." instead of "We showed (Smith, 2020)..."
2. **Omit acknowledgments** during review phase
3. **Do not include grant numbers** in submission
4. **Avoid public GitHub links** that could reveal identity
5. **Use anonymous repositories** if supplementary code is needed
6. **Remove author metadata** from PDF properties

---

## Figures, Tables, and Illustrations

### Figure Specifications
- **Placement**: Below the text that references them
- **Captions**: Should appear below figures
- **Font Size**: Captions typically 9 or 10 point
- **Legend**: Include legends inside the figure when space permits
- **Quality**: Use vector graphics (PDF, EPS) where possible for clarity
- **File Formats**: PDF, EPS, PNG with adequate resolution (300 dpi minimum for print)

### Table Specifications
- **Placement**: Above tables when possible
- **Captions**: Should appear above tables
- **Font Size**: Typically 9 or 10 point
- **Lines**: Use clear borders and gridlines
- **Alignment**: Align columns clearly for readability

### Cross-References
```latex
\begin{figure}
  \includegraphics[width=\columnwidth]{figure_name}
  \caption{Description of figure}
  \label{fig:label}
\end{figure}

\begin{table}
  \caption{Description of table}
  \label{tab:label}
  \begin{center}
    % table content
  \end{center}
\end{table}
```

---

## Equation and Mathematical Notation

### Inline Mathematics
- Use `$...$` for inline equations
- Keep inline equations minimal to maintain readability
- Ensure consistent notation throughout paper

### Display Mathematics
- Use `\[...\]` or `equation*` environment for centered display equations
- Number important equations using `equation` environment with `\label{}`
- Use `\ref{}` or `\eqref{}` for cross-references

### Notation Consistency
- Define all symbols and notation on first use
- Use consistent formatting for variables (italics for variables, upright for functions)
- Define non-standard notation in a notation section if paper includes many symbols

---

## Supplementary Material

### Types Supported
1. **Supplementary Manuscripts**: Extended proofs, additional experiments, etc.
2. **Code/Data**: Implementation code, datasets, anonymized repositories

### Submission Format
- **Code Submissions**: ZIP file or PDF
- **Data Submissions**: ZIP file or anonymous repository
- **Anonymity**: Remove author names and identifying information
- **GitHub**: May use anonymous GitHub repositories on dedicated branches

### Important Notes
- Supplementary material is **NOT** published or archived
- Authors are responsible for long-term archival
- Material must be anonymized (no author names in code/comments)
- Include GitHub links in separate text file within submission

### Review Access
- Reviewers may consult supplementary material at their discretion
- Material critical to evaluation must be in the main paper (8-page limit)
- Do not rely on reviewers reviewing supplementary material

---

## Preparation Best Practices

### LaTeX Document Structure
```latex
\documentclass{article}
\usepackage[accepted]{icml2025}  % Use [accepted] only for camera-ready
\usepackage{natbib}              % For citations
\usepackage{graphicx}            % For figures
\usepackage{amsmath}             % For math

\title{Your Paper Title}
\icmlauthor{Author Name}{Institution}
\icmlauthor{Another Author}{Institution}

\begin{document}

\maketitle

\begin{abstract}
Abstract text here (should be comprehensive but concise)
\end{abstract}

\section{Introduction}
% Content...

\bibliography{references}
\bibliographystyle{icml2025}

\end{document}
```

### PDF Generation
- **Recommended**: Use pdflatex for best results
- **Font Embedding**: Ensure all fonts are embedded in final PDF
- **Verification**: Check PDF properties to confirm font embedding
- **File Size**: Keep PDF under reasonable size (typically < 10 MB)

### Common Issues to Avoid
1. **Type-3 Fonts**: Will be rejected; use PostScript or TrueType fonts only
2. **Margin Violations**: Use style file; manual margin adjustments often cause rejection
3. **Page Limit Exceeded**: Submit will be automatically rejected if main body > 8 pages
4. **Missing References**: Ensure all citations in text appear in bibliography
5. **Anonymity Breaches**: Remove all identifying information from submission version
6. **Image Embedding**: Embed all images; do not use external linked images

---

## Submission Requirements and Rules

### Submission Format
- **File Type**: PDF only
- **Compression**: Use reasonable compression (not overly compressed to maintain quality)
- **Single File**: Main paper with appendices all in one PDF
- **Anonymity**: Remove author information from PDF metadata

### Mandatory Confirmations
- Authors must confirm compliance with ICML code of conduct
- Submissions must be original work not under review elsewhere
- Dual submission policy: Papers substantially similar to published work will be rejected

### Key Deadlines and Policies
- **Page Limit Enforcement**: Automatic rejection for main body > 8 pages
- **Formatting Compliance**: Automatic rejection for template deviations
- **Anonymity**: Automatic rejection for papers that reveal author identity
- **Resolution of Conflicts**: Double-blind review ensures anonymous evaluation

---

## Official Resources and Links

### Primary Documentation
- **ICML 2024 Author Instructions**: https://icml.cc/Conferences/2024/AuthorInstructions
- **ICML 2025 Author Instructions**: https://icml.cc/Conferences/2025/AuthorInstructions
- **ICML 2026 Author Instructions**: https://icml.cc/Conferences/2026/AuthorInstructions

### Style Files and Examples
- **ICML 2024 Style Files**: https://media.icml.cc/Conferences/ICML2024/Styles/
- **ICML 2025 Style Files**: https://media.icml.cc/Conferences/ICML2025/Styles/
- **Example Papers**: Available in style file packages

### Template Resources
- **Overleaf ICML 2025 Template**: https://www.overleaf.com/latex/templates/icml2025-template/dhxrkcgkvnkt
- **ICML Website**: https://icml.cc/
- **ICML Proceedings Archive**: https://proceedings.mlr.press/

### Additional Information
- **Call for Papers**: https://icml.cc/Conferences/2025/CallForPapers
- **Code of Conduct**: https://icml.cc/public/CodeOfConduct
- **Accessibility Guidelines**: Follow ICML's inclusive writing guidelines for color-blind and visually impaired readers

---

## Common Questions and Clarifications

### Q: Can I use Word instead of LaTeX?
**A**: No. ICML only supports LaTeX. All submissions must be prepared using the official ICML LaTeX style files.

### Q: What if my paper is longer than 8 pages?
**A**: Your submission will be **automatically rejected**. The page limit is strictly enforced and includes all text, figures, and tables in the main body (not references or appendices).

### Q: When should I use the `[accepted]` option?
**A**: Use `\usepackage[accepted]{icml2024}` ONLY for the camera-ready (final) version after your paper is accepted. Use without `[accepted]` for anonymous submissions during review.

### Q: How should I cite my own unpublished work?
**A**: Include the work as supplementary material and cite it as "anonymous reference" in the text. Cite as "[Anonymous, 2025]" or similar to maintain anonymity during review.

### Q: Are appendices included in the 8-page limit?
**A**: No. Appendices, references, and supplementary material are unlimited. Only the main body (before the appendix starts) counts toward the 8-page limit.

### Q: What fonts should I use to avoid Type-3 font errors?
**A**: Use Times, Computer Modern, or standard PostScript fonts. Avoid decorative or specialty fonts. When using pdflatex with `natbib` and standard packages, Type-3 font issues are uncommon if you follow the standard template.

### Q: How do I ensure proper font embedding?
**A**: Use pdflatex and avoid special font packages. The standard ICML template handles this correctly. Check your PDF properties (File → Properties in most PDF viewers) to verify font embedding.

---

## Version History

- **ICML 2024**: icml2024.sty, icml2024.bst
- **ICML 2025**: icml2025.sty, icml2025.bst (current)
- **ICML 2026**: icml2026.sty (upcoming)

The formatting requirements have remained consistent across these versions with minor updates to the style files.

---

## Document Preparation Checklist

Before submitting to ICML, verify:

- [ ] Used official ICML LaTeX style file (without `[accepted]` option for submission)
- [ ] Main body text is exactly 10 point Times font
- [ ] Line spacing is 11 points throughout
- [ ] Paper is exactly in two-column format
- [ ] Top margin is 1.0 inch, side margins are 0.75 inches
- [ ] Title is 14 point bold, centered between horizontal rules
- [ ] Abstract is properly formatted with 11 point bold heading
- [ ] No author names or identifying information in submission version
- [ ] All figures and tables are properly captioned and referenced
- [ ] Bibliography uses `icml2024.bst` or `icml2025.bst` style
- [ ] All citations are in text and in bibliography
- [ ] No Type-3 fonts in PDF
- [ ] All fonts are embedded in PDF
- [ ] Main body does not exceed 8 pages (excluding references/appendices)
- [ ] References and appendices are unlimited pages
- [ ] Submitted as single PDF file
- [ ] Double-checked anonymity (no identifying metadata)
- [ ] Confirmed compliance with code of conduct
- [ ] Verified paper is not under review elsewhere (dual submission policy)

---

## Additional Notes

### Accessibility and Inclusivity
ICML encourages authors to follow accessibility guidelines:
- Ensure figures are accessible to colorblind readers (use colorblind-friendly palettes)
- Include alt-text for figures in PDF (for digital versions)
- Use descriptive captions for all visual content
- Use inclusive and respectful language throughout
- Update bibliography with current names and venue information

### Code Reproducibility
- Authors are strongly encouraged to submit code
- Use anonymized repositories during review
- Provide clear README files for code execution
- Include required dependencies and versions

### Submission Platform
- **ICML 2024 and earlier**: CMT (Conference Management Toolkit)
- **ICML 2025 and later**: OpenReview.net
- Follow platform-specific instructions for file uploads
- Ensure all supplementary materials are properly tagged

---

*This guide consolidates information from official ICML author instructions (2022-2025) and standard LaTeX formatting practices. Always refer to the most current year's official guidelines at icml.cc for any updates or changes.*
