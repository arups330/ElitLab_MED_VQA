# Reproducing experiments

## Execution environments

The notebooks are designed around Kaggle and Google Colab, rather than an installable Python package. Run the dependency cells in the notebook you select, then follow its platform-specific data and secret setup. Do not execute every notebook in a single shared environment: older experiments use different dependency versions and installation methods.

The closed CoT training notebooks pin `unsloth==2026.9.2`; some archived notebooks install Transformers from GitHub. The all-model evaluators install Unsloth, and the open evaluator additionally installs `bert-score`, `rouge-score`, `nltk`, and `pillow`. Those cells are preserved; they are not a complete environment lockfile.

Record Python, CUDA, PyTorch, Transformers, Unsloth, PEFT, TRL, and bitsandbytes versions from each actual run. A historical saved output cannot establish that today's dependency resolution reproduces the same result. Repository CI needs only Python 3.11 or newer, without GPU dependencies.

## Inputs

The main evaluators use:

```text
/kaggle/input/datasets/arups330/slackdataset/SLAKE_split_en_realimages/
  Brain_Face/CT/test/closed.csv
  Brain_Face/CT/test/open.csv
  Neck/CT/test/...
  Abdomen/CT/test/...
```

This is the path expected by the code, not a dataset distributed with this repository. Preserve train/test separation. Inspect the image-resolution helper before reorganizing image files: filename normalization and flat versus nested paths vary across data preparation stages.

| Field | Meaning |
|---|---|
| `question` | Medical question associated with the image |
| `answer` | Ground-truth answer; closed training filters to Yes/No |
| `image_file` or `img_name` | Image filename expected by the notebook's loader |
| `CoT` | Supporting reasoning used by relevant CoT training workflows |

Example schema only; replace filenames and text with authorized dataset records:

```csv
image_file,question,answer
example.png,Example question,Yes
```

Main evaluation reads image and question inputs without a `CoT` field. Training notebooks use different roots, including `<region>_train_with_CoT/CT/train`; configure them in the notebook rather than assuming evaluation paths apply to training.

## Credentials and model access

- Configure `HF_TOKEN` in Kaggle Secrets for Kaggle notebooks. Colab notebooks may use their existing login flow or secret lookup.
- Never put token values in committed cells, outputs, `.env` files, or reports.
- The training workflows can push adapters to the Hub. Review `HF_USERNAME`, repository naming, and existing-repository skip behavior before running the training loop.
- Confirm access to the base models referenced by each adapter. A public adapter does not grant access to a gated base model.

Closed checkpoint pattern: `Arup330/{Dataset}_closed_{withCoT|noCoT}_{Model}_lora`.
Open pattern: `Arup330/{Dataset}_open_{CoT|noCoT}_{Model}_lora`.
Subset snapshots contain naming exceptions such as `_V2`; inspect `model_repo()` and `MODEL_REPO_OVERRIDES` instead of inferring the actual revision from a filename.

## Running the all-model evaluators

1. Start a fresh Kaggle GPU session. The closed notebook describes T4 x2 with one model on GPU 0; memory is not automatically pooled across both GPUs.
2. Attach the dataset, enable Internet, attach `HF_TOKEN`, and run the notebook's setup cells.
3. Set `RUN_DATASETS` and `RUN_MODELS` for the intended batch. Select closed or open evaluation independently.
4. Set `MAX_ROWS_PER_DATASET = 1` for a smoke test. Confirm image resolution, repository access, prompt, and output parsing.
5. Restore `MAX_ROWS_PER_DATASET = None` before a full evaluation. Keep image size, prompt, normalization, generation settings, and checkpoint identities consistent across comparisons.
6. Run the remaining cells in order. Inspect failures rather than dropping models or questions to obtain a report.

The final reporting cells may refuse incomplete batches. Use the complete grid for a final all-model report, or record subset reporting separately with the corresponding scope. Never relabel smoke tests as full test results.

## Outputs and resuming

| Evaluation | Runtime output directory |
|---|---|
| Closed questions | `/kaggle/working/cot_eval_results` |
| Open questions | `/kaggle/working/open_eval_results` |

The evaluators save predictions and metadata under `raw_hf_models`; the closed workflow also writes `FINAL_MODEL_SUMMARY.txt`. Inspect each notebook's save cells for its other report filenames. Download the complete output directory before ending the session. Preserve checkpoint identity, generation settings, dataset fingerprint, and error policy with each prediction file.

To resume, attach the previous output directory as a Kaggle input and configure `RESUME_RAW_DIRS`. Only reuse cached predictions when their metadata matches the current experiment. For future runs, record immutable Hub revisions rather than relying only on adapter repository names.

## GPU constraints and debugging

Several training cells contain model-specific workarounds: Qwen3-VL single-device placement and image caps, frozen vision layers for selected models, and MedGemma dtype handling on T4. Read these cells before changing device mapping, precision, or package versions. Do not advertise throughput or memory improvements without measured before/after evidence.

## Saved notebook outputs

Downloading, committing, or moving an `.ipynb` does not require clearing its outputs. All original notebooks are fingerprinted in `notebooks/manifest.json`. Run `python scripts/validate_repository.py` after changes. Do not configure pre-commit hooks or Git filters to strip outputs from historical notebooks.

## One-click launch links

Use [the launch directory](launch.md) for the original-platform button for each notebook (Colab or Kaggle). Existing embedded Colab badges now point to the organized paths. The buttons do not adapt Kaggle-specific data paths or secret helpers for Colab.
