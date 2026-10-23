# Results

- `recorded/` contains selected text reports extracted from the original immutable Git snapshot. These files remain historical even when working notebooks are updated.
- `dataset_audit.json` contains aggregate local CSV checks against the original metadata archive, with no source records or images.
- `latest/`, when generated, contains selected reports from current working notebook outputs.

```bash
python scripts/extract_reports.py           # fixed original reports
python scripts/extract_reports.py --working # latest working reports
```

Neither command runs inference or recomputes scores. Embedded tables and figures remain in the notebooks. [Workflow distinctions](../docs/workflows.md) and [experiment caveats](../docs/experiments.md) apply when interpreting scores.
