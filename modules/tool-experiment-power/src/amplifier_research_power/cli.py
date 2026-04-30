"""
cli.py — amplifier-research-power command-line interface.

Subcommand structure:
  amplifier-research-power required-n mcnemar  [options]
  amplifier-research-power mde        mcnemar  [options]
  amplifier-research-power post-hoc   mcnemar  [options]
  amplifier-research-power sensitivity mcnemar [options]

Each top-level subcommand dispatches to a test-type sub-subcommand (mcnemar
or ttest).
"""

from __future__ import annotations

import argparse
import sys

# ---------------------------------------------------------------------------
# required-n mcnemar
# ---------------------------------------------------------------------------


def _cmd_required_n_mcnemar(args: argparse.Namespace) -> None:
    from .mcnemar import required_n_mcnemar

    n = required_n_mcnemar(
        p_disc=args.p_disc,
        p_help_given_disc=args.p_help_given_disc,
        alpha=args.alpha,
        power=args.power,
        two_sided=not args.one_sided,
    )
    delta_pp = args.p_disc * (2 * args.p_help_given_disc - 1) * 100
    print(f"Required n (McNemar): {n}")
    print(f"  Implied Δ = {delta_pp:.2f} pp")
    print(f"  α = {args.alpha}, power = {args.power}")


# ---------------------------------------------------------------------------
# mde mcnemar
# ---------------------------------------------------------------------------


def _cmd_mde_mcnemar(args: argparse.Namespace) -> None:
    from .mcnemar import mde_mcnemar

    mde_pp = mde_mcnemar(
        n=args.n,
        p_disc=args.p_disc,
        alpha=args.alpha,
        power=args.power,
        two_sided=not args.one_sided,
    )
    print(f"MDE (McNemar): {mde_pp:.3f} pp  (Δ = {mde_pp / 100:.5f})")
    print(f"  n = {args.n}, p_disc = {args.p_disc}")
    print(f"  α = {args.alpha}, target power = {args.power}")


# ---------------------------------------------------------------------------
# post-hoc mcnemar
# ---------------------------------------------------------------------------


def _cmd_post_hoc_mcnemar(args: argparse.Namespace) -> None:
    from .mcnemar import power_mcnemar

    pwr = power_mcnemar(
        n=args.n,
        p_disc=args.p_disc,
        p_help_given_disc=args.p_help_given_disc,
        alpha=args.alpha,
        two_sided=not args.one_sided,
    )
    delta_pp = args.p_disc * (2 * args.p_help_given_disc - 1) * 100
    print(f"Achieved power (McNemar): {pwr:.4f}")
    print(f"  n = {args.n}, Δ = {delta_pp:.2f} pp")
    print("  Note: post-hoc power is often uninformative — pair with MDE for honest reporting.")


# ---------------------------------------------------------------------------
# sensitivity mcnemar
# ---------------------------------------------------------------------------


def _cmd_sensitivity_mcnemar(args: argparse.Namespace) -> None:
    from .mcnemar import sensitivity_table

    p_disc_range = [float(x) for x in args.p_disc_range.split(",")]
    p_hgd_range = [float(x) for x in args.p_help_given_disc_range.split(",")]

    df = sensitivity_table(
        p_disc_range=p_disc_range,
        p_help_given_disc_range=p_hgd_range,
        target_pp=args.target_pp,
        alpha=args.alpha,
        power=args.power,
    )
    print(df.to_string(index=False))


# ---------------------------------------------------------------------------
# Parser builders
# ---------------------------------------------------------------------------


def _add_alpha_power(p: argparse.ArgumentParser) -> None:
    p.add_argument("--alpha", type=float, default=0.05, help="Type-I error rate (default: 0.05)")
    p.add_argument("--power", type=float, default=0.80, help="Target power (default: 0.80)")
    p.add_argument(
        "--one-sided", action="store_true", help="Use one-sided test (default: two-sided)"
    )




# ---------------------------------------------------------------------------
# calibration (v0.8.1)
# ---------------------------------------------------------------------------


def _cmd_calibration(args: argparse.Namespace) -> None:
    """Compute ECE, Brier score, reliability bins from a JSONL records file
    of {item_id, confidence, correct}.
    """
    import json
    from .calibration import calibration_report, calibration_report_to_dict

    confidences: list[float] = []
    corrects: list[int] = []
    with open(args.records) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if "confidence" not in rec or "correct" not in rec:
                continue
            confidences.append(float(rec["confidence"]))
            corrects.append(int(bool(rec["correct"])))

    if not confidences:
        print("ERROR: no records with both `confidence` and `correct` fields", file=sys.stderr)
        raise SystemExit(2)

    rep = calibration_report(confidences, corrects, n_bins=args.bins)
    d = calibration_report_to_dict(rep)
    if args.output:
        with open(args.output, "w") as f:
            json.dump(d, f, indent=2)
        print(f"Wrote calibration report to {args.output}")
    print(f"n            = {rep.n}")
    print(f"n_bins       = {rep.n_bins}")
    print(f"ECE          = {rep.ece:.4f}")
    print(f"Brier        = {rep.brier:.4f}")
    print()
    print("Reliability bins:")
    print(f"  {'bin':>3}  {'lo':>5} {'hi':>5}  {'n':>4}  {'conf':>6} {'acc':>6} {'gap':>6}")
    for b in rep.bins:
        if b.n == 0:
            print(f"  {b.bin_index:>3}  {b.lo:>5.2f} {b.hi:>5.2f}  {0:>4}  {'-':>6} {'-':>6} {'-':>6}")
        else:
            print(f"  {b.bin_index:>3}  {b.lo:>5.2f} {b.hi:>5.2f}  {b.n:>4}  {b.mean_confidence:>6.3f} {b.mean_accuracy:>6.3f} {b.gap:>6.3f}")


def _build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="amplifier-research-power",
        description=(
            "Statistical power analysis for paired-binary (McNemar) and "
            "independent t-test experiments."
        ),
    )
    root.set_defaults(func=None)
    sub1 = root.add_subparsers(dest="command", metavar="SUBCOMMAND")

    # --- required-n ---
    rn = sub1.add_parser("required-n", help="Compute required sample size")
    rn_sub = rn.add_subparsers(dest="test_type", metavar="TEST_TYPE")

    rn_mcnemar = rn_sub.add_parser("mcnemar", help="McNemar paired binary test")
    rn_mcnemar.add_argument(
        "--p-disc",
        type=float,
        required=True,
        help="Probability of a discordant pair (0 < p_disc < 1)",
    )
    rn_mcnemar.add_argument(
        "--p-help-given-disc", type=float, required=True, help="P(help | discordant) in [0.5, 1.0]"
    )
    _add_alpha_power(rn_mcnemar)
    rn_mcnemar.set_defaults(func=_cmd_required_n_mcnemar)

    # --- mde ---
    mde = sub1.add_parser("mde", help="Compute minimum detectable effect")
    mde_sub = mde.add_subparsers(dest="test_type", metavar="TEST_TYPE")

    mde_mcnemar = mde_sub.add_parser("mcnemar", help="McNemar paired binary test")
    mde_mcnemar.add_argument("--n", type=int, required=True, help="Sample size")
    mde_mcnemar.add_argument(
        "--p-disc", type=float, required=True, help="Probability of a discordant pair"
    )
    _add_alpha_power(mde_mcnemar)
    mde_mcnemar.set_defaults(func=_cmd_mde_mcnemar)

    # --- post-hoc ---
    ph = sub1.add_parser("post-hoc", help="Compute achieved (post-hoc) power")
    ph_sub = ph.add_subparsers(dest="test_type", metavar="TEST_TYPE")

    ph_mcnemar = ph_sub.add_parser("mcnemar", help="McNemar paired binary test")
    ph_mcnemar.add_argument("--n", type=int, required=True, help="Sample size")
    ph_mcnemar.add_argument(
        "--p-disc", type=float, required=True, help="Probability of a discordant pair"
    )
    ph_mcnemar.add_argument(
        "--p-help-given-disc", type=float, required=True, help="P(help | discordant)"
    )
    ph_mcnemar.add_argument(
        "--alpha", type=float, default=0.05, help="Type-I error rate (default: 0.05)"
    )
    ph_mcnemar.add_argument("--one-sided", action="store_true", help="Use one-sided test")
    ph_mcnemar.set_defaults(func=_cmd_post_hoc_mcnemar)

    # --- sensitivity ---
    sens = sub1.add_parser("sensitivity", help="Sensitivity table of required n's")
    sens_sub = sens.add_subparsers(dest="test_type", metavar="TEST_TYPE")

    sens_mcnemar = sens_sub.add_parser("mcnemar", help="McNemar paired binary test")
    sens_mcnemar.add_argument(
        "--p-disc-range", required=True, help="Comma-separated p_disc values, e.g. 0.10,0.15,0.20"
    )
    sens_mcnemar.add_argument(
        "--p-help-given-disc-range", required=True, help="Comma-separated p_help_given_disc values"
    )
    sens_mcnemar.add_argument(
        "--target-pp", type=float, default=5.0, help="Reference target effect in pp (default: 5)"
    )
    _add_alpha_power(sens_mcnemar)
    sens_mcnemar.set_defaults(func=_cmd_sensitivity_mcnemar)

    # ---------------- calibration (v0.8.1) ----------------
    cal = sub1.add_parser(
        "calibration",
        help="Compute ECE, Brier score, and reliability bins from JSONL records",
    )
    cal.add_argument(
        "--records", required=True,
        help="Path to JSONL records file (each line: {item_id, confidence, correct})",
    )
    cal.add_argument(
        "--bins", type=int, default=10,
        help="Number of equal-width bins on [0, 1] (default 10)",
    )
    cal.add_argument(
        "--output", default=None,
        help="Optional path to write JSON report (default: stdout summary only)",
    )
    cal.set_defaults(func=_cmd_calibration)

    return root


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point for ``amplifier-research-power`` and
    ``python -m amplifier_research_power.cli``."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        sys.exit(0)

    try:
        args.func(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
