"""Maintain original-platform launch links and workflow indexes; never run cells."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
COLAB = 'https://colab.research.google.com/github/arups330/ElitLab_MED_VQA/blob/main/'
RAW = 'https://raw.githubusercontent.com/arups330/ElitLab_MED_VQA/main/'

def classify(path):
    if '/base_models/' in path: return 'A', 'Base-model evaluation'
    if '/reasoning_generators/' in path: return 'A', 'Reasoning-generator training'
    if '/reasoning/' in path: return 'A', 'Reasoning generation'
    if '/training/' in path: return 'B', 'Answer-model training'
    return 'B', 'Fine-tuned model evaluation'

def launch_url(path, platform):
    if platform == 'Colab': return COLAB + quote(path, safe='/')
    return 'https://www.kaggle.com/kernels/welcome?src=' + quote(RAW + quote(path, safe='/'), safe='')

def button(path, platform):
    image = 'https://colab.research.google.com/assets/colab-badge.svg' if platform == 'Colab' else 'https://img.shields.io/badge/Kaggle-Import_notebook-20BEFF?logo=kaggle&logoColor=white'
    label = 'Open in Colab' if platform == 'Colab' else 'Import into Kaggle'
    return f'[![{label}]({image})]({launch_url(path, platform)})'

def catalog(root=ROOT):
    manifest = json.loads((root / 'notebooks/manifest.json').read_text(encoding='utf-8'))
    historical = {r['path']: r for r in manifest['notebooks']}
    rows = []
    for p in sorted((root / 'notebooks').rglob('*.ipynb')):
        path = p.relative_to(root).as_posix()
        nb = json.loads(p.read_text(encoding='utf-8'))
        record = historical.get(path, {})
        platform = record.get('platform')
        if platform is None:
            md = nb.get('metadata', {})
            if ('colab' in md) == ('kaggle' in md):
                raise ValueError(f'Unknown or ambiguous original platform for new notebook: {path}')
            platform = 'Colab' if 'colab' in md else 'Kaggle'
        pipeline, stage = classify(path)
        question = 'open' if '/open/' in path or '_open' in p.stem else 'closed' if '/closed/' in path or '_closed' in p.stem else 'mixed or reused'
        rows.append(dict(path=path, platform=platform, pipeline=pipeline, stage=stage, question_type=question,
                         original_path=record.get('original_path', ''), launch=launch_url(path, platform)))
    return rows

def generated_files(root=ROOT):
    rows = catalog(root)
    intro = ('Pipeline A conditions base models on a test CoT column. Pipeline B compares fine-tuned answer checkpoints without a test CoT column. '
             'Each button follows the original platform. Kaggle links import the matching GitHub copy; original published Kaggle URLs were not present in the exports. '
             'Configure data, secrets, and GPU before running. Working notebooks can be updated; original evidence stays in the pinned Git snapshot.')
    files = {}
    lines = ['# Notebook catalog', '', intro, '', 'See [workflows](workflows.md), [updating notebooks](updating_notebooks.md), and [snapshot preservation](snapshots.md).', '',
             '| Notebook | Pipeline and stage | Question type | Platform | Launch | Original filename |', '|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| [{r['path'].removeprefix('notebooks/')}](../{r['path']}) | {r['pipeline']}: {r['stage']} | {r['question_type']} | {r['platform']} | {button(r['path'],r['platform'])} | `{r['original_path']}` |")
    files['docs/notebooks.md'] = '\n'.join(lines) + '\n'
    lines = ['# Open notebooks on their original platform', '', intro, '', 'The buttons do not run cells. See [reproduction](reproduction.md) and [the workflow trace](workflows.md).', '']
    for platform in ['Colab', 'Kaggle']:
        lines += ['## ' + platform, '', '| Pipeline | Notebook | Launch |', '|---|---|---|']
        for r in rows:
            if r['platform'] == platform:
                lines.append(f"| {r['pipeline']}: {r['stage']} | [{r['path'].removeprefix('notebooks/')}](../{r['path']}) | {button(r['path'],platform)} |")
        lines.append('')
    files['docs/launch.md'] = '\n'.join(lines).rstrip() + '\n'
    for folder in sorted({str(Path(r['path']).parent).replace('\\','/') for r in rows}):
        subset = [r for r in rows if str(Path(r['path']).parent).replace('\\','/') == folder]
        title = folder.removeprefix('notebooks/').replace('/', ' / ').replace('_', ' ').title()
        lines = ['# ' + title, '', f"Pipeline {subset[0]['pipeline']} — {subset[0]['stage']}.", '',
                 'Open the notebook on its original platform. Kaggle buttons import a GitHub copy. Configure data and credentials before running; preserve saved outputs when exporting.', '',
                 '| Notebook | Question type | Platform | Launch |', '|---|---|---|---|']
        for r in subset:
            lines.append(f"| [{Path(r['path']).stem}]({Path(r['path']).name}) | {r['question_type']} | {r['platform']} | {button(r['path'],r['platform'])} |")
        files[folder + '/README.md'] = '\n'.join(lines) + '\n'
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for name, text in generated_files().items():
        p = ROOT / name
        if args.check:
            if not p.exists() or p.read_text(encoding='utf-8') != text: stale.append(name)
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding='utf-8', newline='\n')
    if stale: raise SystemExit('Catalog update needed: run python scripts/update_catalog.py\n' + '\n'.join(stale))
    print('Catalog and original-platform links checked.' if args.check else 'Updated catalog, launch directory, and notebook-folder indexes.')

if __name__ == '__main__': main()
