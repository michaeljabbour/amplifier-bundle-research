"""
amplifier_research_power — Experiment Power Analysis capability.

Reusable tools for paired-binary (McNemar) and independent t-test power
calculations.  Covers required-n, minimum detectable effect, post-hoc power,
and sensitivity tables.

Quick start::

    from amplifier_research_power.mcnemar import required_n_mcnemar
    n = required_n_mcnemar(p_disc=0.12, p_help_given_disc=0.667)
    print(n)  # required sample size
"""

from .mcnemar import mde_mcnemar, power_mcnemar, required_n_mcnemar, sensitivity_table
from .mount import mount

__version__ = "0.1.0"

__all__ = [
    "required_n_mcnemar",
    "mde_mcnemar",
    "power_mcnemar",
    "sensitivity_table",
    "mount",
]
