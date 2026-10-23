# Code-level workflow trace

## Shared data preparation

The local original archive has `slake_metadata_train.csv`, `slake_metadata_validation.csv`, `slake_metadata_test.csv`, and `imgs.zip`. The three selected CT subsets match the English metadata grouped by `location`, `modality`, original split, and `answer_type`. Exported records include image identifiers, questions, answers, language, and question type. See [dataset preparation](dataset_preparation.md) for the audit and counts. The splitter source itself was not found; these are verified artifact properties, not a claim to have recovered its exact implementation.

## Pipeline A: reasoning generator, then base-model conditioning

| Stage | Code evidence | Meaning |
|---|---|---|
| Initial training CoT | [Abdomen closed](../notebooks/reasoning/generate_abdomen_train_closed.ipynb), [Abdomen open](../notebooks/reasoning/generate_abdomen_train_open.ipynb) | `FastVisionModel.from_pretrained` selects base Llama. `generate_cot(image, question, answer)` supplies the known answer and writes `CoT`. |
| Reasoning-target fine-tuning | [Abdomen generator](../notebooks/training/reasoning_generators/mixed/abdomen_llama.ipynb), [BrainFace/Neck generator](../notebooks/training/reasoning_generators/mixed/brainface_neck_llama.ipynb) | `convert_to_conversation` uses `sample['CoT']` as assistant target. This trains a reasoning generator, not the short-answer models in Pipeline B. |
| Abdomen test CoT | [Closed](../notebooks/reasoning/generate_abdomen_test_closed.ipynb), [Open](../notebooks/reasoning/generate_abdomen_test_open.ipynb) | Loads `Arup330/Abdomen_CoT_llama_lora`; includes the known answer in the generation prompt and writes `CoT` for test rows. |
| BrainFace test CoT | [BrainFace test generation](../notebooks/reasoning/generate_test_cot.ipynb) | Loads `Arup330/BrainFaceWithNeck_CoT_llama_lora`; the notebook processes test CSVs and writes a test-CoT dataset. |
| Neck saved generator | [Reused Llama notebook](../notebooks/reasoning/generate_cot_llama_vision.ipynb) | Despite a general filename, current code processes Neck test rows using base `unsloth/Llama-3.2-11B-Vision-Instruct`. It does not currently load the fine-tuned Neck adapter. |
| Base-model evaluation | [Closed](../notebooks/evaluation/base_models/closed), [Open](../notebooks/evaluation/base_models/open) | `MODEL_REGISTRY` loaders select base/instruction checkpoints. `cot_text = row['CoT'] if use_cot else ''` toggles test-time reasoning. The target is the medical answer. |

The base-model evaluators include Gemma4-E4B, MedGemma-4B, Qwen2.5-VL-7B, Qwen3-VL-8B, and Llama-11B in the inspected registries. Their “With/Without” labels refer to **test prompt conditioning**, not training variants. Empty/failed CoT filtering and per-model skip behavior can change the effective evaluation scope; inspect saved row and model counts.

### Answer-conditioned test reasoning

The generation templates contain `Ground Truth Answer: {answer}` and explicitly justify that answer. This means a test CoT can encode answer information. A base model receiving that CoT is evaluated with additional answer-conditioned information. Report this condition explicitly; do not present it as a blind benchmark or as directly comparable to Pipeline B's no-test-CoT setting.

## Pipeline B: fine-tuned answer checkpoints

| Stage | Code evidence | Meaning |
|---|---|---|
| With-CoT answer training | [Closed](../notebooks/training/closed), [Open](../notebooks/training/open) | `systemPrompt(question, cot)` receives reasoning, but `convert_to_conversation` sets the assistant target to `sample['answer']`. |
| Without-CoT answer training | Same directories, `without_cot` filenames | Prompt receives question and image, with the medical answer as target. |
| Adapter publication | `HF_USERNAME`, `DATASET_TAG`, `HUB_REPO`, training loop | The notebooks publish dataset/model/condition-specific LoRA artifacts under `Arup330`. Review skip-if-repository-exists logic before a new run. |
| Fine-tuned evaluation | [Closed](../notebooks/evaluation/closed/evaluate_all_models.ipynb), [Open](../notebooks/evaluation/open/evaluate_all_models.ipynb) | `model_repo()` constructs adapter repository names; `FastVisionModel.from_pretrained(repo)` loads the matching adapter/base dependency. The shared `systemPrompt(question)` has no test `CoT` argument. |

This branch compares five families (Lingshu, MedGemma, Qwen2.5-VL, Qwen3-VL, Llama) across three region subsets and two training conditions. Do not call the two branches the same CoT experiment.

## Saved configuration mismatches to review before running

- The notebook named [Abdomen closed with CoT](../notebooks/training/closed/abdomen_with_cot.ipynb) currently has `DATASET_TAG = 'Neck'` and a Neck training path. It is byte-identical in code to the Neck version in the inspected snapshot. Confirm the intended region and checkpoint destination before rerunning. No automatic code correction was made because its saved outputs reflect historical execution.
- The [BrainFace subset evaluator](../notebooks/evaluation/closed/evaluate_brainface_snapshot.ipynb) currently selects Abdomen but retains BrainFace output. The author described changing configuration after the run. Synchronize the configuration before a fresh evaluation.
- The Neck test generator currently selects base Llama, whereas the described intended stage uses a fine-tuned reasoning generator. Confirm the correct adapter before changing it.
- Some filenames describe earlier experiments or reused configurations. Platform metadata and code paths are better evidence than the filename alone. New runs should record exact dataset, checkpoint revision, prompt, environment, and output scope.

## Structural references

The organization borrows clear stage directories, separate examples/documentation, and CPU checks from [TRL](https://github.com/huggingface/trl), [Unsloth notebooks](https://github.com/unslothai/notebooks), and [PyTorch Lightning](https://github.com/Lightning-AI/pytorch-lightning). Their training code and results were not copied into this project.
