# Updating notebooks from Kaggle or Colab

## Existing working notebooks

You can save new code and outputs to an existing working notebook. CI no longer rejects ordinary changes just because they differ from the first saved run. Original evidence is pinned in [the research snapshot](snapshots.md).

1. Open the existing Kaggle/Colab notebook you normally use, or use its original-platform button in [the launch directory](launch.md).
2. Check the configured region, question type, input paths, adapter revisions, prompt, and output settings.
3. Run the experiment and save the completed notebook with outputs included. Do not clear output cells before exporting.
4. In Kaggle's GitHub connection, select `arups330/ElitLab_MED_VQA`, branch `main`, and the **exact destination path** from the catalog. An old root filename is not automatically redirected after a move.
5. In Colab, use **File → Save a copy in GitHub**, select the same repository/branch, and enter the exact destination path. Include outputs when the save dialog offers that option.
6. Use a descriptive commit message and check the rendered GitHub notebook and Actions result after publishing.

For fine-tuned checkpoint evaluation, the stable working paths are:

```text
notebooks/evaluation/closed/evaluate_all_models.ipynb
notebooks/evaluation/open/evaluate_all_models.ipynb
```

Pipeline A base-model evaluators live under `notebooks/evaluation/base_models/open` or `closed`. Reasoning-generator training lives under `notebooks/training/reasoning_generators/mixed`. Those files were previously mislabeled as archived evaluation/early experiments; use their new paths when reconnecting.

## New experiments

For a new variant or important independent result, save a distinct descriptive notebook in the corresponding stage and open/closed folder. Keep mixed open/closed reasoning-target training under `mixed` instead of pretending it handles a single question type.

Then regenerate the working catalog and launch links:

```bash
python scripts/update_catalog.py
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

For newly added notebooks, infer original platform from Colab/Kaggle metadata; the catalog generator stops on unknown/ambiguous platform metadata instead of guessing. Existing platform assignments remain stable even if an editor modifies unrelated metadata.

## Result reports

Embedded notebook outputs are the primary saved result. `results/recorded` is a fixed export of the original Git snapshot and does not change when working notebooks are rerun.

To export the latest working summary tables separately:

```bash
python scripts/extract_reports.py --working
```

This writes `results/latest`, without recomputing predictions or metrics. Review and commit those exports if useful. It is not necessary for an ordinary notebook push to pass CI.
