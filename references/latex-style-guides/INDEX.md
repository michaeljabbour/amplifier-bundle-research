# LaTeX Style Guides Repository Index

This directory contains comprehensive formatting guides for academic conference submissions.

## Available Guides

### 1. NeurIPS Style Guide
**File**: `neurips-style-guide.md` (15 KB, 558 lines)

Complete reference for Neural Information Processing Systems (NeurIPS) LaTeX formatting requirements.

**Key Topics Covered**:
- Style file installation and usage
- Document class setup with package options
- Required LaTeX packages
- Citation and bibliography guidelines
- Page layout specifications (5.5" × 9")
- Formatting rules for sections, figures, tables
- Author information and anonymity requirements
- Acknowledgments and required declarations
- Complete working LaTeX preamble examples
- Official download links
- Troubleshooting guide

**Quick Facts**:
- Maximum content: 9 pages (refs/appendices don't count)
- Font: Times New Roman, 10pt
- Default package: natbib for citations
- Current version: neurips_2025.sty
- Style file options: `final`, `preprint`, `nonatbib`

**Document Sections**:
1. Overview
2. Style File Basics
3. Document Class Setup
4. Required Packages
5. Citations and References
6. Page Layout and Margins
7. Formatting Rules
8. Figures and Tables
9. Author Information and Anonymity
10. Acknowledgments and Declarations
11. Special Environments and Commands
12. Common LaTeX Preamble
13. Download Links
14. Key Restrictions
15. Additional Resources
16. Version History
17. Quick Reference
18. Troubleshooting
19. Final Notes

**Official Resources**:
- NeurIPS 2024: https://neurips.cc/Conferences/2024/PaperInformation/StyleFiles
- NeurIPS 2025: https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles
- GitHub: https://github.com/ArmageddonKnight/NeurIPS
- Overleaf: https://www.overleaf.com/latex/templates/neurips-2024/tpsbbrdqcmsh

---

### 2. ACL Style Guide
**File**: `acl-style-guide.md` (7.3 KB)

Reference for Association for Computational Linguistics (ACL) conference submissions.

---

### 3. ACM Style Guide
**File**: `acm-style-guide.md` (15 KB, 507 lines)

Comprehensive guide for ACM conference and publication submissions.

---

### 4. IEEE Style Guide
**File**: `ieee-style-guide.md` (15 KB, 546 lines)

Complete reference for IEEE conference and journal submissions.

---

### 5. ICML Style Guide
**File**: `icml-style-guide.md` (16 KB, 445 lines)

Comprehensive guide for International Conference on Machine Learning submissions.

---

### 6. arXiv Style Guide
**File**: `arxiv-style-guide.md` (35 KB, 740+ lines)

Complete reference for arXiv preprint submissions with critical .bbl file requirements and HTML rendering best practices.

**Key Topics Covered**:
- No style file required (flexibility)
- Critical .bbl file inclusion requirements
- Recommended document classes (article, revtex4, amsart)
- Font recommendations (Computer Modern, Times)
- Source file submission requirements
- HTML rendering and accessibility
- Metadata and category taxonomy
- AutoTeX compilation system
- Top 10 common submission errors
- Version control and updates
- License options (CC BY 4.0, etc.)

---

### 7. Quick Summary
**File**: `NEURIPS_SUMMARY.txt` (2.1 KB)

Quick reference card with key formatting rules and options for NeurIPS submissions.

---

## How to Use

### For NeurIPS Submissions

1. **Download the main guide**: `neurips-style-guide.md`
2. **Quick reference**: Check `NEURIPS_SUMMARY.txt` for common options
3. **Find style files**: Use the links provided in the "Download Links" section
4. **Setup your document**: Follow the "Document Class Setup" section
5. **Troubleshooting**: Refer to the "Troubleshooting" section if you encounter issues

### Key Decision Points

#### Choosing Package Options

| Your Goal | Use This | Example |
|-----------|----------|---------|
| Submit paper | Default | `\usepackage{neurips_2024}` |
| Final accepted paper | Add `final` | `\usepackage[final]{neurips_2024}` |
| ArXiv preprint | Add `preprint` | `\usepackage[preprint]{neurips_2024}` |
| Avoid natbib conflicts | Add `nonatbib` | `\usepackage[nonatbib]{neurips_2024}` |

#### Quick Setup Template

```latex
\documentclass{article}
\usepackage{neurips_2024}

% Include required packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{graphicx}

\title{Your Paper Title}
\author{Anonymous submission}

\begin{document}

\maketitle

\begin{abstract}
Abstract (150-250 words)
\end{abstract}

\section{Introduction}
% Your content

\section*{Acknowledgments}
% Only in final version

\bibliography{references}

\end{document}
```

---

## Important Reminders

### NeurIPS Specific

- **Always** use the current year's style file (e.g., `neurips_2025.sty` for 2025)
- **Never** modify the `.sty` file (grounds for rejection)
- **Omit** `final` and `preprint` options when submitting
- **Keep** papers to 9 pages maximum (excluding references)
- **Use** "Anonymous submission" for author names in submissions
- **Include** acknowledgments only in the final camera-ready version
- **Ensure** all co-authors have OpenReview profiles

### Citation Guidelines

- Choose either **Author/Year** or **Numeric** style
- **Maintain consistency** throughout the paper
- Use `\citet{key}` for inline citations
- Use `\citep{key}` for parenthetical citations
- natbib is loaded by default

### Page Layout

- Text area: 5.5 inches wide × 9 inches tall
- Font: Times New Roman 10pt
- Line spacing: 11pt
- Paragraph spacing: 5.5pt
- No paragraph indentation

---

## Content Created Date

Generated: February 4, 2025
Last Updated: February 4, 2025
Repository Version: 1.0

---

## File Locations

All files are stored in this bundle at:
```
references/latex-style-guides/
```
(relative to the `amplifier-bundle-research` repo root)

### File List

| File | Size | Type | Purpose |
|------|------|------|---------|
| `neurips-style-guide.md` | 15 KB | Markdown | Complete NeurIPS formatting reference |
| `NEURIPS_SUMMARY.txt` | 2.1 KB | Text | Quick reference card |
| `acl-style-guide.md` | 7.3 KB | Markdown | ACL formatting guide |
| `acm-style-guide.md` | 15 KB | Markdown | ACM formatting guide |
| `INDEX.md` | This file | Markdown | Repository index and guide |

---

## Quick Links

### Official Conference Websites

- [NeurIPS 2025](https://neurips.cc/Conferences/2025/)
- [NeurIPS 2024](https://neurips.cc/Conferences/2024/)
- [ACL](https://www.aclweb.org/)
- [ACM](https://www.acm.org/)

### Style File Repositories

- [NeurIPS GitHub](https://github.com/ArmageddonKnight/NeurIPS)
- [Overleaf Templates](https://www.overleaf.com/)
- [Media Server](https://media.neurips.cc/)

### Additional Resources

- [NeurIPS 2025 FAQ](https://neurips.cc/Conferences/2025/PaperInformation/NeurIPS-FAQ)
- [NeurIPS Call for Papers](https://neurips.cc/Conferences/2025/CallForPapers)

---

## Tips for Academic Paper Writing

1. **Start with templates**: Use official Overleaf or GitHub templates
2. **Follow guidelines strictly**: Non-compliant formatting can lead to rejection
3. **Use version control**: Track changes with Git throughout writing
4. **Consistency is key**: Maintain consistent citation and formatting styles
5. **Review examples**: Look at accepted papers to understand formatting expectations
6. **Test compilation**: Regularly compile your LaTeX to catch errors early
7. **Check word limits**: Keep content within specified page limits
8. **Proofread carefully**: Review formatting one final time before submission

---

## Notes

- These guides are compiled from official conference documentation and resources
- Information is current as of February 2025
- Always verify with official conference websites for the most up-to-date requirements
- Different workshops or special tracks may have modified requirements

---

**For detailed NeurIPS information**: See `neurips-style-guide.md`
**For quick reference**: See `NEURIPS_SUMMARY.txt`
