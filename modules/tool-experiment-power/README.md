# tool-experiment-power

Statistical power analysis for experiment design.  Sibling to
`tool-experiment-audit` and `tool-experiment-resume` in the
`amplifier-bundle-research` toolkit.

Covers **McNemar paired-binary** tests (the natural model for paired
help/hurt experiments) and **independent t-tests** (Cohen's d based).

---

## Install

```bash
pip install -e modules/tool-experiment-power/
```

## CLI

### `required-n` — How many items do I need?

```bash
amplifier-research-power required-n mcnemar \
    --p-disc 0.12 --p-help-given-disc 0.667 \
    --alpha 0.05 --power 0.80
# Required n (McNemar): 584
```

- `--p-disc`: Probability of a discordant pair = (help + hurt) / n
- `--p-help-given-disc`: P(help | discordant) — must be ≥ 0.5

### `mde` — What's the smallest effect I can detect?

```bash
amplifier-research-power mde mcnemar \
    --n 150 --p-disc 0.12 \
    --alpha 0.05 --power 0.80
```

Given a fixed n, what is the minimum Δ (in pp) detectable at 80% power?

### `post-hoc` — What power did my completed study have?

```bash
amplifier-research-power post-hoc mcnemar \
    --n 150 --p-disc 0.12 --p-help-given-disc 0.667
```

Reports achieved power. Pair with MDE for honest reporting; post-hoc power
alone is generally uninformative.

### `sensitivity` — How robust are my assumptions?

```bash
amplifier-research-power sensitivity mcnemar \
    --p-disc-range 0.10,0.15,0.20 \
    --p-help-given-disc-range 0.55,0.65,0.75 \
    --target-pp 5 --alpha 0.05 --power 0.80
```

Produces a cross-product table of required n's over the assumption ranges.

---

## Python API

```python
from amplifier_research_power.mcnemar import (
    required_n_mcnemar,
    mde_mcnemar,
    power_mcnemar,
    sensitivity_table,
)

# Reflection-tokens scenario: 12 help, 6 hurt, in a prior n=150 study
n = required_n_mcnemar(p_disc=0.12, p_help_given_disc=0.667)
# → 584
```

---

## Math (McNemar)

Let `p_b = P(help only)` and `p_c = P(hurt only)`, so:

- `p_disc = p_b + p_c` (discordant rate)
- `Δ = p_b − p_c = p_disc × (2·p_help_given_disc − 1)` (net accuracy gain)

The Schork-Williams (1980) approximation gives:

```
n = [z_{α/2}·√p_disc  +  z_β·√(p_disc − Δ²)]²  /  Δ²
```

This is derived from the variance of the McNemar test statistic under H₁.

---

## Tests

```bash
pytest modules/tool-experiment-power/tests/ -v
```

23 tests covering: monotonicity, input validation, textbook values,
round-trip MDE consistency, statsmodels agreement, and CLI integration.
