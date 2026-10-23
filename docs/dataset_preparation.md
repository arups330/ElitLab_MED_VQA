# Dataset preparation and verification

## Criteria verified from local artifacts

1. Select `q_lang == 'en'` from the original metadata exports.
2. Group by anatomical `location`; the study focuses on Abdomen, Brain/Face (`Brain_Face`), and Neck.
3. Keep modality separate. The inspected experiment inputs use `CT`; the exported data also contain other regions and modalities.
4. Retain the original metadata assignment to train, validation, or test (`validation` becomes folder `val`). No new random train/test ratio is inferred.
5. Separate `answer_type == 'OPEN'` and `answer_type == 'CLOSED'` into `open.csv` and `closed.csv` within each split.

```text
<dataset-root>/
  Abdomen/CT/{train,val,test}/{open.csv,closed.csv}
  Brain_Face/CT/{train,val,test}/{open.csv,closed.csv}
  Neck/CT/{train,val,test}/{open.csv,closed.csv}
```

This documents verified artifacts. The original split-generation program was not found in the GitHub notebooks or inspected local source files, so its exact image-copying implementation is not claimed to be reproduced here.

## Audited CT question counts

| Region | Train open | Train closed | Validation open | Validation closed | Test open | Test closed | Test closed Yes/No |
|---|---:|---:|---:|---:|---:|---:|---:|
| Abdomen | 694 | 569 | 135 | 112 | 160 | 127 | 108 |
| Brain/Face | 76 | 64 | 20 | 20 | 17 | 12 | 12 |
| Neck | 67 | 62 | 20 | 20 | 19 | 16 | 16 |

These counts were audited on 23 October 2026 from local `SLAKE_split_en_realimages` CSVs and compared with the original metadata archive. They are question counts, not patient counts. The closed evaluators filter answers to Yes/No, explaining why Abdomen's scored count is 108 rather than 127.

The audit checks question-ID membership against the original split and image-ID overlap across splits. For the three selected CT subsets, the inspected train/validation/test image-ID intersections were empty. This does not establish patient-level independence or verify every dataset version hosted remotely.

## Audit your copy

```bash
python scripts/audit_dataset.py --data-root /path/to/SLAKE_split_en_realimages --original-zip /path/to/SLAKE_original_dataset_combined.zip
```

The script reads metadata only and prints aggregate checks; it does not run models, display medical images, or upload data. `--original-zip` is optional, but without it the original-metadata membership comparison is skipped. The associated [audit report](../results/dataset_audit.json) contains counts and checks, not source records.

## CoT-augmented tables

Training and test augmentation append a `CoT` column and use stage-specific folders such as `BrainFaceT_train_with_CoT`, `Neck_train_with_CoT`, `BrainFace_Test_with_CoT`, and `Abdomen_Train_with_CoT`. CSV casing varies (`open_with_CoT.csv`, `Open_with_CoT.csv`, or `open.csv` containing CoT). Use the path actually selected by the notebook; do not silently treat every `CoT` CSV as training data.

Keep validation data available for choices about prompts and hyperparameters. The current notebooks' use of validation should be verified individually; having a `val` folder does not prove a notebook uses it for model selection.
