---
bundle:
  name: research-honest-pivot
  version: 0.2.0
  description: |
    Surfaces any divergence between the hash-locked pre-registration and the
    user's analysis, findings, or draft. Fires at every mode boundary after
    /plan. Default-on; overridable only with explicit --no-honest-pivot flag.
    The single behavior that separates rigorous research from motivated
    reasoning.
---

# Behavior: honest-pivot

**Default:** on
**Overridable:** yes, with visible warning
**Applies to:** all modes after `/plan` has produced a pre-registration

---

## What it does

When the user's analysis, findings, or draft diverges from what was written in the hash-locked pre-registration, the bundle surfaces the divergence explicitly. It does not let the pre-registration be quietly rewritten after results are in.

This is the behavior that separates rigorous research from motivated reasoning. HARKing — hypothesizing after results are known — is the most common way honest analyses become dishonest papers. The `honest-pivot` behavior catches it at every mode boundary after `/plan`.

## Triggers

The behavior fires when any of the following is detected:

1. `/execute` produces results that don't match predictions from the pre-registration, AND the next action tries to modify the pre-registration.
2. `/draft` produces prose that states a different hypothesis than the pre-registered one without labeling it as exploratory.
3. `/critique` finds the draft's Discussion section claims a confirmatory finding that was not pre-registered.
4. `/publish` is invoked on a draft whose findings contradict the pre-registration without an acknowledgment.

## Response

On trigger, the behavior:

1. **Stops the mode transition.** The user sees the divergence explicitly.
2. **Shows the diff.** Pre-registered claim vs. current draft claim, side by side.
3. **Offers three paths:**
   - **Keep the pre-registration, label the new finding exploratory.** Most common path. The draft's Results section gets two clearly separated subsections: Confirmatory and Exploratory.
   - **Update the pre-registration with a timestamped amendment.** For cases where a legitimate methodological correction is needed (e.g., a bug in the analysis script that a reviewer would agree should be fixed). The amendment is hash-locked; the original pre-registration is preserved.
   - **Disable `honest-pivot` for this session.** Requires explicit `--no-honest-pivot` flag. The bundle logs the disable event in the audit trail. The published artifact's metadata records that honest-pivot was disabled.

4. **Never silently accepts the change.** There is no "just continue" path.

## Why "pivot" and not "violation"

Language matters here. Researchers pivot all the time for legitimate reasons — a bug is found, a measurement fails, a better analysis approach becomes apparent. The word *violation* would frame every divergence as misconduct; the word *pivot* correctly frames the situation as "something changed, acknowledge it." The bundle's job is to make the acknowledgment mandatory, not to moralize about the pivot itself.

## Interaction with `exploratory-labeling`

The two behaviors work together. `honest-pivot` catches the moment a divergence happens; `exploratory-labeling` ensures any downstream mention of a non-pre-registered finding carries the `exploratory` tag through to the final output. One without the other is insufficient.

## Example — empirical-paper recipe

```
[ honest-pivot: ON ]

/execute has completed.

PREREGISTRATION SAID:
  Primary prediction: +3pp task-completion on GSM8K at α=0.05

ACTUAL RESULT:
  +1pp on GSM8K, not significant (p=0.22)
  +4pp on AIME, significant (p=0.003)

DIVERGENCE DETECTED:
  Pre-registration did not predict AIME as primary.
  Current draft is emphasizing the AIME result.

OPTIONS:
  [1] Keep preregistration. Report GSM8K as confirmatory (null),
      AIME as exploratory. Discussion section notes the unexpected
      AIME finding and calls for replication.
  [2] Amend preregistration with timestamped note explaining why
      AIME should be promoted to primary. Requires methodologist
      sign-off; the original preregistration is preserved in the
      record.
  [3] Disable honest-pivot for this session (requires --no-honest-pivot
      and will be recorded in the published artifact's metadata).

Your choice:
```

## When this behavior should not fire

- During `/question` and `/plan` — no pre-registration exists yet.
- In `replication-study` recipe, when the divergence is the source paper's vs. the replication's results (that's the whole point of the replication). Behavior recognizes the recipe and adjusts the wording.
- When the user is the reviewer (Persona C) evaluating someone else's document — they're not the one who made the pre-registration, so the enforcement target is wrong.

## Audit trail

Every firing and every user response is logged to:

```
.amplifier/sessions/<session>/honest-pivot-log.yaml
```

This log is included in the `preregistration.yaml` artifact shipped with the final output. Anyone reviewing the published work can see the pivot history, which is part of what makes the rigor claim verifiable.
