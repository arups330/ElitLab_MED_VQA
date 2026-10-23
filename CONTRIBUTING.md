# Contributing

## Daily research workflow

Working notebooks can be updated in place from their existing Kaggle or Colab connections. Use exact GitHub destination paths and preserve the saved outputs. See [updating notebooks](docs/updating_notebooks.md).

Original runs are retained in the [pinned research snapshot](docs/snapshots.md). CI validates that immutable evidence separately from working files; new results do not need to match old output fingerprints.

## Organization

- Keep Pipeline A (test-CoT conditioning of base models) distinct from Pipeline B (fine-tuned answer-checkpoint comparison).
- Use lowercase descriptive paths and explicit `open`, `closed`, or `mixed` question-type labels.
- Preserve dataset splits; record exact model/adapter revisions, prompts, package versions, GPU, seed, and output scope.
- Mark partial or smoke-test results honestly. Do not claim a benchmark improvement from unrelated checkpoints or conditions.
- Keep tokens in the platform secret manager. Do not upload raw medical data, private material, or model weights without the relevant rights.
- For new notebooks, run `python scripts/update_catalog.py` and commit the resulting launch/catalog updates.

## Checks

```bash
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

Checks use Python's standard library and Git; they do not execute ML notebook cells. GPU experiments run in their documented environments. The [data and licensing guide](docs/data_and_licensing.md) applies to all contributions.
