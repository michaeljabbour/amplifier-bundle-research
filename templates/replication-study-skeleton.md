# Replication Study Skeleton

## amplifier-bundle-research — /publish output for replication-study recipe

<!-- Structure: IMRAD with replication-specific additions. -->
<!-- Replication work has an extra discipline: every deviation from the -->
<!-- original must be named and justified. The honest-pivot behavior -->
<!-- applies — do not silently change methods to match the original's -->
<!-- results, and do not silently change them to diverge. -->

---

# Replication of %ORIGINAL_TITLE% (%ORIGINAL_AUTHORS%, %ORIGINAL_YEAR%)

**Authors:** %AUTHORS%
**Affiliations:** %AFFILIATIONS%
**Date:** %DATE%
**Pre-registration:** %PREREG_URL% (SHA256: %PREREG_HASH%)

<!-- Title convention: start with "Replication of" or "A Replication of" -->
<!-- so the work is indexable as a replication. Some journals prefer -->
<!-- "Registered Replication Report" for pre-registered multi-lab efforts. -->

---

## Abstract

**Original study replicated:** %ORIGINAL_CITATION%

%ABSTRACT_BODY%

<!-- Structured abstract, ~250 words. Explicit components: -->
<!-- 1. Which study is being replicated (full citation in-body). -->
<!-- 2. The original claim being tested (one sentence). -->
<!-- 3. Replication type: direct / conceptual / close / extension. -->
<!-- 4. Our methods and any intentional deviations. -->
<!-- 5. Our results and comparison to original. -->
<!-- 6. Replication verdict: successful / partial / failed / inconclusive. -->

---

## 1. Introduction

### 1.1 The Original Study

%ORIGINAL_STUDY_SUMMARY%

<!-- Summarize the original study fairly: its question, design, sample, -->
<!-- primary finding, and effect size. Cite primary source, not secondary -->
<!-- coverage. If the original has been cited >100 times, note that — it -->
<!-- raises the stakes of the replication. -->

### 1.2 The Original Claim

%ORIGINAL_CLAIM%

<!-- State the claim being tested in one sentence, quoting the original -->
<!-- where possible. If the original made multiple claims, state which -->
<!-- one(s) this replication targets and why. -->

### 1.3 Why Replicate

%WHY_REPLICATE%

<!-- Possible reasons: the finding anchors a research program, the effect -->
<!-- size has policy implications, methodological concerns have been -->
<!-- raised, the original was underpowered, prior replication attempts -->
<!-- disagreed. State the reason plainly — "to see if it's true" is a -->
<!-- legitimate reason and better than a manufactured narrative. -->

### 1.4 Replication Type

%REPLICATION_TYPE%

<!-- Direct: same materials, same population, same analysis. -->
<!-- Close: same design, different sample or stimulus set. -->
<!-- Conceptual: same hypothesis, different operationalization. -->
<!-- Extension: replicates + tests new boundary condition. -->
<!-- Be honest about which this is. Conceptual replications cannot -->
<!-- adjudicate the original claim directly. -->

---

## 2. Methods

### 2.1 Original Methods (as reported)

%ORIGINAL_METHODS%

<!-- Summarize the original methods as described in the original paper. -->
<!-- Use their terminology. Note any ambiguities — things you had to -->
<!-- interpret because the original was underspecified. -->

### 2.2 Deviations from Original and Rationale

%DEVIATIONS_TABLE%

| # | Original | Our approach | Reason for deviation |
|---|----------|--------------|----------------------|
| 1 | %ORIG_1% | %OURS_1% | %REASON_1% |
| 2 | %ORIG_2% | %OURS_2% | %REASON_2% |

<!-- Every deviation — even small ones — listed with a reason. Common -->
<!-- legitimate reasons: materials unavailable, instrument obsolete, -->
<!-- IRB required a change, original contained an error. Not-legitimate -->
<!-- reasons that should NOT appear: "our results looked better this way". -->

### 2.3 Our Methods

%OUR_METHODS%

<!-- Full IMRAD methods section for our replication. Enough detail for a -->
<!-- third party to replicate us, including code, seeds, instrument -->
<!-- versions, and analysis pipeline. -->

#### 2.3.1 Participants / Sample

%SAMPLE_DETAILS%

#### 2.3.2 Materials

%MATERIALS%

#### 2.3.3 Procedure

%PROCEDURE%

#### 2.3.4 Analysis Plan

%ANALYSIS_PLAN%

<!-- Should match pre-registration exactly. If it diverges, that is an -->
<!-- amendment and must be timestamped — not silently updated. -->

### 2.4 Pre-registration Statement

%PREREG_STATEMENT%

<!-- Pre-registration URL and SHA256 hash. Template text: -->
<!-- "This replication was pre-registered at [URL]. The pre-registration -->
<!-- hash is [SHA256]. The analyses reported in Section 3 follow the -->
<!-- pre-registered plan. Any analyses not in the pre-registration are -->
<!-- labeled [exploratory] throughout." -->

---

## 3. Results

### 3.1 Side-by-Side Comparison with Original

%SIDE_BY_SIDE_TABLE%

| Measure | Original | Replication | Difference | 95% CI | Interpretation |
|---------|----------|-------------|------------|--------|----------------|
| %METRIC_1% | %ORIG_VAL_1% | %OUR_VAL_1% | %DIFF_1% | %CI_1% | %INTERP_1% |
| %METRIC_2% | %ORIG_VAL_2% | %OUR_VAL_2% | %DIFF_2% | %CI_2% | %INTERP_2% |

<!-- Same units, same statistics, same direction. If the original -->
<!-- reported only p-values, compute the effect size and CI from -->
<!-- reported numbers and note the derivation. -->

### 3.2 Confirmatory Results

%CONFIRMATORY_RESULTS%

<!-- Pre-registered analyses first. Report full results — statistic, df, -->
<!-- p, effect size, CI — even when null. -->

### 3.3 Exploratory Results

%EXPLORATORY_RESULTS%

<!-- Any non-pre-registered analysis labeled [exploratory] inline. These -->
<!-- are generative, not confirmatory — do not treat them as evidence -->
<!-- adjudicating the replication question. -->

---

## 4. Replication Analysis

### 4.1 Replication Verdict

%VERDICT%

<!-- One of: -->
<!-- - Successful replication: effect replicated in same direction, -->
<!--   comparable magnitude (within pre-specified bounds). -->
<!-- - Partial replication: some predictions replicated, others did not. -->
<!-- - Failed replication: effect not observed, or observed in opposite -->
<!--   direction, or effect magnitude <25% of original. -->
<!-- - Inconclusive: study underpowered to adjudicate. -->
<!-- State the verdict once, clearly. Do not bury it. -->

### 4.2 Effect Size Comparison

%EFFECT_SIZE_COMPARISON%

<!-- Our effect size vs. the original's, with CIs. If the CIs do not -->
<!-- overlap, the replication statistically disagrees with the original. -->
<!-- If the original's point estimate falls outside our CI, note this. -->

### 4.3 What the Comparison Implies

%COMPARISON_IMPLICATIONS%

<!-- What does this tell us about the phenomenon — not about the -->
<!-- original authors. Avoid personalizing failed replications. -->

---

## 5. Discussion

### 5.1 Implications for the Literature

%LITERATURE_IMPLICATIONS%

<!-- If successful: what this adds to the confidence in the original -->
<!-- claim, and what remaining questions stand. -->
<!-- If failed: what revisions to the literature are warranted — -->
<!-- boundary conditions, moderators, scope limitations. Do not -->
<!-- overclaim from a single replication. -->

### 5.2 Alternative Explanations

%ALTERNATIVES%

<!-- Sample differences, temporal effects, cultural context, stimulus -->
<!-- drift, measurement drift. Take these seriously — they are the -->
<!-- honest reader's first questions. -->

### 5.3 Limitations

%LIMITATIONS%

<!-- Specific limitations of our replication, not generic caveats. -->

### 5.4 Honest-Pivot Section: Deviations and Unexpected Findings

%HONEST_PIVOT%

<!-- Required section for replication work. Covers: -->
<!-- - Any deviation from pre-registration and its timestamped amendment. -->
<!-- - Any unexpected result that changed our interpretation. -->
<!-- - Any analysis we considered and discarded, and why. -->
<!-- This section builds trust by demonstrating we did not silently -->
<!-- optimize toward (or away from) the original's conclusion. -->

### 5.5 Future Work

%FUTURE_WORK%

---

## 6. Conclusion

%CONCLUSION%

<!-- 1-2 paragraphs. State the verdict, the effect size comparison, and -->
<!-- the recommendation to the field. No new arguments. -->

---

## References

%REFERENCES%

<!-- Include the original paper as the first cited reference. Include -->
<!-- any prior replication attempts. -->

---

## Supplementary Materials

### S1. Full Analysis Code

%CODE_AVAILABILITY%

<!-- Link to repository with commit hash, environment specification, -->
<!-- and seeds. Private repos noted with access procedure. -->

### S2. Full Dataset

%DATA_AVAILABILITY%

<!-- Link to data repository with access terms. If data cannot be -->
<!-- shared, explain why and describe an access-controlled alternative. -->

### S3. Pre-registration Document

%PREREG_FULL%

<!-- Either reproduced in full here or linked with hash. -->

### S4. Amendment Log

%AMENDMENT_LOG%

<!-- Timestamped list of any amendments to the pre-registration. -->
<!-- Each amendment has: date, what changed, why, who approved. -->

### S5. Materials

%MATERIALS_APPENDIX%

<!-- Stimuli, survey instruments, task protocols. Either full copies -->
<!-- or license-respecting excerpts. -->

---

## Quality Checklist (removed before submission)

- [ ] Title explicitly marks this as a replication
- [ ] Abstract names the original study and states the verdict
- [ ] Replication type is explicitly declared (direct / close / conceptual / extension)
- [ ] Every deviation from the original is listed with a reason
- [ ] Pre-registration hash is recorded and verified
- [ ] Results reported for all pre-registered analyses, including nulls
- [ ] Exploratory analyses labeled [exploratory] inline
- [ ] Side-by-side comparison table present
- [ ] Replication verdict stated once, clearly, not hedged into meaninglessness
- [ ] Honest-pivot section present and non-empty
- [ ] Code, data, materials, and pre-registration all linked in supplement
- [ ] Amendment log reviewed — no silent changes to pre-registration
