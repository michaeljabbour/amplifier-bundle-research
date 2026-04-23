---
bundle:
  name: research-exploratory-labeling
  version: 0.2.0
  description: |
    Automatically tags any finding, analysis, or claim that was NOT in the
    pre-registration as exploratory. Complements honest-pivot — where
    honest-pivot catches *deviations* from the plan, exploratory-labeling
    catches *additions* beyond the plan. Tags propagate through to the
    published artifact. Default-on for empirical work.
---

# Behavior: exploratory-labeling

**Default:** on
**Overridable:** yes, with `exploratory_label_required: false` in recipe defaults
**Applies to:** `/execute`, `/critique`, `/draft`, `/publish` modes

---

## What it does

Automatically tags any finding, analysis, or claim that was **not specified in the pre-registration** as exploratory. This is the complement to `honest-pivot` — where honest-pivot catches *deviations* from the plan, exploratory-labeling catches *additions* that were never in the plan at all.

## Why it matters

The single most common way otherwise-solid research becomes unsound is failing to distinguish confirmatory findings (planned before seeing data) from exploratory findings (discovered after seeing data). Both are legitimate — but they carry different evidentiary weight, and readers deserve to know which is which.

For non-scientists: this is the difference between "we predicted this would happen and it did" versus "we noticed something interesting while looking." Both are valuable. Only the first one counts as strong evidence.

## Detection logic

The behavior compares every claim in the draft against the locked pre-registration artifact:

1. **Extract claims** from the current draft (assertions, findings, results, recommendations)
2. **Match against pre-registration** predictions, analyses, and hypotheses
3. **Tag unmatched claims** with `[EXPLORATORY]` label

### Matching rules

A claim is **confirmatory** if:
- It directly tests a pre-registered hypothesis
- It uses the pre-registered statistical test
- It reports the pre-registered outcome measure
- All three conditions hold simultaneously

A claim is **exploratory** if ANY of:
- The hypothesis was not pre-registered
- The analysis method differs from pre-registered plan
- The outcome measure was not pre-registered
- The subgroup was not pre-registered
- The comparison was not pre-registered

### Edge cases

- **Pre-registered sensitivity analyses:** confirmatory (they were planned)
- **Robustness checks not in pre-registration:** exploratory
- **Post-hoc corrections applied to pre-registered tests:** confirmatory test, but flag the correction as a deviation via honest-pivot
- **Unplanned secondary analyses:** exploratory, even if they use pre-registered measures on pre-registered data

## Label format

In draft output:

```
[EXPLORATORY] We also observed that processing time decreased by 15%
under high-load conditions (t(47) = 2.31, p = .025, d = 0.67).
This analysis was not pre-registered and should be interpreted
as hypothesis-generating.
```

In structured output (YAML):

```yaml
finding:
  claim: "Processing time decreased by 15% under high-load conditions"
  status: exploratory
  reason: "Subgroup analysis (high-load) not specified in pre-registration"
  statistical_test: "Independent t-test, t(47) = 2.31, p = .025, d = 0.67"
  recommendation: "Include in Results with exploratory label; discuss in Limitations"
```

## Persona-aware presentation

**Persona A (non-scientist):**
> "This finding is interesting but wasn't part of our original plan. That means it's a lead worth investigating further, not a conclusion we can bank on yet. I'll flag it clearly so anyone reading knows the difference."

**Persona B (researcher):**
> "[EXPLORATORY] — not pre-registered. Report in Results with explicit exploratory label. Do not include in Abstract conclusions. Appropriate for Discussion as hypothesis-generating."

**Persona C (reviewer):**
> "This claim appears exploratory (not matched to any pre-registered analysis). Verify whether the authors acknowledge this. If presented as confirmatory, flag as potential HARKing."

## Interaction with other behaviors

- **honest-pivot:** Handles *deviations* from the plan. Exploratory-labeling handles *additions* beyond the plan. They're complementary, not overlapping.
- **When honest-pivot fires first:** If honest-pivot already flagged a deviation and the user chose to proceed, exploratory-labeling picks up the resulting findings and tags them.
- **When no pre-registration exists:** Behavior is inactive. Recipes without `/plan` mode (e.g., some white papers) don't produce pre-registrations, so all findings are implicitly unregistered. The behavior does not tag everything as exploratory — that would be noise, not signal.

## Override

```yaml
# In recipe defaults or user config:
defaults:
  exploratory_label_required: false  # disables auto-tagging
```

When overridden, a visible warning appears:
> "Exploratory labeling is disabled. Findings will not be automatically distinguished from pre-registered predictions. This is appropriate for output types without pre-registration (white papers, position papers) but not recommended for empirical work."

## Failure modes to guard against

1. **Over-labeling:** Don't tag things as exploratory that are reasonable extensions of pre-registered analyses (e.g., computing a CI around a pre-registered effect size)
2. **Under-labeling:** Don't miss subgroup analyses, additional outcome measures, or post-hoc comparisons that weren't pre-registered
3. **Label fatigue:** If >60% of findings are tagged exploratory, surface a warning — the pre-registration may have been too narrow, or the analysis drifted significantly
4. **Performative labeling:** The label must carry consequences — exploratory findings should not appear in the Abstract's conclusions or the Executive Summary's key findings
