"""
Test configuration — adds src/ to sys.path so tests can import the package
as ``amplifier_research_audit`` without a pip install in CI.
"""

import sys
from pathlib import Path

# Allow: from amplifier_research_audit.checklist import ...
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
