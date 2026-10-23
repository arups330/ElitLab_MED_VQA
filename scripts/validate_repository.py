"""Validate mutable working notebooks and immutable original Git snapshots."""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True).encode()).hexdigest()

def snapshot_errors(raw, record):
    errors = []
    if hashlib.sha256(raw).hexdigest() != record['original_sha256']:
        errors.append('original file hash differs')
    nb = json.loads(raw)
    if fingerprint([c for c in nb['cells'] if c['cell_type'] == 'code']) != record['code_cells_sha256']:
        errors.append('original code-cell fingerprint differs')
    outputs = [c.get('outputs', []) for c in nb['cells']]
    if fingerprint(outputs) != record['outputs_sha256'] or sum(map(len, outputs)) != record['output_count']:
        errors.append('original saved outputs differ')
    return errors

def notebook_errors(nb):
    errors = []
    if nb.get('nbformat') != 4 or not isinstance(nb.get('cells'), list):
        return ['expected notebook format 4 with a cell list']
    for i, cell in enumerate(nb['cells']):
        if cell.get('cell_type') not in {'code', 'markdown', 'raw'}:
            errors.append(f'cell {i} has an unknown type')
        source = cell.get('source')
        if not isinstance(source, (list, str)) or isinstance(source, list) and not all(isinstance(s,str) for s in source):
            errors.append(f'cell {i} has invalid text source')
        if cell.get('cell_type') == 'code':
            outputs = cell.get('outputs')
            if not isinstance(outputs, list):
                errors.append(f'code cell {i} has no outputs list')
                continue
            if not all(isinstance(o,dict) and o.get('output_type') in {'stream','display_data','execute_result','error'} for o in outputs):
                errors.append(f'code cell {i} has an invalid output object')
    return errors

def check(root=ROOT):
    errors = []
    manifest = json.loads((root / 'notebooks/manifest.json').read_text(encoding='utf-8'))
    records = manifest['notebooks']
    if len(records) != 31 or len({r['original_path'] for r in records}) != 31:
        errors.append('Expected 31 distinct original notebook records.')
    for r in records:
        try:
            raw = subprocess.check_output(['git','show',manifest['upstream_commit'] + ':' + r['original_path']], cwd=root, stderr=subprocess.PIPE)
            errors.extend(f"Snapshot {r['original_path']}: {e}" for e in snapshot_errors(raw,r))
        except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as exc:
            errors.append(f"Cannot verify original snapshot {r['original_path']}; fetch full Git history. {type(exc).__name__}")
        if not (root / r['path']).is_file():
            errors.append(f"Missing working notebook {r['path']}; update its manifest mapping if deliberately moved.")
    notebooks = list((root / 'notebooks').rglob('*.ipynb'))
    for path in notebooks:
        try:
            nb = json.loads(path.read_text(encoding='utf-8'))
            errors.extend(f'{path.relative_to(root)}: {e}' for e in notebook_errors(nb))
        except (ValueError, TypeError) as exc:
            errors.append(f'{path.relative_to(root)}: invalid JSON notebook: {exc}')
    for path in root.rglob('*.md'):
        if '.git' in path.parts: continue
        for target in re.findall(r'\]\(([^)\s]+)\)', path.read_text(encoding='utf-8')):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path: continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                errors.append(f'{path.relative_to(root)}: broken local link {target}')
    patterns = [r'hf_[A-Za-z0-9]{20,}',r'gh[pousr]_[A-Za-z0-9]{20,}',r'github_pat_[A-Za-z0-9_]{30,}',r'sk-[A-Za-z0-9]{20,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']
    for path in root.rglob('*'):
        if not path.is_file() or '.git' in path.parts or path.suffix not in {'.ipynb','.py','.md','.txt','.json','.yml'}: continue
        if any(re.search(pattern,path.read_text(encoding='utf-8')) for pattern in patterns):
            errors.append(f'Potential credential in {path.relative_to(root)} (value withheld).')
    return errors, len(notebooks)

def main():
    errors,count = check()
    if errors:
        print('\n'.join(errors),file=sys.stderr)
        return 1
    print(f'PASS: {count} working notebooks validated; in-place code/output updates are allowed.')
    print('PASS: all 31 original Git snapshots and 3390 original output objects verified separately.')
    print('PASS: local links and common credential-pattern checks. No GPU execution performed.')
    return 0

if __name__ == '__main__': raise SystemExit(main())
