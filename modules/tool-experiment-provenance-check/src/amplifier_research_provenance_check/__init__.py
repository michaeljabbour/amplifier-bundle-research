"""
amplifier_research_provenance_check — Pre-experiment data provenance checker.

Audits that all data files referenced by an experiment script are git-tracked,
preventing reproducibility gaps like the hle_handcrafted.json gap (commit e189188).

Quick start::

    from amplifier_research_provenance_check.ast_walker import walk_script
    from amplifier_research_provenance_check.git_check import check_files, FileStatus
    from amplifier_research_provenance_check.report import generate_report

    paths = walk_script(open("sweep.py").read())
    results = check_files(paths, repo="/path/to/repo")
    md = generate_report(results, script_path="sweep.py")
"""

from .mount import mount

__version__ = "0.1.0"

__all__ = ["mount", "__version__"]
