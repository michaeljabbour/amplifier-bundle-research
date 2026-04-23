# arXiv LaTeX Style Guide

## Overview

This is a comprehensive reference guide for preparing and submitting LaTeX documents to arXiv.org, the premier open-access archive for scientific preprints. Unlike conference-specific style files, arXiv emphasizes **flexibility, portability, and automated processing** while maintaining high standards for scientific communication.

**Key Philosophy**: arXiv does not impose a specific visual style but requires that submissions be processable by their automated system (AutoTeX) and convertible to multiple formats including PDF and HTML.

**Current System**: TeX Live 2025 (updated regularly)
**Accepted Formats**: (La)TeX, PDFLaTeX (preferred); PDF, HTML (with restrictions)
**Submission Cost**: Free for authors

---

## arXiv's Unique Position

### Purpose and Mission

arXiv serves as:
- **Preprint repository**: Share research before peer review
- **Permanent archive**: All versions preserved indefinitely
- **Open access platform**: Free to read, free to submit
- **Multi-format delivery**: PDF, HTML (experimental), mobile-optimized views

### Key Differences from Conference Submissions

| Aspect | Conference (e.g., NeurIPS) | arXiv |
|--------|---------------------------|-------|
| **Style file** | Required specific .sty | No specific style required |
| **Formatting** | Strict visual requirements | Flexible, must compile cleanly |
| **Page limits** | Enforced (e.g., 9 pages) | No page limits |
| **Anonymity** | Required at submission | Not required (optional) |
| **Acceptance** | Peer review required | Moderation only (topical check) |
| **Permanence** | Final version only | All versions preserved |
| **Updates** | Not permitted | Replacements create new versions |

### Why Submit TeX Source?

arXiv **strongly prefers** TeX/LaTeX source because:
1. **Future-proof archiving**: Source remains processable as technology evolves
2. **Format flexibility**: Generate PDF, HTML, mobile views from source
3. **Accessibility**: Convert to accessible formats (screen readers, text-to-speech)
4. **Text extraction**: Full-text search, indexing, data mining
5. **Reproducibility**: Others can build upon your work

---

## Document Class Setup

### Recommended Document Classes

arXiv processes a wide range of document classes. The most common and reliable:

#### Standard Article Class

```latex
\documentclass[11pt]{article}
```

**Advantages**:
- Universal compatibility
- Well-tested by arXiv AutoTeX
- Clean HTML conversion
- No dependencies on external style files

**When to use**: General papers, interdisciplinary work, preprints for any journal

#### REVTeX 4 (Physics)

```latex
\documentclass[aps,prl,twocolumn]{revtex4-2}
```

**Advantages**:
- Standard for physics journals (Physical Review, etc.)
- Built-in two-column layout
- Comprehensive bibliography handling
- Well-supported by arXiv

**When to use**: Physics papers, especially those targeting APS journals

**Note**: Use `revtex4-2` (current version), not older `revtex4-1` or `revtex4`

#### AMS Article Classes

```latex
\documentclass{amsart}
```

**Advantages**:
- Designed for mathematics
- Excellent theorem environments
- Superior mathematical typography

**When to use**: Mathematics papers, papers with heavy theorem content

#### Other Supported Classes

- **`IEEEtran`**: IEEE journal submissions
- **`elsarticle`**: Elsevier journals
- **`svjour3`**: Springer journals
- **`quantumarticle`**: Quantum journal

**Important**: Always use the **official, unmodified** versions of these classes. Custom modifications may break AutoTeX processing.

### Basic Document Structure

Minimal working example:

```latex
\documentclass[11pt]{article}

% Essential packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{graphicx}

\title{Your Paper Title}
\author{Author One \\ Institution One \and Author Two \\ Institution Two}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
Your abstract here.
\end{abstract}

\section{Introduction}
Your content...

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

---

## Font Recommendations

### Default Fonts (Recommended)

arXiv's AutoTeX works best with standard TeX fonts:

#### Computer Modern (LaTeX default)

```latex
% No special font commands needed - this is the default
\documentclass{article}
```

**Advantages**:
- Universal compatibility
- No additional packages required
- Guaranteed to work on arXiv
- Excellent mathematical typography

#### Times Roman

```latex
\usepackage{times}
% or modern alternative:
\usepackage{mathptmx}  % Times for text and math
```

**Advantages**:
- More compact than Computer Modern
- Common in published journals
- Good for papers with page constraints

### Font Encoding

Always specify proper font encoding for international characters:

```latex
\usepackage[T1]{fontenc}      % 8-bit font encoding
\usepackage[utf8]{inputenc}   % UTF-8 input encoding
```

### Mathematical Fonts

For mathematics-heavy papers:

```latex
\usepackage{amsmath}   % AMS mathematical facilities
\usepackage{amssymb}   % AMS mathematical symbols
\usepackage{amsfonts}  % AMS fonts
```

### Fonts to Avoid

**Do NOT use** fonts that require external files or proprietary licenses:
- System-specific fonts (fonts installed only on your computer)
- Proprietary commercial fonts
- Unusual/uncommon fonts not in TeX Live

**Exception**: You can include `.mf` (METAFONT) files and `fontmap.map` with special handling via `00README.XXX` directive.

---

## Bibliography Requirements (CRITICAL!)

### The .bbl File Requirement

**MOST IMPORTANT**: arXiv does **NOT** run BibTeX during processing. You **MUST** include your compiled `.bbl` file.

#### Workflow for Bibliography

1. **Compile locally** (run multiple times):
   ```bash
   pdflatex paper.tex
   bibtex paper
   pdflatex paper.tex
   pdflatex paper.tex
   ```

2. **Locate the .bbl file**: After running BibTeX, you'll have `paper.bbl` in your directory

3. **Include .bbl in submission**: Upload both `paper.tex` AND `paper.bbl` to arXiv

4. **File naming**: The `.bbl` filename **must match** your main `.tex` filename
   - Main file: `paper.tex`
   - Bibliography: `paper.bbl` ✓
   - Bibliography: `mybib.bbl` ✗ (will not work!)

### BibTeX Setup

In your `.tex` file:

```latex
\bibliographystyle{plain}  % or abbrv, alpha, unsrt, etc.
\bibliography{references}   % references.bib file
```

### Common Bibliography Styles

| Style | Description | Output Example |
|-------|-------------|----------------|
| `plain` | Alphabetical by author | [1] Author (Year)... |
| `unsrt` | Order of citation | [1] First cited... |
| `abbrv` | Abbreviated names | A. Smith (2020)... |
| `alpha` | Alphabetic labels | [Smi20] Smith (2020)... |
| `abbrvnat` | Natural sciences (natbib) | Smith et al. (2020) |
| `plainnat` | Natural style (natbib) | Smith and Jones (2020) |

### Using natbib

For author-year citations:

```latex
\usepackage{natbib}
\bibliographystyle{abbrvnat}

% In text:
\citet{key}   % Author (Year)
\citep{key}   % (Author, Year)

% At end:
\bibliography{references}
```

**Remember**: Still need to include the `.bbl` file!

### Biblatex Compatibility

If using biblatex (modern alternative):

```latex
\usepackage[backend=biber]{biblatex}
\addbibresource{references.bib}

% Compile with biber instead of bibtex
% Then include the generated .bbl file
```

**Warning**: arXiv's biblatex version may differ from yours. Check the submission log for compatibility warnings.

### Alternative: Embedded Bibliography

Instead of BibTeX, you can manually include references:

```latex
\begin{thebibliography}{99}
\bibitem{key1}
Author Name, ``Paper Title,'' \emph{Journal}, vol. X, pp. Y-Z, Year.

\bibitem{key2}
Another Author, ``Another Title,'' \emph{Conference}, Year.
\end{thebibliography}
```

**Advantage**: No `.bbl` file needed
**Disadvantage**: More tedious, no automatic formatting

---

## Figure and Table Guidelines

### Figure Formats

arXiv accepts two processing modes with different figure requirements:

#### For LaTeX/TeX Processing

**Accepted formats**: PostScript (`.ps`, `.eps`)

```latex
\usepackage{graphicx}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{figure.eps}
  \caption{Figure caption describing the content.}
  \label{fig:example}
\end{figure}
```

#### For PDFLaTeX Processing

**Accepted formats**: PDF (`.pdf`), JPEG (`.jpg`), PNG (`.png`)

```latex
\usepackage[pdftex]{graphicx}

\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{figure.pdf}
  \caption{Figure caption describing the content.}
  \label{fig:example}
\end{figure}
```

### CRITICAL: Do Not Mix Figure Formats

**Common mistake**: Using both `.eps` and `.pdf` figures in the same document.

- If AutoTeX detects `.eps` → processes as LaTeX → **all** figures must be `.ps`/`.eps`
- If AutoTeX detects `.pdf`/`.jpg`/`.png` → processes as PDFLaTeX → **all** figures must be PDF/JPEG/PNG

**Solution**: Convert all figures to one format before submission.

### Figure Best Practices

#### File Naming

**Use only these characters**: `a-z A-Z 0-9 _ + - . , =`

**Avoid**:
- Spaces: `my figure.pdf` ✗ → `my_figure.pdf` ✓
- Special characters: `figure?.pdf` ✗
- Unicode: `figure™.pdf` ✗

#### Case Sensitivity

arXiv's filesystem is **case-sensitive**:

```latex
% Your LaTeX:
\includegraphics{Figure1.pdf}

% But your file is named: figure1.pdf
% Result: COMPILATION ERROR
```

**Always match case exactly** in `\includegraphics` commands.

#### Relative Paths Only

```latex
% Correct:
\includegraphics{figures/plot.pdf}
\includegraphics{../data/graph.pdf}

% WRONG (absolute path):
\includegraphics{/Users/myname/paper/figure.pdf}
```

Absolute paths will fail on arXiv's servers.

### Accessibility: Alt Text for Figures

For HTML rendering and accessibility:

```latex
\usepackage{graphicx}

\includegraphics[
  width=0.8\linewidth,
  alt={Graph showing accuracy vs. training epochs, with accuracy increasing from 60% to 95% over 100 epochs}
]{accuracy_plot.pdf}
```

**Benefits**:
- Screen readers can describe images
- Better HTML conversion
- Improved searchability

### Table Formatting

#### Professional Tables

Use the `booktabs` package for publication-quality tables:

```latex
\usepackage{booktabs}

\begin{table}[htbp]
  \centering
  \caption{Comparison of methods}
  \label{tab:results}
  \begin{tabular}{lcc}
    \toprule
    Method & Accuracy & Time (s) \\
    \midrule
    Baseline & 85.2\% & 10.3 \\
    Proposed & 92.7\% & 12.1 \\
    \bottomrule
  \end{tabular}
\end{table}
```

**Key principles**:
- **No vertical lines** (professional standard)
- Use `\toprule`, `\midrule`, `\bottomrule` (not `\hline`)
- Keep tables simple and readable

#### Wide Tables

For tables wider than text width:

```latex
\begin{table*}[htbp]  % Note the asterisk for two-column spanning
  \centering
  % ... table content
\end{table*}
```

---

## Source File Requirements

### What to Submit

arXiv needs **ALL** files necessary to compile your paper:

**Required**:
- Main `.tex` file (or multiple `.tex` files)
- All `.bbl` files (bibliography)
- All figure files
- Any custom `.sty` or `.cls` files you use

**Optional**:
- `00README.XXX` file (special processing instructions)
- Ancillary files (datasets, code)

### File Organization

#### Simple Submission (Single Directory)

```
paper.tex
paper.bbl
figure1.pdf
figure2.pdf
custom_macros.sty
```

Upload all files directly, or create `paper.tar.gz` containing all files.

#### Submission with Subdirectories

```
main.tex
main.bbl
figures/
  figure1.pdf
  figure2.pdf
sections/
  intro.tex
  methods.tex
```

**Must use** `.tar.gz` or `.zip` to preserve directory structure.

### Creating Archive Files

#### Using tar (Linux/Mac):

```bash
tar -czf submission.tar.gz paper.tex paper.bbl figures/
```

#### Using zip:

```bash
zip -r submission.zip paper.tex paper.bbl figures/
```

### The 00README.XXX File

Special directives file for non-standard processing:

```
# File: 00README.XXX

# Ignore specific files
supplementary.tex ignore

# Disable HyperTeX (if causing conflicts)
nohypertex

# Keep PostScript comments (for binary figures)
paper.dvi keepcomments

# Custom font handling
fontmap directive
```

**Common uses**:
- Mark files to ignore
- Disable hyperref processing
- Specify non-standard compilation

---

## Metadata and Categories

### Required Metadata Fields

When submitting to arXiv, you provide metadata **separately** from your TeX source:

#### Title

- Use sentence case or title case
- **Do NOT** use all uppercase
- Can include LaTeX math: `$\mathcal{O}(n)$`
- Keep concise (no abstracts in title)

```latex
% In your .tex file:
\title{Deep Learning for Quantum State Tomography}

% Avoid:
\title{DEEP LEARNING FOR QUANTUM STATE TOMOGRAPHY}  % All caps
```

#### Authors

Format: `Firstname Lastname` or `Firstname Middlename Lastname`

```latex
\author{
  John Smith\thanks{Corresponding author} \\
  Department of Physics, MIT \\
  \texttt{jsmith@mit.edu}
  \and
  Jane Doe \\
  Google Research \\
  \texttt{jdoe@google.com}
}
```

**In arXiv submission form**:
```
John Smith (MIT), Jane Doe (Google Research)
```

**Important**: 
- Full names (no "et al.")
- Affiliations in parentheses
- Separate multiple authors with commas or "and"

#### Abstract

- Maximum **1920 characters**
- Plain text with basic LaTeX math
- No `\abstract{}` command text in the abstract itself
- Avoid excessive TeX formatting

```latex
\begin{abstract}
We present a novel approach to quantum state tomography using deep 
neural networks. Our method achieves 95\% accuracy on benchmark 
datasets while reducing computational cost by $\mathcal{O}(n^2)$ 
compared to traditional methods.
\end{abstract}
```

#### Comments Field

Optional but recommended for:
- Page/figure count: "12 pages, 5 figures"
- Software/data availability: "Code available at http://..."
- Submission status: "Submitted to Physical Review Letters"
- Related materials: "See ancillary files for dataset"

### arXiv Categories

Select appropriate category from arXiv's taxonomy. Major categories:

#### Physics
- `astro-ph.*`: Astrophysics
- `cond-mat.*`: Condensed Matter
- `gr-qc`: General Relativity and Quantum Cosmology
- `hep-*`: High Energy Physics
- `nucl-*`: Nuclear Physics
- `physics.*`: Physics (various subcategories)
- `quant-ph`: Quantum Physics

#### Mathematics
- `math.AG`: Algebraic Geometry
- `math.CO`: Combinatorics
- `math.DG`: Differential Geometry
- `math.NT`: Number Theory
- `math.PR`: Probability
- `math.ST`: Statistics Theory

#### Computer Science
- `cs.AI`: Artificial Intelligence
- `cs.CL`: Computation and Language
- `cs.CV`: Computer Vision
- `cs.LG`: Machine Learning
- `cs.NE`: Neural and Evolutionary Computing

#### Cross-Listing

You can cross-list to secondary categories:
- **Primary**: Where paper will be announced
- **Secondary**: Additional relevant categories

**Example**: Primary `quant-ph`, Secondary `cs.LG` (quantum ML paper)

### Optional Classification Fields

#### MSC Class (Mathematics)

Mathematics Subject Classification:

```
MSC-class: 14J60 (Primary); 14F05, 14J26 (Secondary)
```

#### ACM Class (Computer Science)

ACM Computing Classification:

```
ACM-class: F.2.2; I.2.7
```

---

## Compilation Workflow

### How arXiv Processes Your Submission

arXiv's AutoTeX system:

1. **Detects format**: LaTeX vs. PDFLaTeX (based on figure types)
2. **Identifies main file**: Looks for `\documentclass`
3. **Runs compilation**:
   - For LaTeX: `latex → dvips → ps2pdf`
   - For PDFLaTeX: `pdflatex` (no intermediate steps)
4. **Does NOT run**: BibTeX, Biber, Makeindex (you must provide outputs)
5. **Generates**: PDF, HTML (experimental), source tarball

### Testing Before Submission

**Always test locally** with clean compilation:

```bash
# Remove all auxiliary files
rm *.aux *.log *.bbl *.blg *.out *.toc

# Compile from scratch
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex

# Verify paper.pdf looks correct
# Verify paper.bbl exists
```

### Compiler Selection

AutoTeX automatically chooses:

**LaTeX** if it finds:
- `.eps` or `.ps` figures
- Packages requiring DVI mode

**PDFLaTeX** if it finds:
- `.pdf`, `.jpg`, `.png` figures
- Modern packages requiring PDF mode

**Force specific compiler** (if needed):

```latex
% First line of .tex file:
%&latex
% or
%&pdflatex
```

### Handling Multiple .tex Files

If your paper has multiple `.tex` files:

**Option 1: Use `\input`** (recommended)

```latex
% main.tex
\documentclass{article}
\begin{document}
\input{intro.tex}
\input{methods.tex}
\input{results.tex}
\end{document}
```

**Option 2: Use `\include`**

```latex
% main.tex
\documentclass{article}
\begin{document}
\include{intro}
\include{methods}
\end{document}
```

**Important**: With `\include`, all files **must be in top-level directory** (AutoTeX cannot write `.aux` files to subdirectories).

**Option 3: Multiple top-level files**

You can select multiple main `.tex` files during submission. arXiv concatenates their output.

---

## HTML Rendering Considerations

### arXiv's HTML Papers Initiative

As of 2024, arXiv generates **accessible HTML** versions alongside PDF:

**Benefits**:
- Screen reader compatible
- Mobile-friendly
- Text-to-speech support
- Reflow to any screen size
- Better accessibility for visually impaired researchers

**Status**: Experimental (not all papers convert perfectly)

### Semantic LaTeX for Better HTML

Use **meaningful** LaTeX commands, not visual formatting:

#### Good: Semantic Markup

```latex
\section{Introduction}
\emph{important concept}
\textbf{key finding}
```

Conveys **structure and meaning** → converts well to HTML

#### Bad: Visual-Only Markup

```latex
{\normalfont\fontsize{12}{15}\bfseries Introduction}
{\it important concept}
{\bf key finding}
```

Only specifies **appearance** → poor HTML conversion

### Packages for HTML Success

arXiv uses **LaTeXML** for HTML conversion. Best compatibility with:

**Well-supported packages**:
- `graphicx` (standard graphics)
- `amsmath`, `amssymb` (mathematics)
- `hyperref` (links)
- `theorem` (theorem environments)
- `algorithm2e` (algorithms)

**Check supported packages**: https://dlmf.nist.gov/LaTeXML/manual/included.bindings/

### Alt Text for Images (Accessibility)

```latex
\includegraphics[
  width=0.8\linewidth,
  alt={Scatter plot showing positive correlation between 
       variables X and Y, with R-squared value of 0.89}
]{correlation_plot.pdf}
```

**Why important**:
- Blind researchers using screen readers
- Text-only displays
- Failed image loading
- Search engine indexing

### Structured Abstracts

For HTML conversion:

```latex
\begin{abstract}
\textbf{Background:} Context for the work...

\textbf{Methods:} How the study was conducted...

\textbf{Results:} Key findings...

\textbf{Conclusions:} Implications...
\end{abstract}
```

---

## Accessibility Recommendations

### General Principles

1. **Use standard LaTeX constructs** (not custom macros for structure)
2. **Provide alt text** for all figures
3. **Use semantic markup** (`\emph` not `\it`)
4. **Avoid custom fonts** (stick to standard fonts)
5. **Test HTML output** after submission

### Color and Contrast

For color figures:

- Ensure sufficient contrast (especially for colorblind readers)
- Don't rely solely on color to convey information
- Use line styles (solid, dashed) in addition to colors

```latex
% Good: combines color with line style
\plot[color=blue, line=solid] {data1}
\plot[color=red, line=dashed] {data2}
```

### Mathematical Accessibility

Use standard math environments:

```latex
% Good - semantic meaning
\begin{equation}
  E = mc^2
  \label{eq:einstein}
\end{equation}

% Avoid - display-only formatting
$$E = mc^2$$
```

### Table Accessibility

```latex
\begin{table}
  \caption{Descriptive caption explaining table contents}
  \label{tab:results}
  \begin{tabular}{lcc}
    \toprule
    \textbf{Method} & \textbf{Accuracy} & \textbf{Time} \\
    \midrule
    % ... data rows
    \bottomrule
  \end{tabular}
\end{table}
```

**Best practices**:
- Descriptive captions
- Header row with bold labels
- Simple structure (avoid merged cells)

---

## Common Submission Errors (Top 10)

### 1. Missing .bbl File

**Error**: `Empty bibliography` or references not appearing

**Cause**: Forgot to include `.bbl` file

**Solution**: 
```bash
# Generate .bbl file
bibtex paper
# Include paper.bbl in submission
```

### 2. Mixed Figure Formats

**Error**: `Cannot determine size of graphic` or similar

**Cause**: Using both `.eps` and `.pdf` figures

**Solution**: Convert all figures to one format:
```bash
# Convert EPS to PDF
epstopdf figure.eps
# Or convert PDF to EPS
pdftops -eps figure.pdf figure.eps
```

### 3. Case Sensitivity Mismatches

**Error**: `File 'Figure1.pdf' not found`

**Cause**: `\includegraphics{Figure1.pdf}` but file is `figure1.pdf`

**Solution**: Match case exactly:
```latex
% If file is figure1.pdf:
\includegraphics{figure1.pdf}  % Correct
```

### 4. Absolute File Paths

**Error**: Files not found during compilation

**Cause**: 
```latex
\includegraphics{/Users/myname/paper/figure.pdf}
```

**Solution**: Use relative paths:
```latex
\includegraphics{figure.pdf}
\includegraphics{figures/plot.pdf}
```

### 5. Missing Style Files

**Error**: `File 'mystyle.sty' not found`

**Cause**: Custom `.sty` file not included in submission

**Solution**: Include ALL custom style files in upload

### 6. Subdirectory `.aux` File Issues

**Error**: `Can't write 'subdir/file.aux'`

**Cause**: Using `\include{subdir/file}` (tries to write `.aux` to subdirectory)

**Solution**: Use `\input` instead:
```latex
\input{subdir/file}  % No .aux file generated
```

Or move file to top directory.

### 7. HyperTeX Conflicts

**Error**: `Option clash for package hyperref`

**Cause**: arXiv loads hyperref automatically, conflicts with your options

**Solution**: Disable arXiv's hyperref:
```
# In 00README.XXX file:
nohypertex
```

Then load hyperref yourself with desired options.

### 8. Incompatible Biblatex Version

**Error**: `File 'paper.bbl' is wrong format version`

**Cause**: Your biblatex version differs from arXiv's

**Solution**: 
- Check arXiv's TeX Live version
- Regenerate `.bbl` with compatible biblatex version
- Or switch to traditional BibTeX

### 9. Invalid Characters in Filenames

**Error**: File not found or processing failure

**Cause**: `my figure.pdf` (space), `figure?.pdf` (special char)

**Solution**: Rename files:
```bash
mv "my figure.pdf" my_figure.pdf
```

### 10. PDF Conversion Failures

**Error**: Complex section structure causing PDF errors

**Cause**: hyperref generates bad pdfmarks with complex numbering

**Solution**: Disable bookmarks:
```latex
\usepackage[bookmarks=false]{hyperref}
```

Or disable HyperTeX entirely (see #7).

---

## Version Control and Updates

### arXiv's Versioning System

**All versions are permanent**: You cannot delete a version once announced.

**Version numbering**: `arXiv:YYMM.NNNNN` → `arXiv:YYMM.NNNNNv2`, `v3`, etc.

### Submitting a Replacement

**When to replace**:
- Correcting errors
- Adding new results
- Responding to feedback
- Journal acceptance (add journal reference)

**How to replace**:

1. Log in to arXiv
2. Find paper in your list
3. Click "Replace" (not "New submission")
4. Upload updated files
5. **Explain changes** in comments field

### Replacement Comments

**Good practice**:
```
Comments: 15 pages, 7 figures. v2: Fixed error in Theorem 3, 
added comparison with method X, updated references
```

Helps readers understand what changed between versions.

### Withdrawal vs. Replacement

**Withdrawal**:
- Paper remains visible but marked "withdrawn"
- Use only for serious errors or ethical issues
- Cannot be undone

**Replacement**:
- Old version remains accessible
- New version becomes default
- Preferred method for updates

### Journal Publication Updates

After journal acceptance:

1. **Submit replacement** (optional but recommended)
2. **Add journal reference**:
   ```
   Journal-ref: Phys. Rev. Lett. 125, 123456 (2020)
   ```
3. **Add DOI**:
   ```
   DOI: 10.1103/PhysRevLett.125.123456
   ```

**Can be done without replacement**: arXiv provides form to add journal info to existing versions.

---

## License Options

### Available Licenses

arXiv offers several licenses (chosen at submission):

#### CC BY 4.0 (Recommended)

**Creative Commons Attribution**

- Most permissive
- Anyone can reuse with attribution
- Promotes open science
- Compatible with most journals

```
License: arXiv.org perpetual non-exclusive license to 
distribute this article (Minimal rights for arXiv.org)
+ CC BY 4.0
```

#### CC BY-SA 4.0

**Creative Commons Attribution-ShareAlike**

- Derivative works must use same license
- "Copyleft" for papers

#### CC BY-NC-SA 4.0

**Creative Commons Attribution-NonCommercial-ShareAlike**

- No commercial use
- ShareAlike requirement
- More restrictive

#### CC0 (Public Domain)

**Creative Commons Zero**

- Waive all copyright
- Dedicate to public domain
- Maximum freedom

#### arXiv.org Non-exclusive License (Default)

**Minimum permission required by arXiv**

- arXiv can distribute
- You retain copyright
- Others must contact you for reuse

### Choosing a License

**Recommended**: CC BY 4.0 for maximum impact and compatibility

**Consider**:
- Journal requirements (check before choosing restrictive license)
- Funding agency policies (some require open licenses)
- Future reuse (permissive licenses increase citations)

### Copyright Notice

You can include copyright notice on first page:

```latex
\title{Paper Title}
\author{...}
\date{...}

\begin{document}
\maketitle

\noindent
\textcopyright{} 2024 Author Name. Licensed under CC BY 4.0.

\begin{abstract}
...
\end{abstract}
```

**Important**: Copyright notice must not contradict license granted to arXiv.

---

## Comparison with Conference Formats

### Converting Conference Papers to arXiv

Many authors post conference submissions to arXiv. Key adaptations:

#### From NeurIPS/ICML Style

```latex
% Original (conference):
\usepackage{neurips_2024}
\author{Anonymous submission}  % For review

% arXiv version:
\documentclass{article}
\usepackage{neurips_2024}
\usepackage[preprint]{neurips_2024}  % Removes anonymization
\author{Full author names and affiliations}
```

**Or** remove conference style entirely for standard article format.

#### From IEEE Style

```latex
% Original:
\documentclass[conference]{IEEEtran}

% For arXiv: keep or switch to article
\documentclass[journal]{IEEEtran}  % Journal format
% or
\documentclass{article}  % Standard format
```

#### From ACM Style

```latex
% Original:
\documentclass[sigconf]{acmart}

% For arXiv:
\documentclass{article}
% Re-implement basic formatting without acmart
```

### Page Limit Considerations

**Conference**: Strict page limits (e.g., NeurIPS 9 pages)

**arXiv**: No page limits!

**Strategy**:
- Main paper matches conference version
- Add appendices with extended proofs/experiments
- Include supplementary material inline

```latex
\section{Introduction}
...

\section{Conclusion}
...

\bibliographystyle{plain}
\bibliography{references}

% Additional material for arXiv version
\appendix
\section{Extended Proofs}
...

\section{Additional Experiments}
...
```

### Anonymity Handling

**Conference**: Anonymous during review

**arXiv**: Never anonymous (but can post after review starts, check conference rules)

**Common practice**:
1. Submit to conference (anonymous)
2. Simultaneously or shortly after, post to arXiv (with names)
3. After acceptance, update arXiv with journal/conference reference

---

## Troubleshooting Section

### Diagnostic Tools

#### Check Compilation Log

arXiv provides detailed logs:
- Look for errors (search for `!`)
- Check warnings (especially font/figure warnings)
- Verify file detection (main file, figures)

#### Common Log Messages

**"Processing with PDFLaTeX"** → `.pdf`/`.jpg`/`.png` figures expected

**"Processing with LaTeX"** → `.eps`/`.ps` figures expected

**"Missing \begin{document}"** → AutoTeX can't find main file

### Quick Fixes Reference

| Problem | Quick Fix |
|---------|-----------|
| Empty bibliography | Include `.bbl` file |
| Figure not found | Check filename case sensitivity |
| Wrong processor (LaTeX vs PDFLaTeX) | Convert all figures to one format |
| Package not found | Include `.sty` file or use standard alternative |
| Font errors | Use standard fonts (Computer Modern, Times) |
| Hyperref conflicts | Add `nohypertex` to `00README.XXX` |
| Subdirectory aux errors | Use `\input` not `\include` |
| PDF conversion fails | Disable bookmarks: `\usepackage[bookmarks=false]{hyperref}` |

### Getting Help

**arXiv support**:
- Email: help@arxiv.org
- Include: arXiv paper ID, error messages, log excerpts

**Community resources**:
- TeX Stack Exchange: https://tex.stackexchange.com/ (tag: arxiv)
- arXiv FAQ: https://info.arxiv.org/help/faq/
- LaTeX Community: https://latex.org/forum/

### Testing in Overleaf

Overleaf can approximate arXiv's environment:

1. Set compiler to "TeX Live 2025" (or current arXiv version)
2. Set error mode to "Stop on first error"
3. Include `.bbl` file in project
4. Test compilation

**Note**: Overleaf may have newer packages than arXiv. Always verify on arXiv.

---

## Additional Resources

### Official arXiv Documentation

- **Submission Overview**: https://info.arxiv.org/help/submit/index.html
- **TeX/LaTeX Submission**: https://info.arxiv.org/help/submit_tex.html
- **Common Mistakes**: https://arxiv.org/faq/mistakes.html
- **HTML Best Practices**: https://info.arxiv.org/help/submit_latex_best_practices.html
- **Metadata Guidelines**: https://info.arxiv.org/help/prep.html

### LaTeX Resources

- **LaTeX Project**: https://www.latex-project.org/
- **CTAN**: https://www.ctan.org/ (package documentation)
- **LaTeXML**: https://dlmf.nist.gov/LaTeXML/ (HTML converter)
- **Overleaf Tutorials**: https://www.overleaf.com/learn

### Category Information

- **Category Taxonomy**: https://arxiv.org/category_taxonomy
- **Subject Classifications**: Check specific categories for MSC/ACM codes

---

## Quick Reference Checklist

### Pre-Submission Checklist

- [ ] Paper compiles cleanly locally (no errors)
- [ ] All figures in one format (.eps OR .pdf/.jpg/.png)
- [ ] `.bbl` file included (matches main `.tex` filename)
- [ ] All custom `.sty`/`.cls` files included
- [ ] Figure filenames use only allowed characters
- [ ] Case sensitivity checked in `\includegraphics` commands
- [ ] Relative paths only (no absolute paths)
- [ ] Metadata prepared (title, authors, abstract, comments)
- [ ] License selected
- [ ] Category selected (primary and cross-lists)

### During Submission Checklist

- [ ] All necessary files uploaded
- [ ] AutoTeX detects correct main file
- [ ] Compilation log shows no errors
- [ ] Preview PDF looks correct
- [ ] Metadata accurate
- [ ] Comments field filled in (page count, etc.)

### Post-Submission Checklist

- [ ] HTML version renders correctly (check after announcement)
- [ ] Abstract appears correctly in listings
- [ ] Figures display properly
- [ ] Links work correctly
- [ ] Author names and affiliations correct

---

## Example: Complete arXiv Submission

### Minimal Working Example

```latex
\documentclass[11pt]{article}

% Essential packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{hyperref}

% Title and authors
\title{A Novel Approach to Quantum Computing}

\author{
  Alice Researcher \\
  Department of Physics \\
  Example University \\
  \texttt{alice@example.edu}
  \and
  Bob Scientist \\
  Quantum Research Institute \\
  \texttt{bob@qri.org}
}

\date{February 2026}

\begin{document}

\maketitle

\begin{abstract}
We present a groundbreaking method for quantum state preparation 
that reduces decoherence time by $50\%$. Our approach combines 
topological protection with machine learning optimization, 
achieving state fidelities exceeding $99.9\%$ on current 
quantum hardware. We demonstrate applications to quantum 
simulation and cryptography.
\end{abstract}

\section{Introduction}

Quantum computing promises exponential speedups for certain 
computational problems...

\section{Methods}

Our approach consists of three key innovations...

\subsection{Topological Protection}

We leverage topological codes to protect against...

\section{Results}

Figure~\ref{fig:results} shows the improvement...

\begin{figure}[htbp]
  \centering
  \includegraphics[
    width=0.8\linewidth,
    alt={Bar chart comparing our method to baseline, showing 50 percent improvement}
  ]{results.pdf}
  \caption{Comparison of fidelity across different methods.}
  \label{fig:results}
\end{figure}

\section{Conclusion}

We have demonstrated a practical approach to...

\section*{Acknowledgments}

We thank John Doe for helpful discussions. This work was 
supported by NSF Grant No. 12345.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

### Files to Submit

```
paper.tex          (main LaTeX file)
paper.bbl          (compiled bibliography - CRITICAL!)
results.pdf        (figure file)
references.bib     (optional, for completeness)
```

**Submit as**: Either upload individually or as `submission.tar.gz`

### Metadata to Provide

```
Title: A Novel Approach to Quantum Computing

Authors: Alice Researcher (Example University), Bob Scientist (Quantum Research Institute)

Abstract: We present a groundbreaking method for quantum state 
preparation that reduces decoherence time by 50%. Our approach 
combines topological protection with machine learning optimization, 
achieving state fidelities exceeding 99.9% on current quantum hardware.

Comments: 10 pages, 3 figures

Primary Category: quant-ph
Secondary Categories: cs.LG, cond-mat.mes-hall

License: CC BY 4.0
```

---

## Final Notes

arXiv's flexible approach allows authors to focus on content over formatting, while automated processing ensures long-term accessibility and discoverability. By following these guidelines, you'll ensure smooth submission processing and optimal presentation across PDF, HTML, and future formats.

**Key Philosophy**: Write clean, semantic LaTeX → Include all necessary files → Let arXiv handle the rest.

**For latest information**: Always check https://info.arxiv.org/help/ for current submission guidelines and system updates.

**Good luck with your submission!**

---

Last Updated: February 2026  
Document Version: 1.0  
Based on: TeX Live 2025, arXiv submission system v1.5
