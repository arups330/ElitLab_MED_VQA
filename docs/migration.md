# Repository migration

GitHub snapshot: `fdfc6fc28b315f44486772d590b8e70f29bc954b`. GitHub is the source of truth; local PC notebooks were not merged over it.

All 31 notebooks were renamed and grouped by workflow. Their bytes, cell inputs, execution counts, output objects, and metadata were preserved. Git history remains available; no history rewrite or output stripping was performed.

The [manifest](../notebooks/manifest.json) records SHA-256 content and output fingerprints. The [catalog](notebooks.md) maps each original filename to its new path. Existing GitHub file links to the old default-branch paths should be updated; commit-pinned links to the upstream snapshot remain valid.

Organization adds README and workflow documentation, integrity tooling, selected saved-output report exports, contributor guidance, ignore rules, and CPU-only CI. Historical experimental code, model behavior, and metrics are unchanged.

## Local workspace comparison

`E:/Eliteclub/MED_VQA/Code` contained only a small subset of notebooks, a pre-integration backup, and a Python export. These were not used to replace the more complete GitHub snapshot. Private local data, paper folders, and result folders were not uploaded.

## Launch-link maintenance

After the initial byte-identical migration, markdown-only Colab links were repaired to use the new paths. The manifest retains `original_sha256` and adds `code_cells_sha256`; all original code cells (including execution counts and outputs) are unchanged. The reviewed `sha256` reflects the markdown link repair. Launch buttons are also available in the main README, catalog, launch directory, and notebook-folder READMEs.
