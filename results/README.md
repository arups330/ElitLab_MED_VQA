# Recorded results

`recorded/` contains selected report text extracted from the four main saved evaluation notebooks. No new training or inference was performed. The notebook outputs are the source of these reports, including their historical limitations and possible configuration mismatches.

Regenerate with:

```bash
python scripts/extract_reports.py
```

Embedded tables, figures, and other MIME outputs remain inside their `.ipynb` files. The text export does not replace those notebook outputs. See [experiment caveats](../docs/experiments.md) before interpreting the reports.
