"""Check historical notebook preservation, notebook structure, links, and credentials.

Standard-library only. Does not execute any notebook cell or load model weights.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path = ROOT) -> tuple[list[str], int]:
    errors = []
    manifest = json.loads((root / 'notebooks/manifest.json').read_text(encoding='utf-8'))
    records = manifest['notebooks']
    if len(records) != 31 or len({r['path'] for r in records}) != len(records):
        errors.append('Migration manifest must contain 31 distinct historical notebooks.')
    for record in records:
        path = root / record['path']
        if not path.is_file():
            errors.append(f'Missing historical notebook: {record["path"]}')
            continue
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            errors.append(f'Historical notebook changed: {record["path"]}; save a new run separately.')
        try:
            notebook = json.loads(raw)
            outputs = [c.get('outputs', []) for c in notebook['cells']]
            digest = hashlib.sha256(json.dumps(outputs, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
            if digest != record['outputs_sha256'] or sum(map(len, outputs)) != record['output_count']:
                errors.append(f'Saved outputs changed: {record["path"]}')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'Invalid notebook data: {record["path"]}: {exc}')

    notebooks = list((root / 'notebooks').rglob('*.ipynb'))
    for path in notebooks:
        relative = path.relative_to(root)
        try:
            nb = json.loads(path.read_text(encoding='utf-8'))
            if nb.get('nbformat') != 4 or not isinstance(nb.get('cells'), list):
                raise ValueError('expected notebook format 4 with a cell list')
            for i, cell in enumerate(nb['cells']):
                if cell.get('cell_type') not in {'code', 'markdown', 'raw'}:
                    raise ValueError(f'cell {i} has an unknown type')
                if not isinstance(cell.get('source'), (list, str)):
                    raise ValueError(f'cell {i} has no text source')
                if cell['cell_type'] == 'code':
                    if not isinstance(cell.get('outputs'), list):
                        raise ValueError(f'code cell {i} has no outputs list')
                    for output in cell['outputs']:
                        if output.get('output_type') not in {'stream', 'display_data', 'execute_result', 'error'}:
                            raise ValueError(f'cell {i} has an unknown output type')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'{relative}: {exc}')

    for path in root.rglob('*.md'):
        if '.git' in path.parts:
            continue
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)\s]+)\)', text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f'{path.relative_to(root)}: broken local link {target}')

    patterns = [r'hf_[A-Za-z0-9]{20,}', r'gh[pousr]_[A-Za-z0-9]{20,}',
                r'github_pat_[A-Za-z0-9_]{30,}', r'sk-[A-Za-z0-9]{20,}',
                r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    for path in root.rglob('*'):
        if not path.is_file() or '.git' in path.parts or path.suffix not in {'.ipynb', '.py', '.md', '.txt', '.json', '.yml'}:
            continue
        text = path.read_text(encoding='utf-8')
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f'Potential credential in {path.relative_to(root)} (value withheld).')
    return errors, len(notebooks)


def main() -> int:
    errors, count = check()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {count} notebooks; 31 historical files and all 3390 saved output objects preserved.')
    print('PASS: notebook structure, local documentation links, and common credential-pattern checks.')
    print('No model training, inference, or scientific result verification was performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
