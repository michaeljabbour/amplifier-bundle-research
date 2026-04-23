# ACM LaTeX Style Guide (acmart Class)

## Overview

The `acmart.cls` class is the official ACM primary article template for LaTeX, consolidating 8 individual ACM journal and proceedings templates into a single, unified class. It provides support for various ACM venues including SIGCHI, SIGGRAPH, and other conference series.

**Current Version:** Latest version available on CTAN
**Maintainer:** Boris Veytsman
**Repository:** GitHub - borisveytsman/acmart

## acmart.cls Usage and Options

### Basic Document Structure

```latex
\documentclass[OPTION]{acmart}
```

### Class Options

#### Submission Format Options
- **`manuscript`**: Use for submission versions for review. This is the recommended format when preparing papers for initial submission.
  ```latex
  \documentclass[manuscript]{acmart}
  ```
- **`review`**: Alternative review format option
- **`final`**: Use for final camera-ready versions after acceptance

#### Venue/Conference Options
Specify the target venue to apply appropriate formatting rules:

- **`sigconf`**: ACM Conference Proceedings format (default two-column)
  ```latex
  \documentclass[sigconf]{acmart}
  ```
- **`sigplan`**: SIGPLAN conference proceedings
- **`sigchi`**: SIGCHI conference proceedings (also supports `chi`)
- **`siggraph`**: SIGGRAPH conference proceedings
- **`sigmod`**: SIGMOD/PODS conference proceedings
- **`sigsoft`**: SIGSOFT conference proceedings
- **`sigdb`**: SIGDB conference proceedings
- **`sigapp`**: SIGAPP conference proceedings
- **`sigarch`**: SIGARCH conference proceedings
- **`sigops`**: SIGOPS conference proceedings
- **`sigspatial`**: SIGSPATIAL conference proceedings
- **`tsp`**: Transactions format (for journals)
- **`acmlarge`**: Large format for journals
- **`acmsmall`**: Small format for journals

#### Column Layout Options
- **`twocolumn`**: Two-column layout (default for conference formats)
  ```latex
  \documentclass[sigconf,twocolumn]{acmart}
  ```
- **`singlecolumn`**: Single-column layout (useful for manuscript/review mode)
  ```latex
  \documentclass[manuscript,singlecolumn]{acmart}
  ```
- **`onecolumn`**: Alias for single-column layout

#### Additional Formatting Options
- **`anonymous`**: For blind review, removes author/affiliation information
- **`authorversion`**: Includes version control information
- **`nonacm`**: For non-ACM venues using the template
- **`natbib`**: Use natbib for bibliography management
- **`balance`**: Balance columns on final page

### Complete Example Configurations

**For Conference Submission (Manuscript Mode):**
```latex
\documentclass[manuscript,singlecolumn,sigconf]{acmart}
```

**For SIGCHI Submission:**
```latex
\documentclass[manuscript,singlecolumn,sigchi]{acmart}
```

**For Camera-Ready Conference Paper:**
```latex
\documentclass[sigconf,twocolumn]{acmart}
```

**For Blind Review:**
```latex
\documentclass[manuscript,singlecolumn,sigconf,anonymous]{acmart}
```

## Single vs. Two-Column Modes

### Two-Column Mode (Default)
- **Usage Context**: Final camera-ready copy, published conference proceedings
- **Characteristics**:
  - Default for all venue-specific options (sigconf, sigchi, etc.)
  - Professionally formatted for publication
  - More compact presentation
- **When to Use**:
  - Final camera-ready papers for accepted submissions
  - When publishing in conference proceedings

```latex
% Two-column format
\documentclass[sigconf,twocolumn]{acmart}
```

### Single-Column Mode
- **Usage Context**: Submission for review, manuscript preparation
- **Characteristics**:
  - Easier to read and edit during review process
  - Better for providing comments and feedback
  - Larger margins for reviewer annotations
  - Recommended by ACM for manuscript submissions
- **When to Use**:
  - Initial paper submissions for review
  - Manuscript-stage documents
  - During writing and editing phases

```latex
% Single-column format for manuscript/review
\documentclass[manuscript,singlecolumn]{acmart}
```

## TAPS Workflow Requirements

TAPS (ACM Typesetting and Production System) is the official ACM system for processing papers. Understanding the workflow is essential for successful submission and publication.

### TAPS Preparation Guidelines

1. **Use `manuscript` Option**: Always use `\documentclass[manuscript]{acmart}` for submission through TAPS
   ```latex
   \documentclass[manuscript,singlecolumn]{acmart}
   ```

2. **Required Metadata**: Include complete metadata in your document preamble:
   ```latex
   \title{Your Paper Title}
   \author{Author Name}
   \affiliation{%
     \institution{Your Institution}
     \country{Country}
   }
   \email{author@institution.edu}
   ```

3. **Proper Figure and Table Formatting**:
   - Figure captions must be entered **after** the figure body
   - Table captions must be entered **before** the table body
   - All figures must be within `figure` environment with actual image content
   - Tables should NOT be nested within `figure` environments

   ```latex
   % Correct figure format
   \begin{figure}
     \includegraphics[width=\columnwidth]{image.pdf}
     \caption{Figure caption goes here.}
   \end{figure}

   % Correct table format
   \begin{table}
     \caption{Table caption goes here.}
     \begin{tabular}{...}
       % table content
     \end{tabular}
   \end{table}
   ```

4. **Bibliography Format**:
   - Use BibTeX or biblatex for bibliography management
   - Ensure all citations are properly formatted
   - Follow ACM reference style guidelines

5. **Document Compilation**:
   - Compile with `pdflatex`, `xelatex`, or `lualatex`
   - Run bibliography tool (BibTeX) after initial compilation
   - Recompile document to resolve all references

### TAPS Workflow Stages

1. **Submission Stage**: Author submits PDF and source files through conference/journal portal
2. **Automated Checks**: TAPS performs validation checks on LaTeX source
3. **Review Stage**: Paper undergoes peer review
4. **Acceptance & Copyediting**: Accepted papers go through copyediting
5. **Final Processing**: TAPS generates final formatted versions (PDF for publication, HTML for online)
6. **Publication**: Paper published in proceedings or journal

### TAPS Validation Requirements

Ensure your document passes TAPS validation:
- All required metadata fields are present
- Proper LaTeX class and options used
- Bibliography entries are valid
- All referenced figures and tables exist
- No undefined references or citations
- No overfull/underfull boxes producing warnings

## Accessibility Guidelines

ACM is committed to publishing accessible content. Authors should follow these guidelines:

### Document Structure
- Use proper heading hierarchy: `\section`, `\subsection`, `\subsubsection`
- Use descriptive section titles
- Avoid empty headings or using fonts for structural purposes

### Figures and Images
- **Alt Text**: Provide descriptive captions for all figures
  ```latex
  \begin{figure}
    \includegraphics{figure.pdf}
    \caption{Descriptive caption that conveys the figure's meaning.}
  \end{figure}
  ```
- Use clear, high-contrast colors
- Ensure figures are readable when printed in grayscale
- Label axes and data elements clearly

### Tables
- Use proper table structure with clear headers
- Provide table captions that describe content
- Avoid complex nested tables
- Use simple formatting without color-only distinctions

```latex
\begin{table}
  \caption{Descriptive table caption.}
  \label{tab:example}
  \begin{tabular}{|l|r|}
    \hline
    Header 1 & Header 2 \\
    \hline
    Data 1 & Data 2 \\
    \hline
  \end{tabular}
\end{table}
```

### Mathematical Content
- Use proper LaTeX math mode for equations
- Provide alt text for complex mathematical expressions
- Ensure equations are properly numbered and referenced
- Use `equation` environment with `\label` for referenceable equations

```latex
\begin{equation}\label{eq:example}
  E = mc^2
\end{equation}
```

### Color and Contrast
- Avoid relying solely on color to convey information
- Use hatching, patterns, or different line styles in figures
- Ensure sufficient contrast between text and background (minimum 4.5:1 for body text)
- Test documents in grayscale to verify readability

### Citations and References
- Use meaningful citation text
- Avoid "click here" or "see reference" without context
- Provide complete reference information
- Use hyperref package for clickable references

```latex
% Good: Descriptive citation
Smith et al.~\cite{smith2020} demonstrated that...

% Avoid: Non-descriptive citation
See~\cite{smith2020} for more information.
```

### Links and URLs
- Use `\href{}{}` for hyperlinks with descriptive text
- Avoid bare URLs without context
- Ensure links are distinguishable (underlined, colored, etc.)

```latex
\href{https://www.acm.org}{ACM Website}  % Good
https://www.acm.org                       % Avoid
```

## Title Formatting Guidelines

### Title Length and Format
- **Rule of Thumb**: If title exceeds single column width, it should be shortened
- Avoid redundant terms and abbreviations where possible
- Use standard capitalization (title case or sentence case consistently)

### Long Title Handling
Use the optional `ShortTitle` parameter for papers with lengthy titles:

```latex
\title[Short Title]{This is a Much Longer Title That Might Be Difficult to Fit in a Single Column}

% or

\title{This is a Much Longer Title}
\subtitle{With Additional Context}
```

## Author Information Formatting

### Name and Affiliation Format
- Use consistent name formatting throughout the document, bibliography, and all submissions
- Choose one consistent format and apply it everywhere:
  - Lawrence P. Leipuner (Full Name + Initial)
  - L.P. Leipuner (Initial.Initial. Surname)
  - Gordon K.M. Tobin (Full Name + Multiple Initials)
  - G.K.M. Tobin (Multiple Initials + Surname)

### Author Metadata Structure
```latex
\author{First Author Name}
\affiliation{%
  \institution{University Name}
  \streetaddress{Street Address}
  \city{City}
  \state{State}
  \country{Country}
  \postcode{Postcode}
}
\email{author1@university.edu}

\author{Second Author Name}
\affiliation{%
  \institution{Company Name}
  \country{Country}
}
\email{author2@company.com}
```

## Spacing and Vertical Layout

### vspace Command Usage
- **ACM Guidance**: "Do not abuse this command"
- **Appropriate Uses**:
  - Adjusting spacing around wrapfigure environments
  - Fine-tuning layout in wraptable environments
  - Minimal spacing corrections in specific cases

- **Inappropriate Uses**:
  - General page layout adjustments
  - Spacing between sections
  - Paragraph spacing
  - Creating space for reviewer comments

```latex
% Good: Using vspace with wrapfigure
\begin{wrapfigure}{r}{0.5\textwidth}
  \centering
  \includegraphics[width=0.45\textwidth]{figure.pdf}
  \caption{Figure caption.}
\end{wrapfigure}
\vspace{-0.5cm}  % Minimal adjustment
Text content...

% Avoid: Using vspace for general spacing
Some text\vspace{2cm}More text  % DO NOT DO THIS
```

## Official Resources and Template Links

### Primary Resources
1. **ACM Publications Proceedings Template**
   - https://www.acm.org/publications/proceedings-template
   - Official ACM template and documentation

2. **ACM LaTeX Best Practices**
   - https://www.acm.org/publications/taps/latex-best-practices
   - Guidelines for LaTeX preparation and TAPS workflow

3. **ACM Author Submissions**
   - https://www.acm.org/publications/authors/submissions
   - General submission guidelines and requirements

### Documentation
4. **acmart Class Documentation (acmguide.pdf)**
   - https://ctan.math.illinois.edu/macros/latex/contrib/acmart/acmguide.pdf
   - Comprehensive guide by Boris Veytsman (PDF)
   - Full technical documentation of class options and commands

5. **GitHub Repository**
   - https://github.com/borisveytsman/acmart
   - Source code, issue tracking, and version history
   - Latest development versions

### Overleaf Templates
6. **ACM Conference Proceedings Template (Overleaf)**
   - https://www.overleaf.com/latex/templates/acm-conference-proceedings-primary-article-template/wbvnghjbzwpc
   - Ready-to-use template in Overleaf online editor
   - Example documents with various options

7. **TAPS LaTeX Article Preparation**
   - https://homes.cs.washington.edu/~spencer/taps/article-latex.html
   - Detailed TAPS workflow and LaTeX preparation guide

### Quick Reference Guides
8. **Quick and Dirty Instructions for acmart Class**
   - https://ipsn.acm.org/2019/HowTo.pdf
   - Quick reference guide for common usage patterns
   - Useful troubleshooting tips

9. **SIGGRAPH Author Instructions**
   - https://www.siggraph.org/preparing-your-content/author-instructions/
   - Venue-specific guidelines for SIGGRAPH submissions
   - Additional formatting requirements for SIGGRAPH papers

## Common acmart Command Reference

### Document Metadata
```latex
\title{Paper Title}
\author{Author Name}
\affiliation{...}
\email{author@email.com}
\date{Month Year}
\abstract{Abstract text...}
\keywords{keyword1, keyword2, keyword3}
```

### Sectioning Commands
```latex
\section{Section Title}
\subsection{Subsection Title}
\subsubsection{Subsubsection Title}
\paragraph{Paragraph Title}
```

### Figure Environment
```latex
\begin{figure}
  \centering
  \includegraphics[width=\columnwidth]{image.pdf}
  \caption{Caption text.}
  \label{fig:label}
\end{figure}
```

### Table Environment
```latex
\begin{table}
  \caption{Caption text.}
  \label{tab:label}
  \begin{tabular}{cc}
    Header 1 & Header 2 \\
    \hline
    Data 1 & Data 2 \\
  \end{tabular}
\end{table}
```

### Bibliography
```latex
\bibliography{references}
% BibTeX entries in references.bib file
```

## Troubleshooting Common Issues

### Overfull/Underfull Boxes
- Use `\emergencystretch` if necessary
- Check for long URLs or citations
- Review figure and table widths

### Missing References
- Ensure all labels match citation keys exactly
- Recompile document after adding new citations
- Run BibTeX between pdflatex runs

### Figure/Table Numbering Issues
- Verify `\caption{}` and `\label{}` are in correct positions
- Recompile document to update cross-references
- Check for duplicate labels

### Compilation Errors
- Verify `\documentclass[...]{acmart}` is first line
- Check for unmatched braces and environment closures
- Ensure all packages are compatible with acmart

## Summary of Recommended Practices

1. **Always use manuscript mode with singlecolumn for submissions**:
   ```latex
   \documentclass[manuscript,singlecolumn,sigconf]{acmart}
   ```

2. **Include complete author and affiliation metadata**

3. **Place figure captions after figures; table captions before tables**

4. **Use consistent name formatting throughout**

5. **Follow TAPS validation requirements**

6. **Implement accessibility guidelines from the start**

7. **Consult official ACM resources for venue-specific requirements**

8. **Test document compilation before final submission**

9. **Avoid excessive use of spacing commands**

10. **Use `\label` and `\ref` for all cross-references**

---

**Last Updated:** February 2026
**Source:** ACM Official Documentation and GitHub Repository
**For Latest Information:** Visit https://www.acm.org/publications/proceedings-template
