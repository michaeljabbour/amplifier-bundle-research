---
mode:
  name: question
  description: "Sharpen a rough claim into a falsifiable, operationalized research question"
  tools:
    safe:
      - read_file
      - glob
      - grep
      - web_search
      - web_fetch
      - delegate
      - recipes
      - load_skill
    warn:
      - bash
  default_action: block
---

# Mode: /question

**Purpose:** Sharpen a rough claim, topic, or intuition into a falsifiable, operationalized question with explicit predictions.

**Entrypoint for:** all recipes except `replication-study` (which starts at `/plan`).

**Default agents:** `hypothesis-designer`, `methodologist` (advisory)

---

## Contract

**Input:** user's opening turn — typically a claim in plain English, a topic area, or a research intuition.

**Output:** a structured `sharpened_question` object (see `agents/hypothesis-designer.md`) plus a natural-language summary the user can confirm.

**Exit condition:** user confirms the sharpened frame matches their intent. Only then does the mode hand off to `/plan`.

## Persona-aware behavior

**Persona A (non-scientist):**
- No jargon. Explanations at one sentence.
- Ask one clarifying question at a time; never a wall of four.
- Frame operationalization as "what specifically would count as success" — not as "operationalization."
- Show the sharpened frame in plain English first; show the structured YAML second, as a "for your records" artifact.

**Persona B (working researcher):**
- Use discipline-appropriate terms.
- Skip the explanatory framing. Go straight to "sharpened frame: yes/no?"
- Invoke `methodologist` advisorily to flag bias risks relevant to the question's domain.

**Persona C (reviewer):**
- `/question` is rarely the entry point. If invoked, it's typically to extract the load-bearing claims *from an incoming document*. Behavior shifts: read the document, list the claims, return the claim frame for user confirmation.

## Failure modes to refuse

- **User wants to skip to `/execute` without sharpening.** Mode politely insists; this is the entire point of the discipline. Users who try to force this see a one-paragraph explanation and the option to bypass with `--no-sharpen` (which gets logged in the audit trail).
- **User's claim is not actually a claim.** ("I want to think about AI." "AI is interesting.") Mode asks what specifically they want to defend or explore, and doesn't proceed until an actual claim surfaces.
- **User's claim is already sharp.** ("Does BH-FDR correction at α=0.05 give us enough power at n=512 for a 3pp shift?") Mode recognizes this and hands off to `/plan` immediately.

## Worked example (Persona A)

```
User:  "I think our AI product saves time."

Mode: That's a claim worth making defensible. Three quick questions
      to sharpen:

      1. Saves time for whom — a specific user type, or everyone?
      2. Saves time compared to what — manual work, a competitor,
         an earlier version?
      3. How would you measure it — minutes saved per task,
         tasks-per-hour, something else?

User:  "Support agents, vs doing the ticket manually, minutes per ticket."

Mode: Good. Sharpened frame:

      "Does our AI product reduce minutes-per-ticket for support
       agents compared to manual handling, on the same ticket
       distribution?"

      I'll flag one thing: this version can be measured head-to-head.
      Your earlier 'saves time' version could be defended by a wide
      range of evidence. This version has a clear success and failure
      condition — which means someone reading it can check.

      Look good, or adjust?

User:  "Look good."

Mode: [hands off to /plan]
```

## Worked example (Persona B)

```
User:  "/question — reflection tokens at trained intervals, GSM8K + AIME,
        paired comparison vs. base decoding."

Mode: Sharpened frame:

      Q: Does inserting reflection tokens at trained intervals during
         generation improve task-completion rate on GSM8K and AIME
         vs. standard decoding, paired by prompt?

      Claim frame:
        - Insertion causes measurable improvement
        - Not explained by output-length increase alone
        - Effect increases with horizon

      Flagged methodology risk (methodologist advisory):
        - "Paired by prompt" — confirm pairing is at the item level,
          not the batch level. At batch level, carryover contamination
          is possible.

      Proceed to /plan? y/n

User:  "y, item-level pairing."

Mode: [hands off to /plan]
```

## Interaction with behaviors

- **`honest-pivot`:** no-op at `/question`. The pivot behavior activates once a pre-registration exists.
- **`exploratory-labeling`:** already in effect — anything the user says is "interesting to explore" gets labeled for the exploratory zone in `/plan`.

## Internal state written

On exit, `/question` writes:

```
.amplifier/sessions/<session>/question-frame.yaml
```

Hash-locked on `/plan` entry.
