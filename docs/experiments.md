# Experiment interpretation and known caveats

## What is being compared

The main evaluators compare dataset-specific fine-tuned checkpoints from five model families under two training conditions. The shared evaluation input is an image and question. For closed questions, the target is Yes/No; open questions use short text answers. CoT is supplied as an additional input in the relevant training notebooks, rather than being an independently generated inference-time reasoning trace in the main evaluation.

## Historical snapshots

| Notebook | How to interpret it |
|---|---|
| [All closed models](../notebooks/evaluation/closed/evaluate_all_models.ipynb) | Main closed evaluation with its original saved outputs |
| [All open models](../notebooks/evaluation/open/evaluate_all_models.ipynb) | Main open evaluation with its original saved outputs |
| [Abdomen subset](../notebooks/evaluation/closed/evaluate_abdomen_snapshot.ipynb) | Later saved subset run; check adapter naming and revisions |
| [BrainFace subset](../notebooks/evaluation/closed/evaluate_brainface_snapshot.ipynb) | Code currently selects Abdomen; saved output includes BrainFace. The author described changing the configuration after the BrainFace run to prepare for Abdomen. Preserve it as a historical snapshot, not a reproducible current BrainFace configuration. |
| [Archived evaluations](../notebooks/archive/evaluation) | Earlier versions; do not pool their scores with newer runs without matching conditions |

Renaming a notebook does not fix a configuration/output mismatch. No saved experiment was rerun as part of repository organization, and no historical score was replaced.

## Limits on conclusions

1. **Training/test input mismatch.** Reasoning available during training is absent in the shared evaluation prompt. Models may depend on the extra input differently.
2. **Reasoning generated with answers.** Some reasoning-generation workflows use ground-truth answers. This can leak answer information into training inputs and does not demonstrate independent reasoning.
3. **Prompt objective.** The research discussion identified a distinction between answering the original medical question and judging whether a reasoning trace is valid. Those are different targets. The latest revised prompt is not necessarily recorded with every saved checkpoint.
4. **Small samples.** Some saved closed evaluations contain only 12 BrainFace questions and 16 Neck questions; Abdomen contains 108 in the inspected run. These are run-specific question counts, not patient counts or general dataset statistics.
5. **Invalid predictions.** Inspect `INVALID_PRED_POLICY` and classification metric functions. A prior review flagged how invalid labels are handled for precision/F1. Runs displaying zero invalid predictions are not affected by that specific issue, but the policy must still be checked for future runs.
6. **Mutable artifacts and caches.** Changing an adapter under an existing repository name can change the experiment without changing the name. Record immutable model revisions and cache metadata.
7. **Open-answer metrics.** Text overlap and embedding similarity do not establish clinical validity. Inspect normalization and reference construction before comparing results.

## Future run record

For a new experiment, save the dataset version and split, image/question counts, model and adapter revision, prompt text, training settings, inference settings, random seed, package versions, GPU type, raw predictions, invalid-answer count, and metric implementation. Keep the notebook configuration synchronized with the outputs when saving the final run.
