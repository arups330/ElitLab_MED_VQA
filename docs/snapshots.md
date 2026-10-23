# Original research snapshot

Working notebooks may now be updated in place. The original research evidence is retained in Git history at commit `fdfc6fc28b315f44486772d590b8e70f29bc954b`:

[Browse all 31 original notebooks and saved outputs](https://github.com/arups330/ElitLab_MED_VQA/tree/fdfc6fc28b315f44486772d590b8e70f29bc954b)

`notebooks/manifest.json` maps the original filename to the working path and stores original SHA-256 and code/output fingerprints. CI fetches the full history, reads each original Git blob, and verifies those fingerprints. It validates working notebook structure without forcing a new run to match historical results.

The later folder reorganization and markdown launch-link repairs are recorded in subsequent commits. No old run was overwritten by those changes. GitHub's file history also lets you compare future evaluations.
