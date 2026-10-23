# Contributing

## Scope

This is a notebook-based research repository. Prefer small changes with a clear experiment or documentation purpose. Do not replace saved experiments with an untested generic training framework.

## Development workflow

```bash
git switch -c experiment/describe-your-change
python scripts/validate_repository.py
```

No ML dependencies are needed for repository checks. GPU training and inference happen in the notebook's documented Kaggle/Colab environment.

## Notebook conventions

- Use lowercase, descriptive filenames under `notebooks/reasoning`, `notebooks/training`, or `notebooks/evaluation`.
- Treat the 31 migrated notebooks as frozen historical snapshots. Create a new notebook for new runs instead of silently overwriting saved evidence.
- Keep code, execution counts, outputs, and configuration together. Save complete final runs and mark partial or smoke-test runs explicitly.
- Record dataset, model revisions, package versions, prompts, seeds, GPU, metrics, and known failures.
- Save only shareable artifacts. Store tokens in the platform's secret manager. Exclude private datasets and model weights.
- New notebooks must be JSON notebook format 4 and pass the integrity check. The migration manifest covers historical notebooks; it is not a list of every future experiment.

## Reports

`python scripts/extract_reports.py` regenerates selected text reports from saved evaluation outputs. The script does not run inference or compute new scores. If results change in a new run, give the report and notebook a distinct version and document the source.

## Pull requests

Describe the problem, final change, and checks performed. Distinguish static validation from actual GPU runs. Do not claim improved performance without controlled measurements. Follow the data and model terms described in [data and licensing](docs/data_and_licensing.md).
