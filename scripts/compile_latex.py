#!/usr/bin/env python3
"""
LaTeX Compilation Script for Multiple Conference Formats

Self-contained module for compiling LaTeX papers to PDF with support for
NeurIPS, ICML, ACL, IEEE, ACM, and arXiv formats.

Usage:
    python compile_latex.py paper.tex
    python compile_latex.py paper.tex --format neurips
    python compile_latex.py paper.tex --clean
    python compile_latex.py paper.tex --watch

Contract:
    Input: LaTeX .tex file path + optional format specifier
    Output: Compiled PDF file + compilation log
    Side Effects: Creates auxiliary files (.aux, .log, .bbl, etc.)

Dependencies:
    - latexmk (for robust compilation)
    - pdflatex (LaTeX engine)
    - bibtex or biber (for bibliography)
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple
import shutil


class CompilationError(Exception):
    """Raised when LaTeX compilation fails."""

    pass


class LatexCompiler:
    """
    Handles LaTeX compilation for scientific papers.

    Attributes:
        tex_file: Path to the .tex source file
        output_dir: Directory for build artifacts
        format: Conference format (neurips, icml, acl, ieee, acm, arxiv)
    """

    # Conference-specific compilation settings
    FORMATS = {
        "neurips": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "letterpaper",
        },
        "icml": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "letterpaper",
        },
        "acl": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "a4paper",  # CRITICAL: ACL requires A4
        },
        "ieee": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "letterpaper",
        },
        "acm": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "letterpaper",
        },
        "arxiv": {
            "engine": "pdflatex",
            "bibtex": "bibtex",
            "paper_size": "letterpaper",
        },
    }

    def __init__(
        self, tex_file: Path, format: str = "neurips", output_dir: Optional[Path] = None
    ):
        """
        Initialize LaTeX compiler.

        Args:
            tex_file: Path to .tex file
            format: Conference format (neurips, icml, etc.)
            output_dir: Optional output directory for build artifacts

        Raises:
            FileNotFoundError: If tex_file doesn't exist
            ValueError: If format is unknown
        """
        self.tex_file = Path(tex_file)
        if not self.tex_file.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_file}")

        if format not in self.FORMATS:
            raise ValueError(
                f"Unknown format: {format}. Supported: {', '.join(self.FORMATS.keys())}"
            )

        self.format = format
        self.output_dir = output_dir or self.tex_file.parent / "build"
        self.config = self.FORMATS[format]

    def check_dependencies(self) -> Tuple[bool, list[str]]:
        """
        Check if required compilation tools are available.

        Returns:
            (success, missing_tools) tuple
        """
        required = ["latexmk", "pdflatex", "bibtex"]
        missing = []

        for tool in required:
            if not shutil.which(tool):
                missing.append(tool)

        return len(missing) == 0, missing

    def compile(self, clean_first: bool = False) -> bool:
        """
        Compile LaTeX document to PDF.

        Args:
            clean_first: Remove auxiliary files before compilation

        Returns:
            True if compilation succeeded, False otherwise

        Raises:
            CompilationError: If compilation fails with error details
        """
        print(f"📄 Compiling {self.tex_file.name} ({self.format} format)...")

        # Check dependencies
        success, missing = self.check_dependencies()
        if not success:
            raise CompilationError(
                f"Missing required tools: {', '.join(missing)}\n"
                "Install with: brew install mactex (macOS) or apt install texlive-full (Linux)"
            )

        # Clean if requested
        if clean_first:
            print("🧹 Cleaning auxiliary files...")
            self.clean()

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Compile using latexmk (handles multiple passes automatically)
        cmd = [
            "latexmk",
            "-pdf",  # Use pdflatex
            "-interaction=nonstopmode",  # Don't stop on errors
            "-file-line-error",  # Better error messages
            f"-output-directory={self.output_dir}",
            str(self.tex_file),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Check if latexmk itself failed
            if result.returncode != 0:
                print(f"⚠️ latexmk returned code {result.returncode}")

            # Check for errors in log
            log_file = self.output_dir / f"{self.tex_file.stem}.log"
            if log_file.exists():
                if self._has_critical_errors(log_file):
                    print("❌ Compilation failed with errors")
                    self._print_errors(log_file)
                    return False

            # Verify PDF was created
            pdf_file = self.output_dir / f"{self.tex_file.stem}.pdf"
            if not pdf_file.exists():
                print("❌ PDF not generated")
                return False

            print(f"✅ Successfully compiled to {pdf_file}")
            return True

        except subprocess.TimeoutExpired:
            raise CompilationError("Compilation timed out after 5 minutes")
        except Exception as e:
            raise CompilationError(f"Compilation error: {e}")

    def _has_critical_errors(self, log_file: Path) -> bool:
        """Check if log file contains critical errors."""
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            log_content = f.read()

        # Check for error indicators
        error_patterns = [
            "! LaTeX Error:",
            "! Emergency stop",
            "! Undefined control sequence",
            "! Missing",
        ]

        return any(pattern in log_content for pattern in error_patterns)

    def _print_errors(self, log_file: Path):
        """Extract and print errors from log file."""
        print("\n📋 Compilation Errors:")
        print("-" * 60)

        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        # Find error lines
        for i, line in enumerate(lines):
            if line.startswith("!"):
                # Print error and context
                print(line.rstrip())
                # Print next few lines for context
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].strip():
                        print(lines[j].rstrip())
                    else:
                        break
                print()

        print("-" * 60)
        print(f"Full log: {log_file}")

    def clean(self):
        """Remove auxiliary files from compilation."""
        if not self.output_dir.exists():
            return

        # Extensions to remove
        aux_extensions = [
            ".aux",
            ".log",
            ".bbl",
            ".blg",
            ".out",
            ".toc",
            ".fdb_latexmk",
            ".fls",
            ".synctex.gz",
            ".nav",
            ".snm",
            ".vrb",
            ".lof",
            ".lot",
        ]

        removed = 0
        for ext in aux_extensions:
            for file in self.output_dir.glob(f"*{ext}"):
                file.unlink()
                removed += 1

        print(f"🧹 Removed {removed} auxiliary files")

    def watch(self, interval: int = 2):
        """
        Watch mode: recompile when source file changes.

        Args:
            interval: Check interval in seconds
        """
        print(f"👀 Watching {self.tex_file} for changes...")
        print("Press Ctrl+C to stop")

        last_mtime = self.tex_file.stat().st_mtime

        try:
            while True:
                time.sleep(interval)
                current_mtime = self.tex_file.stat().st_mtime

                if current_mtime > last_mtime:
                    print("\n🔄 Detected change, recompiling...")
                    try:
                        self.compile()
                    except CompilationError as e:
                        print(f"❌ {e}")

                    last_mtime = current_mtime

        except KeyboardInterrupt:
            print("\n✋ Stopped watching")


def validate_format(tex_file: Path, format: str) -> list[str]:
    """
    Validate LaTeX file has required packages for format.

    Args:
        tex_file: Path to .tex file
        format: Conference format

    Returns:
        List of validation warnings (empty if all good)
    """
    warnings = []

    with open(tex_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Format-specific validations
    if format == "neurips":
        if "neurips_2024" not in content and "neurips_2023" not in content:
            warnings.append("Missing \\usepackage{neurips_2024}")

    elif format == "icml":
        if "icml2024" not in content:
            warnings.append("Missing \\documentclass{icml2024}")

    elif format == "acl":
        if "acl" not in content.lower():
            warnings.append("Missing ACL style file (acl.sty or acl_natbib.sty)")
        if "a4paper" not in content:
            warnings.append("⚠️ CRITICAL: ACL requires a4paper (auto-reject if missing)")

    elif format == "ieee":
        if "IEEEtran" not in content:
            warnings.append("Missing \\documentclass{IEEEtran}")

    elif format == "acm":
        if "acmart" not in content:
            warnings.append("Missing \\documentclass{acmart}")

    return warnings


def main():
    """Command-line interface for LaTeX compilation."""
    parser = argparse.ArgumentParser(
        description="Compile LaTeX scientific papers with conference format support"
    )
    parser.add_argument("tex_file", type=Path, help="Path to .tex file to compile")
    parser.add_argument(
        "-f",
        "--format",
        choices=["neurips", "icml", "acl", "ieee", "acm", "arxiv"],
        default="arxiv",
        help="Conference format (default: arxiv)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory for build artifacts (default: ./build)",
    )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="Clean auxiliary files before compilation",
    )
    parser.add_argument(
        "-w", "--watch", action="store_true", help="Watch mode: recompile on changes"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate format, do not compile",
    )

    args = parser.parse_args()

    # Validate format
    warnings = validate_format(args.tex_file, args.format)
    if warnings:
        print("⚠️  Validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()

        if args.validate_only:
            sys.exit(1 if warnings else 0)

    if args.validate_only:
        print("✅ No validation warnings")
        sys.exit(0)

    # Compile
    try:
        compiler = LatexCompiler(
            args.tex_file, format=args.format, output_dir=args.output_dir
        )

        if args.watch:
            compiler.watch()
        else:
            success = compiler.compile(clean_first=args.clean)
            sys.exit(0 if success else 1)

    except CompilationError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✋ Interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()
