#!/usr/bin/env python3
"""
LaTeX Format Validation Script

Self-contained module for validating scientific papers against conference format
requirements (NeurIPS, ICML, ACL, IEEE, ACM, arXiv).

Usage:
    python validate_format.py paper.tex
    python validate_format.py paper.tex --format icml
    python validate_format.py paper.tex --strict
    python validate_format.py paper.tex --check-length

Contract:
    Input: LaTeX .tex file path + optional format/flags
    Output: Validation report with warnings/errors
    Side Effects: None (read-only validation)

Dependencies:
    - Python 3.9+ (for Path, typing)
    - Optional: pdfinfo (for PDF page count)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import shutil


class ValidationIssue:
    """Represents a validation warning or error."""

    def __init__(self, severity: str, message: str, line: Optional[int] = None):
        """
        Create validation issue.

        Args:
            severity: 'error' (must fix) or 'warning' (should fix)
            message: Description of the issue
            line: Optional line number where issue occurs
        """
        self.severity = severity
        self.message = message
        self.line = line

    def __str__(self) -> str:
        """Format issue for display."""
        prefix = "❌" if self.severity == "error" else "⚠️"
        location = f" (line {self.line})" if self.line else ""
        return f"{prefix} {self.severity.upper()}{location}: {self.message}"


class FormatValidator:
    """
    Validates LaTeX papers against conference requirements.

    Attributes:
        tex_file: Path to .tex source file
        format: Conference format (neurips, icml, acl, etc.)
        strict: Whether to treat warnings as errors
    """

    # Conference-specific requirements
    FORMAT_SPECS = {
        "neurips": {
            "paper_size": "letterpaper",
            "required_package": "neurips_2024",
            "alt_packages": ["neurips_2023"],
            "page_limit": 9,
            "columns": 1,
            "font_size": 10,
            "auto_reject": ["a4paper"],  # Common mistake
        },
        "icml": {
            "paper_size": "letterpaper",
            "required_class": "icml2024",
            "alt_classes": ["icml2023"],
            "page_limit": 8,
            "columns": 2,
            "font_size": 10,
            "auto_reject": ["a4paper", "Type 3 fonts"],
        },
        "acl": {
            "paper_size": "a4paper",  # CRITICAL
            "required_package": "acl",
            "page_limit_long": 8,
            "page_limit_short": 4,
            "columns": 2,
            "font_size": 11,
            "auto_reject": ["letterpaper", "wrong filename case"],
        },
        "ieee": {
            "paper_size": "letterpaper",
            "required_class": "IEEEtran",
            "page_limit": 8,
            "columns": 2,
            "font_size": 10,
            "auto_reject": ["Type 3 fonts"],
        },
        "acm": {
            "paper_size": "letterpaper",
            "required_class": "acmart",
            "required_options": ["sigconf"],
            "columns": 2,
            "font_size": 9,
            "auto_reject": ["missing CCS concepts"],
        },
        "arxiv": {
            "paper_size": "letterpaper",
            "auto_reject": [
                "non-PDF figures with pdflatex",
                "missing source files",
                "case-sensitive filename mismatches",
            ],
        },
    }

    def __init__(self, tex_file: Path, format: str = "neurips", strict: bool = False):
        """
        Initialize validator.

        Args:
            tex_file: Path to .tex file
            format: Conference format
            strict: Treat warnings as errors

        Raises:
            FileNotFoundError: If tex_file doesn't exist
            ValueError: If format is unknown
        """
        self.tex_file = Path(tex_file)
        if not self.tex_file.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_file}")

        if format not in self.FORMAT_SPECS:
            raise ValueError(
                f"Unknown format: {format}. "
                f"Supported: {', '.join(self.FORMAT_SPECS.keys())}"
            )

        self.format = format
        self.strict = strict
        self.spec = self.FORMAT_SPECS[format]
        self.issues: List[ValidationIssue] = []

        # Read file content
        with open(self.tex_file, "r", encoding="utf-8") as f:
            self.content = f.read()
            self.lines = self.content.splitlines()

    def validate(self) -> bool:
        """
        Run all validation checks.

        Returns:
            True if validation passed, False if errors found
        """
        print(f"🔍 Validating {self.tex_file.name} ({self.format} format)...\n")

        # Run all checks
        self._check_document_class()
        self._check_paper_size()
        self._check_required_packages()
        self._check_font_encoding()
        self._check_citations()
        self._check_figures()
        self._check_auto_reject_issues()

        # Format-specific checks
        if self.format == "acm":
            self._check_ccs_concepts()
        if self.format == "acl":
            self._check_acl_specifics()
        if self.format == "arxiv":
            self._check_arxiv_specifics()

        # Print results
        self._print_issues()

        # Determine pass/fail
        has_errors = any(issue.severity == "error" for issue in self.issues)
        has_warnings = any(issue.severity == "warning" for issue in self.issues)

        if has_errors or (self.strict and has_warnings):
            return False

        return True

    def _check_document_class(self):
        """Validate document class."""
        # Find documentclass declaration
        doc_class_pattern = r"\\documentclass(?:\[([^\]]*)\])?\{([^}]+)\}"
        match = re.search(doc_class_pattern, self.content)

        if not match:
            self.issues.append(
                ValidationIssue("error", "Missing \\documentclass declaration")
            )
            return

        class_name = match.group(2)

        # Check for required class
        if "required_class" in self.spec:
            required = self.spec["required_class"]
            alt_classes = self.spec.get("alt_classes", [])

            if class_name != required and class_name not in alt_classes:
                self.issues.append(
                    ValidationIssue(
                        "error",
                        f"Wrong document class: {class_name} "
                        f"(expected {required} for {self.format})",
                    )
                )

    def _check_paper_size(self):
        """Validate paper size setting."""
        if "paper_size" not in self.spec:
            return

        required_size = self.spec["paper_size"]

        # Check document class options
        doc_class_pattern = r"\\documentclass\[([^\]]*)\]"
        match = re.search(doc_class_pattern, self.content)

        if match:
            options = match.group(1)
            if required_size in options:
                return  # Found correct paper size

        # Check geometry package
        if required_size in self.content:
            return  # Found in content somewhere

        # Missing paper size
        self.issues.append(
            ValidationIssue(
                "error" if required_size == "a4paper" else "warning",
                f"Missing {required_size} specification (required for {self.format})",
            )
        )

        # Special warning for ACL
        if self.format == "acl" and "letterpaper" in self.content:
            self.issues.append(
                ValidationIssue(
                    "error",
                    "⚠️ CRITICAL: ACL requires a4paper, but letterpaper found - AUTO-REJECT",
                )
            )

    def _check_required_packages(self):
        """Check for required style packages."""
        if "required_package" in self.spec:
            required = self.spec["required_package"]
            alt_packages = self.spec.get("alt_packages", [])

            # Check if package is used
            package_pattern = rf"\\usepackage(?:\[[^\]]*\])?\{{{required}\}}"
            if not re.search(package_pattern, self.content):
                # Check alternatives
                found_alt = any(
                    re.search(rf"\\usepackage(?:\[[^\]]*\])?\{{{alt}\}}", self.content)
                    for alt in alt_packages
                )

                if not found_alt:
                    self.issues.append(
                        ValidationIssue(
                            "error",
                            f"Missing \\usepackage{{{required}}} for {self.format}",
                        )
                    )

    def _check_font_encoding(self):
        """Check for proper font encoding (Type 1 fonts)."""
        # Type 3 fonts are a common rejection reason
        type3_patterns = [
            r"\\usepackage\{times\}",  # Old package, creates Type 3
        ]

        for pattern in type3_patterns:
            if re.search(pattern, self.content):
                self.issues.append(
                    ValidationIssue(
                        "warning",
                        "Using deprecated \\usepackage{times} - may create Type 3 fonts. "
                        "Use \\usepackage{newtxtext,newtxmath} instead",
                    )
                )

        # Check for proper font packages
        has_modern_fonts = any(
            pkg in self.content for pkg in ["newtxtext", "mathptmx", "times", "fontenc"]
        )

        if not has_modern_fonts:
            self.issues.append(
                ValidationIssue(
                    "warning",
                    "No explicit font package detected. Consider adding "
                    "\\usepackage{newtxtext,newtxmath} for Type 1 fonts",
                )
            )

    def _check_citations(self):
        """Validate citation setup."""
        has_natbib = "natbib" in self.content
        has_biblatex = "biblatex" in self.content
        has_cite = "\\cite{" in self.content or "\\citep{" in self.content

        if has_cite and not (has_natbib or has_biblatex):
            self.issues.append(
                ValidationIssue(
                    "warning",
                    "Citations found but no citation package (natbib/biblatex) detected",
                )
            )

        # Format-specific citation checks
        if self.format == "acl":
            if not has_natbib:
                self.issues.append(
                    ValidationIssue(
                        "warning",
                        "ACL strongly prefers natbib with author-year citations",
                    )
                )

    def _check_figures(self):
        """Validate figure setup."""
        # Check for figure inclusions
        has_figures = "\\includegraphics" in self.content

        if has_figures:
            # Check for graphicx package
            if "graphicx" not in self.content:
                self.issues.append(
                    ValidationIssue(
                        "error",
                        "\\includegraphics used but \\usepackage{graphicx} missing",
                    )
                )

            # Check figure formats
            if self.format == "arxiv":
                # arXiv requires specific formats for pdflatex
                eps_figures = re.findall(r"\\includegraphics[^}]*\.eps", self.content)
                if eps_figures:
                    self.issues.append(
                        ValidationIssue(
                            "error",
                            f"arXiv with pdflatex requires PDF/PNG/JPG (found .eps): "
                            f"{eps_figures[0]}",
                        )
                    )

    def _check_auto_reject_issues(self):
        """Check for common auto-reject issues."""
        auto_reject = self.spec.get("auto_reject", [])

        for issue in auto_reject:
            if issue == "Type 3 fonts":
                # Already checked in font encoding
                pass
            elif issue in self.content.lower():
                self.issues.append(
                    ValidationIssue(
                        "error",
                        f"⚠️ AUTO-REJECT RISK: Found '{issue}' for {self.format}",
                    )
                )

    def _check_ccs_concepts(self):
        """Check for ACM CCS concepts (required)."""
        if "\\begin{CCSXML}" not in self.content and "\\ccsdesc" not in self.content:
            self.issues.append(
                ValidationIssue(
                    "error",
                    "ACM requires CCS concepts. Generate at "
                    "https://dl.acm.org/ccs/ccs.cfm",
                )
            )

    def _check_acl_specifics(self):
        """ACL-specific validations."""
        # Check for anonymous submission
        if "\\author{" in self.content and "Anonymous" not in self.content:
            self.issues.append(
                ValidationIssue(
                    "warning",
                    "ACL review is double-blind - ensure \\author{Anonymous ACL submission}",
                )
            )

        # Check bibliography style
        if "acl_natbib.bst" not in self.content:
            self.issues.append(
                ValidationIssue(
                    "warning", "ACL requires acl_natbib.bst bibliography style"
                )
            )

    def _check_arxiv_specifics(self):
        """arXiv-specific validations."""
        # Check for .bbl file (required for arXiv)
        bbl_file = self.tex_file.with_suffix(".bbl")
        if "\\bibliography{" in self.content and not bbl_file.exists():
            self.issues.append(
                ValidationIssue(
                    "warning",
                    "arXiv requires pre-compiled .bbl file. Run bibtex first.",
                )
            )

        # Check for absolute paths (not allowed)
        abs_path_pattern = r"\\includegraphics[^}]*/[^}]*\}"
        if re.search(abs_path_pattern, self.content):
            self.issues.append(
                ValidationIssue(
                    "error",
                    "Absolute paths in \\includegraphics not allowed on arXiv",
                )
            )

    def _print_issues(self):
        """Print all validation issues."""
        if not self.issues:
            print("✅ No validation issues found!\n")
            return

        # Group by severity
        errors = [i for i in self.issues if i.severity == "error"]
        warnings = [i for i in self.issues if i.severity == "warning"]

        if errors:
            print(f"❌ Found {len(errors)} error(s):\n")
            for issue in errors:
                print(f"  {issue}")
            print()

        if warnings:
            print(f"⚠️  Found {len(warnings)} warning(s):\n")
            for issue in warnings:
                print(f"  {issue}")
            print()

    def check_pdf_length(self, pdf_file: Path) -> Optional[int]:
        """
        Check PDF page count using pdfinfo.

        Args:
            pdf_file: Path to PDF file

        Returns:
            Number of pages, or None if pdfinfo not available
        """
        if not shutil.which("pdfinfo"):
            return None

        try:
            result = subprocess.run(
                ["pdfinfo", str(pdf_file)], capture_output=True, text=True, timeout=5
            )

            # Extract page count
            for line in result.stdout.splitlines():
                if line.startswith("Pages:"):
                    return int(line.split(":")[1].strip())

        except (subprocess.TimeoutExpired, ValueError, IndexError):
            pass

        return None


def check_length_compliance(tex_file: Path, format: str) -> List[ValidationIssue]:
    """
    Check if paper length complies with conference limits.

    Args:
        tex_file: Path to .tex file
        format: Conference format

    Returns:
        List of validation issues related to length
    """
    issues = []

    # Look for corresponding PDF
    pdf_file = tex_file.with_suffix(".pdf")
    build_pdf = tex_file.parent / "build" / f"{tex_file.stem}.pdf"

    # Try both locations
    if build_pdf.exists():
        pdf_file = build_pdf
    elif not pdf_file.exists():
        issues.append(
            ValidationIssue(
                "warning",
                "PDF not found - cannot check page count. Compile first.",
            )
        )
        return issues

    validator = FormatValidator(tex_file, format)
    page_count = validator.check_pdf_length(pdf_file)

    if page_count is None:
        issues.append(
            ValidationIssue(
                "warning",
                "pdfinfo not available - cannot check page count. "
                "Install with: brew install poppler",
            )
        )
        return issues

    # Check against limits
    spec = validator.spec

    if "page_limit" in spec:
        limit = spec["page_limit"]
        if page_count > limit:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Page count ({page_count}) exceeds {format} limit ({limit} pages)",
                )
            )
        else:
            print(f"✅ Page count: {page_count}/{limit} pages\n")

    elif format == "acl":
        # ACL has two limits
        if page_count > spec["page_limit_long"]:
            issues.append(
                ValidationIssue(
                    "warning",
                    f"Page count ({page_count}) exceeds long paper limit "
                    f"({spec['page_limit_long']} pages)",
                )
            )
        elif page_count > spec["page_limit_short"]:
            print(f"ℹ️ Page count: {page_count} - must be long paper format\n")
        else:
            print(
                f"✅ Page count: {page_count} - qualifies as short paper "
                f"(limit: {spec['page_limit_short']})\n"
            )

    return issues


def main():
    """Command-line interface for format validation."""
    parser = argparse.ArgumentParser(
        description="Validate LaTeX papers against conference format requirements"
    )
    parser.add_argument("tex_file", type=Path, help="Path to .tex file to validate")
    parser.add_argument(
        "-f",
        "--format",
        choices=["neurips", "icml", "acl", "ieee", "acm", "arxiv"],
        default="neurips",
        help="Conference format (default: neurips)",
    )
    parser.add_argument(
        "-s",
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail on any issue)",
    )
    parser.add_argument(
        "--check-length",
        action="store_true",
        help="Check PDF page count against conference limits",
    )

    args = parser.parse_args()

    try:
        # Run format validation
        validator = FormatValidator(args.tex_file, args.format, args.strict)
        passed = validator.validate()

        # Check length if requested
        if args.check_length:
            length_issues = check_length_compliance(args.tex_file, args.format)
            validator.issues.extend(length_issues)

            if length_issues:
                for issue in length_issues:
                    print(f"  {issue}")
                if any(i.severity == "error" for i in length_issues):
                    passed = False

        # Exit code
        if passed:
            print("✅ Validation passed!\n")
            sys.exit(0)
        else:
            print("❌ Validation failed - fix issues above\n")
            sys.exit(1)

    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
