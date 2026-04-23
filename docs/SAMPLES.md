# Samples

End-to-end runs of the research bundle's pipeline, preserved as repo
artifacts so you can see what a full `/question` → `/publish` session
actually produces. Each sample includes the session artifacts, the
final PDF, any new capabilities added during the run, and a
reproduction recipe.

## Catalog

| Sample | Recipe | Audience | Output | Status |
|---|---|---|---|---|
| [`whitepaper-dogfood-run`](../examples/whitepaper-dogfood-run/) | `white-paper` | Patent attorneys (Persona A) | 16-page LaTeX white paper on the bundle itself, with four embedded DOT diagrams | First dogfood artifact against the v1.0 milestone |

## Reading a sample

Every sample directory contains numbered artifacts corresponding to the
mode that produced them, plus a `README.md` cataloging what the bundle
exercised and what capabilities were added along the way.

```
examples/<sample-name>/
├── README.md                          overview + capability catalog
├── 01-question.yaml                   /question — sharpened thesis
├── 02-study-plan.yaml                 /study-plan — hash-locked method
├── 03-execute-evidence-log.yaml       /execute — evidence + pivots
├── 04-critique.yaml                   /critique — severity-labeled findings
├── 05-draft.{md,tex}                  /draft — source documents
├── 06-whitepaper*.pdf                 /publish — compiled output
└── figures/                           DOT sources + rendered PDFs/PNGs
```

Open the README first; it names which agents fired in which mode, what
findings the `/critique` pass surfaced, and which publish gates passed.

## Why samples exist

Capability papers are easy to hand-wave about. A sample pins the claim
to a reproducible artifact. If the bundle says it produces a
hash-sealed preregistration, the sample shows the actual YAML with the
actual seal. If the bundle says `/critique` catches overclaiming, the
sample shows the specific findings and where the draft honored them.

The `whitepaper-dogfood-run` sample is the bundle running on itself:
the paper it produced is a capability description *of the bundle*,
written *with the bundle*, for patent attorneys. This is the dogfood
pattern [`docs/HANDOFF.md`](HANDOFF.md) names as the v1.0 milestone.

## Contributing a sample

If you run the bundle on a non-confidential topic and would like the
run captured as a sample:

1. Keep the mode-numbered artifact convention (`01-question.yaml`
   through `06-<output>.pdf`).
2. Write a `README.md` that names agents invoked per mode, findings
   surfaced by `/critique`, and publish-gate status.
3. Include any new diagrams as `figures/*.dot` with compiled `.pdf`
   and `.png` variants.
4. Open a PR adding the directory to `examples/` and a row to the
   catalog table above.

Samples are not sales material. Each one should include an honest
"what this run proved and did not prove" section.
