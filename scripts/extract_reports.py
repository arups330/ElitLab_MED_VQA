"""Export selected existing text reports without running notebook code."""
from __future__ import annotations

import argparse
import subprocess
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'closed_all_models': 'notebooks/evaluation/closed/evaluate_all_models.ipynb',
    'closed_abdomen_snapshot': 'notebooks/evaluation/closed/evaluate_abdomen_snapshot.ipynb',
    'closed_brainface_snapshot': 'notebooks/evaluation/closed/evaluate_brainface_snapshot.ipynb',
    'open_all_models': 'notebooks/evaluation/open/evaluate_all_models.ipynb',
}
MARKERS = re.compile(r'FINAL REPORT|FINAL_MODEL_SUMMARY|FULL SUMMARY TABLE|WITH vs WITHOUT|ALL DATASETS.*ALL.*MODELS|FINAL.*SUMMARY|SUMMARY TABLE', re.I)


def output_text(output: dict) -> str:
    value = output.get('text', output.get('data', {}).get('text/plain', ''))
    return ''.join(value) if isinstance(value, list) else value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--working', action='store_true', help='Export current working outputs to results/latest')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'notebooks/manifest.json').read_text(encoding='utf-8'))
    originals = {r['path']:r['original_path'] for r in manifest['notebooks']}
    destination = ROOT / ('results/latest' if args.working else 'results/recorded')
    destination.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        if args.working:
            notebook = json.loads((ROOT / source).read_text(encoding='utf-8'))
            provenance = source
        else:
            original = originals[source]
            notebook = json.loads(subprocess.check_output(['git','show',manifest['upstream_commit']+':'+original],cwd=ROOT))
            provenance = manifest['upstream_commit'] + ':' + original
        reports = []
        for index, cell in enumerate(notebook['cells']):
            texts = [output_text(output) for output in cell.get('outputs', [])]
            text = ''.join(texts)
            if MARKERS.search(text):
                reports.append(f'--- Saved cell {index + 1} ---\n{text.rstrip()}\n')
        if not reports:
            raise ValueError(f'No saved summary text found in {source}; do not invent results.')
        header = (f'SAVED NOTEBOOK REPORT\nSource: {provenance}\n'
                  'Extracted from committed outputs; no new execution or metric calculation.\n'
                  'Read docs/experiments.md before interpreting these historical results.\n\n')
        (destination / f'{name}.txt').write_text(header + '\n'.join(reports), encoding='utf-8', newline='\n')
        print(f'{name}: exported {len(reports)} saved report cells')


if __name__ == '__main__':
    main()
