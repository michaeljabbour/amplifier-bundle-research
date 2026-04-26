# Experiment Power Awareness

The research bundle includes `tool-experiment-power` — a first-class capability for
statistical power analysis of paired-binary (McNemar) and independent t-test experiments.

## When to use it

Use `experiment_power` / `amplifier-research-power` whenever you need to:

- **Pre-register** a sample size for a replication or held-out validation study.
- Answer "how many items do I need?" before running a paired experiment.
- Compute the **minimum detectable effect** for a completed study (honest reporting).
- Check whether a prior pilot study was adequately powered.
- Build a **sensitivity table** to show how sample size requirements change under
  different assumptions about the discordant rate.

## The four subcommands

| Subcommand | Question answered | Inputs → Output |
|------------|-------------------|-----------------|
| `required-n` | How many paired items do I need? | p_disc, p_help_given_disc, α, power → **n** |
| `mde` | What's the smallest effect detectable at this n? | n, p_disc, α, power → **Δ in pp** |
| `post-hoc` | What power did my study achieve? | n, p_disc, p_help_given_disc, α → **power** |
| `sensitivity` | How robust are my sample-size assumptions? | ranges of p_disc, p_help_given_disc → **table of n's** |

> **Note:** Post-hoc power is generally uninformative on its own (it is a
> deterministic function of the observed p-value). Always pair it with the MDE.

---

## McNemar parameters explained

For a paired binary experiment (e.g., reflection vs. no-reflection on the same items):

- **p_disc** = (help + hurt) / n — the fraction of items with a discordant outcome.
  Estimate this from a pilot study.
- **p_help_given_disc** = help / (help + hurt) — among discordant items, what
  fraction went in the "help" direction?  Must be > 0.5 to have a detectable benefit.
- **Δ** (pp) = p_disc × (2 × p_help_given_disc − 1) × 100 — the net accuracy gain.

### Reflection-tokens scenario

From a prior n = 150 study with 12 help, 6 hurt (18 discordant):

```
p_disc             = 18 / 150 = 0.12
p_help_given_disc  = 12 / 18  ≈ 0.667
Δ                  ≈ 4.0 pp
```

**Pre-registration sample size** (α = 0.05, power = 0.80):

```bash
amplifier-research-power required-n mcnemar \
    --p-disc 0.12 --p-help-given-disc 0.667 \
    --alpha 0.05 --power 0.80
# → Required n (McNemar): 584
```

---

## How to invoke

### CLI

```bash
# Required n
amplifier-research-power required-n mcnemar \
    --p-disc 0.12 --p-help-given-disc 0.667 --alpha 0.05 --power 0.80

# MDE (what can n=150 detect at 80% power?)
amplifier-research-power mde mcnemar \
    --n 150 --p-disc 0.12 --alpha 0.05 --power 0.80

# Post-hoc power (honest reporting)
amplifier-research-power post-hoc mcnemar \
    --n 150 --p-disc 0.12 --p-help-given-disc 0.667

# Sensitivity table over assumption ranges
amplifier-research-power sensitivity mcnemar \
    --p-disc-range 0.10,0.15,0.20 \
    --p-help-given-disc-range 0.55,0.65,0.75 \
    --target-pp 5
```

### Python API

```python
from amplifier_research_power.mcnemar import (
    required_n_mcnemar,
    mde_mcnemar,
    power_mcnemar,
    sensitivity_table,
)

n = required_n_mcnemar(p_disc=0.12, p_help_given_disc=0.667)  # 584
mde = mde_mcnemar(n=150, p_disc=0.12)                          # ≈ 6.5 pp
pwr = power_mcnemar(n=150, p_disc=0.12, p_help_given_disc=0.667)
df = sensitivity_table([0.10, 0.15, 0.20], [0.60, 0.70], target_pp=5)
```

### Amplifier tool protocol

```
experiment_power(operation="required_n", test_type="mcnemar",
                 p_disc=0.12, p_help_given_disc=0.667)
```

---

## Relationship to sibling tools

| Tool | Purpose |
|------|---------|
| `experiment_audit` | Verify experiment data integrity before trusting results |
| `experiment_resume` | Repair aborted runs — plan / subset / merge |
| `experiment_power` | Pre-register sample sizes; compute MDE and post-hoc power |

**Typical pre-registration sequence**:
1. Run `experiment_audit` on the pilot study to verify data integrity.
2. Extract p_disc and p_help_given_disc from pilot results.
3. Run `experiment_power required-n` to determine the required n.
4. Run `experiment_power sensitivity` to show robustness over assumption ranges.
5. Hash-lock the plan with `/plan` before collecting new data.

## Installing the tool

```bash
pip install -e modules/tool-experiment-power/
```
